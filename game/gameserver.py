import random

from common.common import debug_print
from config import PARAM_SPLITTER, CONTROL_CHAR_REPLACE, EACH_CARD_IN_DECK, WRONG_MESSAGE_TOLERANCE
from connection.common import Connection
from game.enums.actions import *
from game.enums.cards import *
from game.messages.commands import *
from game.messages.responses import Challenge, Allow, NameResponse, YouAreChallengedDecision, Concede, RevealCard, \
    CardResponse, DoYouBlockDecision, Block, NoBlock, DoYouChallengeDecision, AmbassadorCardResponse, ActionDecision, \
    TargetedActionDecision, NonTargetedActionDecision


class Player:
    def __init__(self, number: int, connection: Connection):
        self.cards: list[Card] = []
        self.money: int = 0
        self.connection: Connection = connection
        self.name: str = ""
        self.number: int = number
        self.all_players: list['Player'] = []

    def __str__(self):
        return f"{self.name}"

    def _handle_dead_players_in_the_middle_of_actions(self, other_players):
        for key in list(other_players.keys()):
            if not len(other_players[key].cards):
                other_players.pop(key)

    def _extort_a_correct_command_with_threat_of_violence(self, function_block, one_responsible):
        retval = None
        try:
            for _ in range(WRONG_MESSAGE_TOLERANCE):
                success, result = function_block()
                if success:
                    retval = result
                    break
            else:
                self.emergency_kill(one_responsible)
        except TimeoutError:
            debug_print(f"Player {one_responsible} took too long and timed out")
            self.emergency_kill(one_responsible)
        return retval

    def set_all_players(self, all_p: list['Player']):
        self.all_players = all_p

    def shutdown(self):
        self.connection.send(Shutdown())
        self.connection.close()

    def give_card(self, c: Card):
        self.cards.append(c)
        self.connection.send(AddCard(c))

    def remove_card(self, c: Card):
        self.cards.remove(c)
        self.connection.send(RemoveCard(c))

    def give_money(self, m: int):
        self.money += m
        self.connection.send(ChangeMoney(m))

    def find_name(self):
        def closure_block():
            resp = NameResponse.deserialize(self.connection.send_and_receive(AskName()))
            if resp is None:
                return False, None
            else:
                return True, resp.player_name
        name = self._extort_a_correct_command_with_threat_of_violence(closure_block, self)
        self.name = name
        debug_print(f"{self.name} created")

    def debug_message(self, msg: str):
        self.connection.send(DebugMessage(msg))

    def add_opponent(self, num: int, name: str):
        self.connection.send(AddOpponent(num, name))

    def player_number(self, num: int):
        self.connection.send(SetPlayerNumber(num))

    def _check_action_leglity(self, action: Action, target_number: int, other_players: dict[int, 'Player']):
        if action.targeted and target_number not in other_players:
            self.debug_message("Target does not exist")
            return False
        if self.money < action.cost:
            self.debug_message("Not enough money")
            return False
        if self.money >= 10 and action != Coup:
            self.debug_message("Must coup")
            return False
        return True

    def _log_successful_action_result(self, action: Action, target_num: int):
        debug_print(f"{action} taken by {self.number} on {target_num} successful")
        for p in self.all_players:
            p.connection.send(ActionWasTaken(action, self.number, target_num))

    def _log_block_result(self, action: Action, target_num: int, blocked_with: Card, blocked_by: int):
        debug_print(f"{action} blocked with {blocked_with} by {blocked_by}. Taken by {self.number} on {target_num}")
        for p in self.all_players:
            p.connection.send(ActionWasBlocked(action, self.number, target_num, blocked_with, blocked_by))

    def _log_challenge_result(self, action: Action, target_num: int, challenger_num: int, successful: bool):
        debug_print(
            f"{action} challenged by {challenger_num} with success {successful}. Taken by {self.number} on {target_num}")
        for p in self.all_players:
            p.connection.send(ActionWasChallenged(action, self.number, target_num, challenger_num, successful))

    def _log_block_challenge_result(self, action: Action, target_num: int, blocked_with: Card, blocker_num: int, challenger_num: int, successful: bool):
        debug_print(
            f"Blocking with {blocked_with} by {blocker_num} the {action} taken by {self.number} on {target_num} challenged by {challenger_num} with success {successful}")
        for p in self.all_players:
            p.connection.send(BlockWasChallenged(action, self.number, target_num, blocked_with, blocker_num, challenger_num,
                              successful))

    def _handle_challenges(self, action: Action, target_number: int, other_players: dict[int, 'Player'], deck: list[Card]):
        # Returns whether the action can continue (False if successfully challenged)
        if not len(action.requires_card):
            return True

        other_numbers_order = list(other_players.keys())
        if action.targeted:
            other_numbers_order.remove(target_number)
            other_numbers_order.insert(0, target_number)

        for other_num in other_numbers_order:
            maybe_challenger = other_players[other_num]

            def closure_block() -> (bool, any):
                raw = maybe_challenger.connection.send_and_receive(DoYouChallengeAction(action, self.number,
                                                                 target_number))
                decision = DoYouChallengeDecision.deserialize(raw)

                if isinstance(decision, Challenge):
                    return True, True
                elif isinstance(decision, Allow):
                    return True, False
                else:
                    maybe_challenger.debug_message("Challenge or allow the action please")
                    return False, None


            challenge = self._extort_a_correct_command_with_threat_of_violence(closure_block, maybe_challenger)
            # Since we're kind of in the middle of logic, handle player dying here
            self._handle_dead_players_in_the_middle_of_actions(other_players)

            # Target died of idiocy. Action cannot continue
            if action.targeted and target_number not in other_players:
                return False

            if challenge is False:
                continue

            if challenge is True:
                def closure_block():
                    what_do = YouAreChallengedDecision.deserialize(self.connection.send_and_receive(YourActionIsChallenged(action, target_number,
                                                         maybe_challenger.number)))
                    if isinstance(what_do, Concede):
                        return True, what_do
                    elif isinstance(what_do, RevealCard):
                        required_card = action.requires_card[0]
                        if required_card in self.cards:
                            return True, what_do
                        else:
                            self.debug_message("You don't have the card to reveal. Concede.")
                            return False, None
                    else:
                        self.debug_message("Choose to concede or reveal please")
                        return False, None

                what_did = self._extort_a_correct_command_with_threat_of_violence(closure_block, self)

                # Action taker could not decide how to answer to the challenge
                if what_did is None:
                    return False

                if isinstance(what_did, RevealCard):
                    challenge_success = False
                    life_loser = maybe_challenger

                    card = action.requires_card[0]
                    self.remove_card(card)
                    deck.append(card)
                    random.shuffle(deck)
                    self.give_card(deck.pop())

                else:
                    challenge_success = True
                    life_loser = self

                def dead_chooser_closure():
                    killed = CardResponse.deserialize(life_loser.connection.send_and_receive(ChooseCardToKill()))
                    if killed.card not in life_loser.cards:
                        life_loser.debug_message("You don't have that card")
                        return False, None
                    life_loser.remove_card(killed.card)
                    for p in self.all_players:
                        p.connection.send(PlayerLostACard(life_loser.number, killed.card))
                    self._log_challenge_result(action, target_number, maybe_challenger.number, challenge_success)
                    return True, None

                self._extort_a_correct_command_with_threat_of_violence(dead_chooser_closure, life_loser)

                # Challenge not successful => action may continue
                return not challenge_success

        # No challenges, return
        return True

    def _handle_blocks(self, action: Action, target_number: int, other_players: dict[int, 'Player'], deck: list[Card]):
        # Returns whether the actions can continue (False if successfully blocked)
        if not len(action.blocked_by):
            return True

        if action.targeted:
            to_ask_numbers = [target_number]
        else:
            to_ask_numbers = list(other_players.keys())

        for other_num in to_ask_numbers:
            maybe_blocker = other_players[other_num]

            def closure_block() -> (bool, object):
                decision = DoYouBlockDecision.deserialize(maybe_blocker.connection.send_and_receive(DoYouBlock(action, self.number)))

                if decision is None:
                    maybe_blocker.debug_message("Challenge or allow the action please")
                    return False, None

                return True, decision

            block_decision = self._extort_a_correct_command_with_threat_of_violence(closure_block, maybe_blocker)

            self._handle_dead_players_in_the_middle_of_actions(other_players)

            # Target died of idiocy. Action cannot continue
            if action.targeted and target_number not in other_players:
                return False

            if isinstance(block_decision, NoBlock):
                continue

            if isinstance(block_decision, Block):
                return self._handle_block_challenges(action, target_number, block_decision.card, other_num, other_players, deck)

        return True

    def _handle_block_challenges(self, action: Action, target_num: int, block_card: Card, blocker_number: int, other_players: dict[int, 'Player'], deck: list[Card]):
        # Returns if the action can continue (basically True only if the block was found to be faulty)
        possible_challengers = [self.number] + [num for num in other_players if num != blocker_number]

        for other_num in possible_challengers:
            maybe_challenger = other_players[other_num] if other_num != self.number else self

            def closure_block() -> (bool, any):
                decision = DoYouChallengeDecision.deserialize(maybe_challenger.connection.send_and_receive(DoYouChallengeBlock(action, self.number,
                                                                 target_num, block_card, blocker_number)))
                if decision is None:
                    maybe_challenger.debug_message("Challenge or allow the block please")
                    return False, None

                return True, decision


            challenge = self._extort_a_correct_command_with_threat_of_violence(closure_block, maybe_challenger)

            self._handle_dead_players_in_the_middle_of_actions(other_players)

            if (action.targeted and target_num not in other_players) or not len(self.cards):
                # Action may not continue if one of the participants died of idiocy
                return False

            if isinstance(challenge, Allow):
                continue

            if isinstance(challenge, Challenge):
                blocker_player = other_players[blocker_number]

                def closure_block():
                    what_do = YouAreChallengedDecision.deserialize(blocker_player.connection.send_and_receive(YourBlockIsChallenged(action, self.number,
                                                                   block_card, maybe_challenger.number)))
                    if isinstance(what_do, Concede):
                        return True, what_do
                    elif isinstance(what_do, RevealCard):
                        if block_card in blocker_player.cards:
                            return True, what_do
                        else:
                            blocker_player.debug_message("You don't have that block card to reveal. Concede.")
                            return False, None
                    else:
                        blocker_player.debug_message("Choose to concede or reveal please")

                        return False, None
                what_did = self._extort_a_correct_command_with_threat_of_violence(closure_block, blocker_player)

                # Blocker player could not decide what to do with the challenge. Action may continue as the block is invalid
                if what_did is None:
                    return True

                if isinstance(what_did, RevealCard):
                    challenge_success = False
                    life_loser = maybe_challenger

                    blocker_player.remove_card(block_card)
                    deck.append(block_card)
                    random.shuffle(deck)
                    blocker_player.give_card(deck.pop())

                else:
                    challenge_success = True
                    life_loser = blocker_player

                def dead_chooser_closure():
                    killed = CardResponse.deserialize(life_loser.connection.send_and_receive(ChooseCardToKill()))
                    if killed.card not in life_loser.cards:
                        life_loser.debug_message("You don't have that card to kill")
                        return False, None
                    life_loser.remove_card(killed.card)
                    for p in self.all_players:
                        p.connection.send(PlayerLostACard(life_loser.number, killed.card))
                    self._log_block_challenge_result(action, target_num, block_card, blocker_number, maybe_challenger.number, challenge_success)
                    return True, None

                self._extort_a_correct_command_with_threat_of_violence(dead_chooser_closure, life_loser)

                # An action participant died of idiocy.
                if not len(self.cards) or (action.targeted and target_num not in other_players):
                    return False

                # Challenge successful => no block => action may continue
                return challenge_success

        # No challenges, action may not continue because it is blocked
        return False

    def _handle_steal(self, target_num: int, other_players: dict[int, 'Player']):
        target_player = other_players[target_num]
        money_stolen = min(target_player.money, 2)
        self.give_money(money_stolen)
        target_player.give_money(-money_stolen)
        self._log_successful_action_result(Steal(), target_player.number)

    def a_player_is_dead(self, target_player: int):
        self.connection.send(PlayerIsDead(target_player))

    def _handle_assassinate(self, target_num: int, other_players: dict[int, 'Player']):
        target_player = other_players[target_num]

        # Target chooses which card to kill
        def closure_block():
            killed = CardResponse.deserialize(target_player.connection.send_and_receive(ChooseCardToKill()))
            if killed.card not in target_player.cards:
                target_player.debug_message("You don't have that card")
                return False, None
            target_player.remove_card(killed.card)
            for p in self.all_players:
                p.connection.send(PlayerLostACard(target_num, killed.card))
            self._log_successful_action_result(Assassinate(), target_player.number)
            return True, None

        self._extort_a_correct_command_with_threat_of_violence(closure_block, target_player)

    def _handle_foreign_aid(self):
        self.give_money(2)
        self._log_successful_action_result(ForeignAid(), self.number)

    def _handle_income(self):
        self.give_money(1)
        self._log_successful_action_result(Income(), self.number)

    def _handle_tax(self):
        self.give_money(3)
        self._log_successful_action_result(Tax(), self.number)

    def _handle_coup(self, target_num: int, other_players: dict[int, 'Player']):
        target_player = other_players[target_num]

        # Target chooses which card to kill
        def closure_block():
            killed = CardResponse.deserialize(target_player.connection.send_and_receive(ChooseCardToKill()))
            if killed.card not in target_player.cards:
                target_player.debug_message("You don't have that card")
                return False, None
            target_player.cards.remove(killed.card)
            self._log_successful_action_result(Coup(), target_player.number)
            return True, None

        self._extort_a_correct_command_with_threat_of_violence(closure_block, target_player)

    def _handle_ambassadate(self, deck: list[Card]):
        random.shuffle(deck)
        self.give_card(deck.pop())
        self.give_card(deck.pop())

        def closure_block():
            decision = AmbassadorCardResponse.deserialize(self.connection.send_and_receive(ChooseAmbassadorCardsToRemove()))
            if decision.card1 == decision.card2 and self.cards.count(decision.card1) < 2:
                self.debug_message("You don't have 2 of that card")
                return False, None
            if decision.card1 != decision.card2 and (decision.card1 not in self.cards or decision.card2 not in self.cards):
                self.debug_message("You don't have both those cards")
                return False, None
            self.remove_card(decision.card1)
            self.remove_card(decision.card2)
            deck.append(decision.card1)
            deck.append(decision.card2)
            self._log_successful_action_result(Ambassadate(), self.number)
            return True, None

        self._extort_a_correct_command_with_threat_of_violence(closure_block, self)

    def emergency_kill(self, player: 'Player'):
        debug_print(f"Player {player} died because of rule violations")
        for c in player.cards:
            for p in self.all_players:
                p.connection.send(PlayerLostACard(player.number, c))

        player.cards = []

    def take_turn(self, other_players: dict[int, 'Player'], deck: list[Card]):
        debug_print(f"Player {self} taking turn")

        def closure_block():
            raw = self.connection.send_and_receive(TakeTurn())
            decision = ActionDecision.deserialize(raw)

            if decision is None:
                return False, None

            action = decision.action()
            if isinstance(decision, TargetedActionDecision):
                target_number = decision.target()
            else:
                target_number = -1

            debug_print(f"Player {self} attempting {action} on {target_number}")

            if not self._check_action_leglity(action, target_number, other_players):
                return False, None

            if not self._handle_challenges(action, target_number, other_players, deck):
                return True, None

            self._handle_dead_players_in_the_middle_of_actions(other_players)
            if action.targeted and target_number not in other_players:
                return True, None

            # Cost happens before possible blocking, but after challenges
            if action.cost > 0:
                self.give_money(-action.cost)

            if not self._handle_blocks(action, target_number, other_players, deck):
                return True, None

            self._handle_dead_players_in_the_middle_of_actions(other_players)
            if action.targeted and target_number not in other_players:
                return True, None

            if action == Steal():
                self._handle_steal(target_number, other_players)
            elif action == Assassinate():
                self._handle_assassinate(target_number, other_players)
            elif action == ForeignAid():
                self._handle_foreign_aid()
            elif action == Income():
                self._handle_income()
            elif action == Tax():
                self._handle_tax()
            elif action == Coup():
                self._handle_coup(target_number, other_players)
            elif action == Ambassadate():
                self._handle_ambassadate(deck)
            return True, None

        self._extort_a_correct_command_with_threat_of_violence(closure_block, self)


