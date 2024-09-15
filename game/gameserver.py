import random

from common.common import debug_print, commands_params, get_just_data_from_socket
from config import PARAM_SPLITTER, CONTROL_CHAR_REPLACE, EACH_CARD_IN_DECK, WRONG_MESSAGE_TOLERANCE
from connection.common import OpenSocket
from game.enums.actions import all_actions_map, Action, DoYouChallengeDecision, YouAreChallengedDecision
from game.enums.cards import all_cards, Card
from game.enums.commands import *


class Player:
    def __init__(self, number: int, connection: OpenSocket):
        self.cards = []
        self.money = 0
        self.connection = connection
        self.name = ""
        self.number = number
        self.all_players = []

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
        except TimeoutError as e:
            debug_print(f"Player {one_responsible} took too long and timed out")
            self.emergency_kill(one_responsible)
        return retval

    def set_all_players(self, all):
        self.all_players = all

    def shutdown(self):
        self.connection.send(SHUTDOWN)
        self.connection.close()

    def give_card(self, c: Card):
        self.cards.append(c)
        self.connection.send(ADD_CARD, c)

    def remove_card(self, c: Card):
        self.cards.remove(c)
        self.connection.send(REMOVE_CARD, c)

    def give_money(self, m: int):
        self.money += m
        self.connection.send(CHANGE_MONEY, m)

    def find_name(self):
        self.name = get_just_data_from_socket(self.connection.send_and_receive(ASK_NAME))[0]
        debug_print(f"{self.name} created")

    def debug_message(self, msg):
        self.connection.send(DEBUG_MESSAGE, msg.replace(PARAM_SPLITTER, CONTROL_CHAR_REPLACE))

    def add_opponent(self, num, name):
        self.connection.send(ADD_OPPONENT, num, name)

    def player_number(self, num):
        self.connection.send(SET_PLAYER_NUMBER, num)

    def _check_action_leglity(self, action, target_number, other_players):
        if action not in all_actions_map():
            self.debug_message("Choose a real action")
            return False
        action = all_actions_map()[action]
        if action.targeted and target_number not in other_players:
            self.debug_message("Target does not exist")
            return False
        if self.money < action.cost:
            self.debug_message("Not enough money")
            return False
        if self.money >= 10 and action != Action.COUP:
            self.debug_message("Must coup")
            return False
        return True

    def _log_successful_action_result(self, action, target_num):
        debug_print(f"{action.name} taken by {self} on {target_num} successful")
        for p in self.all_players:
            p.connection.send(ACTION_WAS_TAKEN, action.name, self.number, target_num)

    def _log_block_result(self, action, target_num, blocked_with):
        debug_print(f"{action.name} taken by {self} on {target_num} blocked with {blocked_with}")
        for p in self.all_players:
            p.connection.send(ACTION_WAS_BLOCKED, action.name, self.number, target_num, blocked_with)

    def _log_challenge_result(self, action, target_num, challenger_num, successful):
        debug_print(f"{action.name} taken by {self} on {target_num} challenged by {challenger_num} with success {successful}")
        for p in self.all_players:
            p.connection.send(ACTION_WAS_CHALLENGED, action.name, self.number, target_num, challenger_num, successful)

    def _log_block_challenge_result(self, action, target_num, blocked_with, challenger_num, successful):
        debug_print(
            f"Blocking with {blocked_with} the {action.name} taken by {self} on {target_num} challenged by {challenger_num} with success {successful}")
        for p in self.all_players:
            p.connection.send(BLOCK_WAS_CHALLENGED, action.name, self.number, target_num, blocked_with, challenger_num, successful)

    def _handle_challenges(self, action, target_number, other_players, deck):
        # Returns whether the action can continue (False if successfully challenged)
        if len(action.requires_card):
            other_numbers_ordered = list(other_players.keys())
            if action.targeted:
                other_numbers_ordered.remove(target_number)
                other_numbers_ordered.insert(0, target_number)

            for other_num in other_numbers_ordered:
                maybe_challenger = other_players[other_num]
                def closure_block() -> (bool, any):
                    decision = get_just_data_from_socket(
                        maybe_challenger.connection.send_and_receive(DO_YOU_CHALLENGE_ACTION, action.name, self.number, target_number)
                    )[0]
                    if decision == DoYouChallengeDecision.CHALLENGE.value:
                        return True, True
                    elif decision == DoYouChallengeDecision.ALLOW.value:
                        return True, False
                    else:
                        maybe_challenger.debug_message("Challenge or allow the action please")
                        return False, None
                challenge = self._extort_a_correct_command_with_threat_of_violence(closure_block, maybe_challenger)
                # Since we're kind of in the middle of logic, handle player dying because of idiocy here
                if challenge is None:
                    self._handle_dead_players_in_the_middle_of_actions(other_players)

                if challenge == False:
                    continue

                if challenge == True:
                    def closure_block():
                        what_do = get_just_data_from_socket(
                            self.connection.send_and_receive(YOUR_ACTION_IS_CHALLENGED, action.name, target_number, maybe_challenger.number)
                        )[0]
                        if what_do == YouAreChallengedDecision.CONCEDE.value:
                            return True, what_do
                        elif what_do == YouAreChallengedDecision.REVEAL_CARD.value:
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

                    if what_did == YouAreChallengedDecision.REVEAL_CARD.value:
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
                        killed = get_just_data_from_socket(life_loser.connection.send_and_receive(CHOOSE_CARD_TO_KILL))[0]
                        if killed not in life_loser.cards:
                            print(killed, life_loser.cards)
                            life_loser.debug_message("You don't have that card")
                            return False, None
                        life_loser.remove_card(killed)
                        self._log_challenge_result(action, target_number, maybe_challenger.number, challenge_success)
                        return True, None

                    self._extort_a_correct_command_with_threat_of_violence(dead_chooser_closure, life_loser)

                    # Challenge not successful => action may continue
                    return not challenge_success

            # No challenges, return
            return True
        else:
            return True

    def _handle_blocks(self, action, target_number, other_players, deck):
        # TODO: If the action allows blocking, ask the defendant which card, if any, they would like to block with.
        #       In case of block, go around the players a few times to check if anyone wants to challenge the block.

        # Returns whether the actions can continue (False if successfully blocked)
        return True

    def _handle_steal(self, target_num, other_players):
        target_player = other_players[target_num]
        money_stolen = min(target_player.money, 2)
        self.give_money(money_stolen)
        target_player.give_money(-money_stolen)
        self._log_successful_action_result(Action.STEAL, target_player.number)

    def a_player_is_dead(self, target_player):
        self.connection.send(A_PLAYER_IS_DEAD, target_player.number)

    def _handle_assassinate(self, target_num, other_players):
        target_player = other_players[target_num]
        # Target chooses which card to kill
        def closure_block():
            killed = get_just_data_from_socket(target_player.connection.send_and_receive(CHOOSE_CARD_TO_KILL))[0]
            if killed not in target_player.cards:
                target_player.debug_message("You don't have that card")
                return False, None
            target_player.cards.remove(killed)
            self._log_successful_action_result(Action.ASSASSINATE, target_player.number)
            return True, None
        self._extort_a_correct_command_with_threat_of_violence(closure_block, target_player)

    def _handle_foreign_aid(self):
        self.give_money(2)
        self._log_successful_action_result(Action.FOREIGN_AID, self.number)

    def _handle_income(self):
        self.give_money(1)
        self._log_successful_action_result(Action.INCOME, self.number)

    def _handle_tax(self):
        self.give_money(3)
        self._log_successful_action_result(Action.TAX, self.number)

    def _handle_coup(self, target_num, other_players):
        target_player = other_players[target_num]
        # Target chooses which card to kill
        def closure_block():
            killed = target_player.connection.send_and_receive(CHOOSE_CARD_TO_KILL)
            if killed not in target_player.cards:
                target_player.debug_message("You don't have that card")
                return False, None
            target_player.cards.remove(killed)
            self._log_successful_action_result(Action.COUP, target_player.number)
            return True, None
        self._extort_a_correct_command_with_threat_of_violence(closure_block, target_player)

    def _handle_ambassadate(self, deck):
        random.shuffle(deck)
        self.give_card(deck.pop())
        self.give_card(deck.pop())
        def closure_block():
            d1, d2 = commands_params(self.connection.send_and_receive(CHOOSE_AMBASSADOR_CARDS_TO_REMOVE))[0]
            cards = [d1] + d2
            if len(cards) != 2:
                self.debug_message("Choose 2 cards")
                return False, None
            if cards[0] == cards[1] and self.cards.count(cards[0]) < 2:
                self.debug_message("You don't have 2 of that card")
                return False, None
            if cards[0] != cards[1] and (cards[0] not in self.cards or cards[1] not in self.cards):
                self.debug_message("You don't have both those cards")
                return False, None
            self.remove_card(cards[0])
            self.remove_card(cards[1])
            deck.append(cards[0])
            deck.append(cards[1])
            self._log_successful_action_result(Action.AMBASSADATE, self.number)
            return True, None
        self._extort_a_correct_command_with_threat_of_violence(closure_block, self)

    def emergency_kill(self, player):
        debug_print(f"Player {player} died because of rule violations")
        player.cards = []

    def take_turn(self, other_players, deck):
        debug_print(f"Player {self} taking turn")
        def closure_block():
            action, target_number = commands_params(self.connection.send_and_receive(TAKE_TURN))[0]
            target_number = int(target_number[0])

            debug_print(f"Player {self} attempting {action} on {target_number}")

            if not self._check_action_leglity(action, target_number, other_players):
                return False, None

            action = all_actions_map()[action]
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

            if action == Action.STEAL:
                self._handle_steal(target_number, other_players)
            elif action == Action.ASSASSINATE:
                self._handle_assassinate(target_number, other_players)
            elif action == Action.FOREIGN_AID:
                self._handle_foreign_aid()
            elif action == Action.INCOME:
                self._handle_income()
            elif action == Action.TAX:
                self._handle_tax()
            elif action == Action.COUP:
                self._handle_coup(target_number, other_players)
            elif action == Action.AMBASSADATE:
                self._handle_ambassadate(deck)
            return True, None

        self._extort_a_correct_command_with_threat_of_violence(closure_block, self)

