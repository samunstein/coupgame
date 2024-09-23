import random
from collections.abc import Callable

from common.common import debug_print
from config import EACH_CARD_IN_DECK, WRONG_MESSAGE_TOLERANCE
from connection.common import Connection
from game.messages.commands import *
from game.messages.responses import *


class TurnEndPanic(Exception):
    def __init__(self):
        super().__init__()

class Player:
    def __init__(self, number: int, connection: Connection):
        self.cards: list[Card] = []
        self.money: int = 0
        self._connection: Connection = connection
        self.name: str = ""
        self.number: int = number

    def __eq__(self, other: 'Player'):
        return self.number == other.number

    def send(self, msg: Command):
        self._connection.send(msg)

    def send_and_receive(self, msg: Command, response_type: type[Response]) -> Response:
        res = self._connection.send_and_receive(msg)
        return response_type.deserialize(res)

    def __str__(self):
        return f"{self.number}:{self.name}"

    def shutdown(self):
        self.send(Shutdown())
        self._connection.close()

    def give_card(self, c: Card):
        self.cards.append(c)
        self.send(AddCard(c))

    def remove_card(self, c: Card):
        self.cards.remove(c)
        self.send(RemoveCard(c))

    def give_money(self, m: int):
        self.money += m
        self.send(ChangeMoney(m))

    def debug_message(self, msg: str):
        self._connection.send(DebugMessage(msg))