class Game:
    def __init__(self, connections: list[Connection], deck: list[Card] | None = None):
        self.players = {i: Player(i, c) for i, c in enumerate(connections)}
        for p in self.players.values():
            p.player_number(p.number)
            p.find_name()
        debug_print(f"Players {[p.name for p in self.players.values()]} joined.")
        self.alive_players = list(self.players.values())
        self.deck = []
        if deck is None:
            for c in Card.all():
                self.deck.extend(EACH_CARD_IN_DECK * [c])
        else:
            self.deck = deck

    def _setup_player(self, player):
        random.shuffle(self.deck)
        player.give_card(self.deck.pop())
        player.give_card(self.deck.pop())
        player.give_money(2)
        for other in self.players.values():
            if player.number != other.number:
                player.add_opponent(other.number, other.name)

    def setup_players(self):
        for p in self.players.values():
            self._setup_player(p)

        for p in self.players.values():
            p.set_all_players(list(self.players.values()))

    # Returns whether the game has ended
    def run_one_turn(self) -> bool:
        taking_action = self.alive_players[0]
        taking_action.take_turn({p.number: p for p in self.alive_players[1:]}, self.deck)

        # Eliminate players, and rotate turn
        newly_dead = [p for p in self.alive_players if not len(p.cards)]
        for d in newly_dead:
            debug_print(f"Player {d.number} is dead")
            for p in self.players.values():
                p.a_player_is_dead(d.number)
        self.alive_players = [p for p in self.alive_players[1:] + [self.alive_players[0]] if len(p.cards)]

        if len(self.alive_players) == 1:
            debug_print(f"Winner is {self.alive_players[0]}!")
            for p in self.players.values():
                p.shutdown()
            return True
        return False

    def run(self):
        self.setup_players()
        while True:
            if self.run_one_turn():
                break