class Game:
    def __init__(self, connections):
        for c in connections:
            c.connection.settimeout(10)
        self.players = {i: Player(i, c) for i, c in enumerate(connections)}
        for p in self.players.values():
            p.player_number(p.number)
            p.find_name()
        debug_print(f"Players {[p.name for p in self.players.values()]} joined.")
        self.alive_players = list(self.players.values())
        self.deck = []
        for c in all_cards():
            self.deck.extend(EACH_CARD_IN_DECK * [c])

    def setup_player(self, player):
        random.shuffle(self.deck)
        player.give_card(self.deck.pop())
        player.give_card(self.deck.pop())
        player.give_money(2)
        for other in self.players.values():
            if player.number != other.number:
                player.add_opponent(other.number, other.name)

    def run(self):
        for p in self.players.values():
            self.setup_player(p)

        for p in self.players.values():
            p.set_all_players(self.players.values())

        while True:
            taking_action = self.alive_players[0]
            taking_action.take_turn({p.number: p for p in self.alive_players[1:]}, self.deck)

            # Eliminate players, and rotate turn
            newly_dead = [p for p in self.alive_players if not len(p.cards)]
            for d in newly_dead:
                debug_print(f"Player {d.number} is dead")
                for p in self.players.values():
                    print(f"Sending to {p}")
                    p.a_player_is_dead(d)
            self.alive_players = [p for p in self.alive_players[1:] + [self.alive_players[0]] if len(p.cards)]

            if len(self.alive_players) == 1:
                debug_print(f"Winner is {self.alive_players[0]}!")
                for p in self.players.values():
                    p.shutdown()
                break