class Game:
    def __init__(self, connections: list[Connection], deck: list[Card] | None = None, crash_on_violation: bool = False):
        self.players: dict[int, Player] = {i: Player(i, c) for i, c in enumerate(connections)}
        self.alive_players: dict[int, Player] = {p: self.players[p] for p in self.players}
        for p in self.players.values():
            p.send(SetPlayerNumber(p.number))
            name = self._extort_a_response(p, AskName(), NameResponse)
            if name is not None:
                p.name = name.player_name
        debug_print(f"Players {[p.name for p in self.players.values()]} joined.")
        self.alive_players: dict[int, Player] = {p: self.players[p] for p in self.players}
        self.deck = []
        if deck is None:
            for c in Card.all():
                self.deck.extend(EACH_CARD_IN_DECK * [c])
        else:
            self.deck = deck
        self.crash_on_violation = crash_on_violation

    def _mark_player_dead(self, player: Player):
        for p in self.players.values():
            p.send(PlayerIsDead(player.number))
        self.alive_players.pop(player.number)

    def _emergency_kill(self, player: 'Player'):
        debug_print(f"Player {player.number} died because of rule violations")
        if self.crash_on_violation:
            raise Exception("Crashing on rule violation")
        for c in player.cards.copy():
            player.remove_card(c)
            for p in self.players.values():
                p.send(PlayerLostACard(player.number, c))
        self._mark_player_dead(player)


    def _extort_a_response[R](self, player: Player, command: Command, response_type: type[R], extra_condition: Callable[[R], bool] | None = None) -> R | None:
        try:
            for _ in range(WRONG_MESSAGE_TOLERANCE):
                result = player.send_and_receive(command, response_type)
                if result is None:
                    continue
                if extra_condition is not None and not extra_condition(result):
                    continue
                return result
        except TimeoutError:
            debug_print(f"Player {player.number} took too long and timed out")
        self._emergency_kill(player)
        return None

    def _setup_player(self, player: Player):
        random.shuffle(self.deck)
        player.give_card(self.deck.pop())
        player.give_card(self.deck.pop())
        player.give_money(2)
        for other in self.players.values():
            if player.number != other.number:
                player.send(AddOpponent(other.number, other.name))

    def setup_players(self):
        for p in self.players.values():
            self._setup_player(p)

    def _get_other_players_than(self, num: int) -> dict[int, Player]:
        return {n: p for (n, p) in self.alive_players.items() if p.number != num}

    def _choose_and_kill_a_card(self, player: Player, failure_means_panic: bool):
        def check_has_card(r: CardResponse):
            if r.card not in player.cards:
                player.debug_message("You don't have that card")
                return False
            return True

        card_response = self._extort_a_response(player, ChooseCardToKill(), CardResponse, check_has_card)

        if card_response is None:
            if failure_means_panic:
                raise TurnEndPanic()
        else:
            player.remove_card(card_response.card)

            for p in self.players.values():
                p.send(PlayerLostACard(player.number, card_response.card))

            if not player.cards:
                self._mark_player_dead(player)


    def _handle_challenges(self, player: Player, action: ActionDecision):
        if not action.action().requires_card:
            # Cannot be challenged
            return

        # There is always only one (if any) card that allows each action
        required_card = action.action().requires_card[0]

        other_players = self._get_other_players_than(player.number)
        other_numbers = list(other_players)
        # Random order of challenging, to lessen the effect of player order
        random.shuffle(other_numbers)
        target_num = -1
        if isinstance(action, TargetedActionDecision):
            target_num = action.target()
            # Put target first
            other_numbers = [action.target()] + [n for n in other_numbers if n != action.target()]

        for other_num in other_numbers:
            challenger = other_players[other_num]

            challenge = self._extort_a_response(challenger, DoYouChallengeAction(action.action(), player.number, target_num), DoYouChallengeDecision)

            # If target somehow died while answering, return but don't panic
            if action.action().targeted and target_num not in self.alive_players:
                return

            if isinstance(challenge, Challenge):
                debug_print(f"It is challenged by {challenger.number}")

                def check_challenged_decision(decision: YouAreChallengedDecision):
                    if isinstance(decision, RevealCard) and required_card not in player.cards:
                        player.debug_message("You don't have the card to reveal. Concede.")
                        return False
                    return True

                challenge_response = self._extort_a_response(player, YourActionIsChallenged(action.action(), target_num, challenger.number), YouAreChallengedDecision,
                                                  check_challenged_decision)

                # Action taker could not decide how to answer to the challenge
                if challenge_response is None:
                    raise TurnEndPanic()

                if isinstance(challenge_response, RevealCard):
                    challenge_success = False
                    life_loser = challenger
                    player.remove_card(required_card)
                    self.deck.append(required_card)
                    random.shuffle(self.deck)
                    player.give_card(self.deck.pop())
                    debug_print("Challenge unsuccessful")

                else:
                    challenge_success = True
                    life_loser = player
                    debug_print("Challenge successful")

                self._choose_and_kill_a_card(life_loser, life_loser == player or life_loser.number == target_num)

                self._log_challenge_result(player, action.action(), target_num, challenger.number, challenge_success)

                if challenge_success:
                    # Action cannot continue if it was successfully challenged
                    raise TurnEndPanic()
                return

    def _log_challenge_result(self, player: Player, action: Action, target_num: int, challenger_num: int, successful: bool):
        debug_print(
            f"{action} challenged by {challenger_num} with success {successful}. Taken by {player.number} on {target_num}")
        for p in self.players.values():
            p.send(ActionWasChallenged(action, player.number, target_num, challenger_num, successful))

    def _handle_blocks(self, player: Player, action: ActionDecision):
        if not action.action().blocked_by:
            # Cannot be blocked
            return

        other_players = self._get_other_players_than(player.number)
        other_numbers = list(other_players)
        # Random order of challenging, to lessen the effect of player order
        random.shuffle(other_numbers)
        target_num = -1
        if isinstance(action, TargetedActionDecision):
            # If targeted, only ask block from the targeted player
            target_num = action.target()
            other_numbers = [action.target()]

        for other_num in other_numbers:
            blocker_player = other_players[other_num]
            block_decision = self._extort_a_response(blocker_player, DoYouBlock(action.action(), player.number), DoYouBlockDecision)

            if isinstance(block_decision, Block):
                debug_print(f"It is blocked by {other_num}")
                self._handle_block_challenges(player, action.action(), target_num, block_decision.card, blocker_player.number)
                return

    def _handle_block_challenges(self, player: Player, action: Action, target_num: int, block_card: Card, blocker_number: int):
        possible_challengers = self._get_other_players_than(blocker_number)

        for other_num in possible_challengers:
            challenger = self.alive_players[other_num]

            challenge_decision = self._extort_a_response(challenger, DoYouChallengeBlock(action, player.number, target_num, block_card, blocker_number), DoYouChallengeDecision)

            # Only the action doer may affect the action here, as either there is no target, or the target is not
            # a possible challenger anyway
            if player.number not in self.alive_players:
                raise TurnEndPanic()

            if isinstance(challenge_decision, Challenge):
                debug_print(f"The block is challenged by {other_num}")
                blocker_player = self.alive_players[blocker_number]

                def check_challenged_decision(decision: YouAreChallengedDecision):
                    if isinstance(decision, RevealCard) and block_card not in blocker_player.cards:
                        blocker_player.debug_message("You don't have the card to reveal. Concede.")
                        return False
                    return True

                challenge_response = self._extort_a_response(blocker_player, YourBlockIsChallenged(action, player.number, block_card, challenger.number), YouAreChallengedDecision,
                                                  check_challenged_decision)

                # Blocker player could not decide what to do with the challenge. Action may continue as the block is invalid
                if challenge_response is None:
                    return

                if isinstance(challenge_response, RevealCard):
                    challenge_success = False
                    life_loser = challenger
                    blocker_player.remove_card(block_card)
                    self.deck.append(block_card)
                    random.shuffle(self.deck)
                    blocker_player.give_card(self.deck.pop())
                    debug_print("Block challenge unsuccessful")

                else:
                    challenge_success = True
                    life_loser = blocker_player
                    debug_print("Block challenge successful")

                self._choose_and_kill_a_card(life_loser, life_loser == player)

                self._log_block_challenge_result(player, action, target_num, block_card, blocker_number, challenger.number, challenge_success)

                if challenge_success:
                    # Action may continue
                    return
                else:
                    # Block was challenged, but unsuccessfully -> action may not continue
                    self._log_block_result(player, action, target_num, block_card, blocker_number)
                    raise TurnEndPanic()

        # Block was not challenged by anyone -> action is blocked and may not continue
        self._log_block_result(player, action, target_num, block_card, blocker_number)
        raise TurnEndPanic()

    def _log_block_result(self, player: Player, action: Action, target_num: int, blocked_with: Card, blocked_by: int):
        debug_print(f"{action} blocked with {blocked_with} by {blocked_by}. Taken by {player.number} on {target_num}")
        for p in self.players.values():
            p.send(ActionWasBlocked(action, player.number, target_num, blocked_with, blocked_by))

    def _log_block_challenge_result(self, player: Player, action: Action, target_num: int, blocked_with: Card, blocker_num: int,
                                    challenger_num: int, successful: bool):
        debug_print(
            f"Blocking with {blocked_with} by {blocker_num} the {action} taken by {player.number} on {target_num} challenged by {challenger_num} with success {successful}")
        for p in self.players.values():
            p.send(
                BlockWasChallenged(action, player.number, target_num, blocked_with, blocker_num, challenger_num,
                                   successful))

    def _handle_steal(self, player: Player, target_num: int):
        target_player = self.players[target_num]
        money_stolen = min(target_player.money, 2)
        player.give_money(money_stolen)
        target_player.give_money(-money_stolen)
        self._log_successful_action_result(player, Steal(), target_player.number)

    def _handle_assassinate(self, player: Player, target_num: int):
        target_player = self.alive_players[target_num]
        self._choose_and_kill_a_card(target_player, False)
        self._log_successful_action_result(player, Assassinate(), target_player.number)

    def _handle_foreign_aid(self, player: Player):
        player.give_money(2)
        self._log_successful_action_result(player, ForeignAid(), -1)

    def _handle_income(self, player: Player):
        player.give_money(1)
        self._log_successful_action_result(player, Income(), -1)

    def _handle_tax(self, player: Player):
        player.give_money(3)
        self._log_successful_action_result(player, Tax(), -1)

    def _handle_coup(self, player: Player, target_num: int):
        target_player = self.alive_players[target_num]
        self._choose_and_kill_a_card(target_player, False)
        self._log_successful_action_result(player, Coup(), target_player.number)

    def _handle_ambassadate(self, player: Player):
        random.shuffle(self.deck)
        player.give_card(self.deck.pop())
        player.give_card(self.deck.pop())

        def check_response(r: AmbassadorCardResponse):
            if r.card1 == r.card2 and player.cards.count(r.card1) < 2:
                player.debug_message("You don't have 2 of that card")
                return False
            if r.card1 != r.card2 and (
                    r.card1 not in player.cards or r.card2 not in player.cards):
                player.debug_message("You don't have both those cards")
                return False
            return True

        decision = self._extort_a_response(player, ChooseAmbassadorCardsToRemove(), AmbassadorCardResponse, check_response)

        if decision is None:
            raise TurnEndPanic()

        player.remove_card(decision.card1)
        player.remove_card(decision.card2)
        self.deck.append(decision.card1)
        self.deck.append(decision.card2)
        self._log_successful_action_result(player, Ambassadate(), -1)

    def _log_successful_action_result(self, player: Player, action: Action, target_num: int):
        debug_print(f"{action} taken by {player.number} on {target_num} successful")
        for p in self.players.values():
            p.send(ActionWasTaken(action, player.number, target_num))

    def _take_action(self, player: Player):
        debug_print(f"Player {player.number} taking turn")
        other_players = self._get_other_players_than(player.number)

        def check_action_legality(action_decision: ActionDecision):
            if isinstance(action_decision, TargetedActionDecision) and action_decision.target() not in other_players:

                player.debug_message(f"Target {action_decision.target()} does not exist in {other_players.keys()}")
                return False
            if player.money < action_decision.action().cost:
                player.debug_message("Not enough money")
                return False
            if player.money >= 10 and action_decision.action() != Coup():
                player.debug_message("Must coup")
                return False
            return True

        action = self._extort_a_response(player, TakeTurn(), ActionDecision, check_action_legality)
        if action is None:
            raise TurnEndPanic()

        debug_print(f"Player {player.number} attempting {action}")

        self._handle_challenges(player, action)

        # At this point the cost should be paid
        player.give_money(-action.action().cost)

        # Target might be dead here. Try block only if possible target is alive
        if isinstance(action, TargetedActionDecision) and action.target() in self.alive_players or isinstance(action, NonTargetedActionDecision):
            self._handle_blocks(player, action)

        # Target might be dead here too. Steal may be performed on a dead target, but otherwise panic out
        if isinstance(action, TargetedActionDecision) and action.target() not in self.alive_players and not isinstance(action, StealDecision):
            raise TurnEndPanic()

        if isinstance(action, StealDecision):
            self._handle_steal(player, action.target())
        elif isinstance(action, AssassinateDecision):
            self._handle_assassinate(player, action.target())
        elif isinstance(action, ForeignAidDecision):
            self._handle_foreign_aid(player)
        elif isinstance(action, IncomeDecision):
            self._handle_income(player)
        elif isinstance(action, TaxDecision):
            self._handle_tax(player)
        elif isinstance(action, CoupDecision):
            self._handle_coup(player, action.target())
        elif isinstance(action, AmbassadateDecision):
            self._handle_ambassadate(player)

    # Returns whether the game has ended
    def run_one_turn(self) -> bool:
        # Remove the first player in the dict and insert it back, in effect
        # rotating the dict and turn order
        taking_action_num = list(self.alive_players)[0]
        taking_action = self.alive_players.pop(taking_action_num)
        self.alive_players[taking_action_num] = taking_action

        try:
            self._take_action(taking_action)
        except TurnEndPanic:
            pass

        newly_dead = [p for p in self.alive_players.values() if not len(p.cards)]
        for d in newly_dead:
            debug_print(f"Player {d.number} is dead")
            self._mark_player_dead(d)

        if len(self.alive_players) == 1:
            debug_print(f"Winner is {list(self.alive_players)[0]}!")
            for p in self.players.values():
                p.shutdown()
            return True
        return False

    def run(self):
        self.setup_players()
        while True:
            if self.run_one_turn():
                break
