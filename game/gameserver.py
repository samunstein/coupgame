import random

from common.common import debug_print, commands_params
from config import PARAM_SPLITTER, CONTROL_CHAR_REPLACE, EACH_CARD_IN_DECK
from connection.common import OpenSocket
from game.enums.actions import all_actions_map, ACTION
from game.enums.cards import all_cards
from game.enums.commands import ADD_CARD, CHANGE_MONEY, ASK_NAME, DEBUG_MESSAGE, ADD_OPPONENT, SET_PLAYER_NUMBER, \
    TAKE_TURN, ACTION_TAKEN, ACTION_BLOCKED, ACTION_CHALLENGED, BLOCK_CHALLENGE_RESULT, KILL_ANY_CARD, PLAYER_DEAD, \
    CHOOSE_AMBASSADOR_CARDS_TO_REMOVE, REMOVE_CARD


class Player:
    def __init__(self, number: int, connection: OpenSocket):
        self.cards = []
        self.money = 0
        self.connection = connection
        self.name = ""
        self.number = number
        self.all_players = []

    def set_all_players(self, all):
        self.all_players = all

    def close(self):
        self.connection.close()

    def give_card(self, c):
        self.cards.append(c)
        self.connection.send(ADD_CARD, c)

    def remove_card(self, c):
        self.cards.remove(c)
        self.connection.send(REMOVE_CARD, c)

    def give_money(self, m):
        self.money += m
        self.connection.send(CHANGE_MONEY, m)

    def find_name(self):
        self.name = commands_params(self.connection.send_and_receive(ASK_NAME))[0][0]
        debug_print(f"{self.name} created")

    def debug_message(self, msg):
        self.connection.send(DEBUG_MESSAGE, msg.replace(PARAM_SPLITTER, CONTROL_CHAR_REPLACE))

    def add_opponent(self, num, name):
        self.connection.send(ADD_OPPONENT, num, name)

    def player_number(self, num):
        self.connection.send(SET_PLAYER_NUMBER, num)

    def _check_action_leglity(self, action, target, other_players):
        if action not in all_actions_map():
            self.debug_message("Choose a real action")
            return False
        action = all_actions_map()[action]
        if action.targeted and int(target[0]) not in other_players:
            self.debug_message("Target does not exist")
            return False
        if self.money < action.cost:
            self.debug_message("Not enough money")
            return False
        if self.money >= 10 and action != ACTION.COUP:
            self.debug_message("Must coup")
            return False
        return True

    def _log_successful_action_result(self, action, target):
        debug_print(f"{action} taken by {self.name} on {target.name} successful")
        for p in self.all_players:
            p.connection.send(ACTION_TAKEN, action, target.number)

    def _log_block_result(self, action, target, blocked_with):
        debug_print(f"{action} taken by {self.name} on {target.name} blocked with {blocked_with}")
        for p in self.all_players:
            p.connection.send(ACTION_BLOCKED, action, target.number, blocked_with)

    def _log_challenge_result(self, action, target, challenger, successful):
        debug_print(f"{action} taken by {self.name} on {target.name} challenged by {challenger.name} with success {successful}")
        for p in self.all_players:
            p.connection.send(ACTION_CHALLENGED, action, target.number, challenger.number, successful)

    def _log_block_challenge_result(self, action, target, blocked_with, challenger, successful):
        debug_print(
            f"Blocking with {blocked_with} the {action} taken by {self.name} on {target.name} challenged by {challenger.name} with success {successful}")
        for p in self.all_players:
            p.connection.send(BLOCK_CHALLENGE_RESULT, action, target.number, challenger.number, blocked_with, successful)

    def _handle_challenges(self, action, target, other_players):
        # TODO: Go around the players probably as many times as there are players and see if anyone challenges
        #       Probably start with the target if there is any

        # Returns whether the action can continue (False if successfully challenged)
        return True

    def _handle_blocks(self, action, target, other_players):
        # TODO: If the action allows blocking, ask the defendant which card, if any, they would like to block with.
        #       In case of block, go around the players a few times to check if anyone wants to challenge the block.

        # Returns whether the actions can continue (False if successfully blocked)
        return True

    def _handle_steal(self, target_num, other_players):
        target_player = other_players[int(target_num[0])]
        money_stolen = min(target_player.money, 2)
        self.give_money(money_stolen)
        target_player.give_money(-money_stolen)
        self._log_successful_action_result(ACTION.STEAL, target_player)

    def a_player_is_dead(self, target_player):
        debug_print(f"Player {target_player} is dead")
        for p in self.all_players:
            p.connection.send(PLAYER_DEAD, target_player.target_num)

    def _handle_assassinate(self, target_num, other_players):
        target_player = other_players[int(target_num[0])]
        self.give_money(-3)
        # Target chooses which card to kill
        while True:
            killed = target_player.connection.send_and_receive(KILL_ANY_CARD)
            if killed not in target_player.cards:
                target_player.debug_message("You don't have that card")
                pass
            target_player.cards.remove(killed)
            break
        self._log_successful_action_result(ACTION.ASSASSINATE, target_player)

    def _handle_foreign_aid(self):
        self.give_money(2)
        self._log_successful_action_result(ACTION.FOREIGN_AID, self)

    def _handle_income(self):
        self.give_money(1)
        self._log_successful_action_result(ACTION.INCOME, self)

    def _handle_tax(self):
        self.give_money(3)
        self._log_successful_action_result(ACTION.TAX, self)

    def _handle_coup(self, target_num, other_players):
        target_player = other_players[int(target_num[0])]
        self.give_money(-7)
        # Target chooses which card to kill
        while True:
            killed = target_player.connection.send_and_receive(KILL_ANY_CARD)
            if killed not in target_player.cards:
                target_player.debug_message("You don't have that card")
                pass
            target_player.cards.remove(killed)
            break
        self._log_successful_action_result(ACTION.COUP, target_player)

    def _handle_ambassadate(self, deck):
        random.shuffle(deck)
        self.give_card(deck.pop())
        self.give_card(deck.pop())
        while True:
            d1, d2 = commands_params(self.connection.send_and_receive(CHOOSE_AMBASSADOR_CARDS_TO_REMOVE))[0]
            cards = [d1] + d2
            if len(cards) != 2:
                self.debug_message("Choose 2 cards")
                pass
            if cards[0] == cards[1] and self.cards.count(cards[0]) < 2:
                self.debug_message("You don't have 2 of that card")
                pass
            if cards[0] != cards[1] and (cards[0] not in self.cards or cards[1] not in self.cards):
                self.debug_message("You don't have both those cards")
                pass
            self.remove_card(cards[0])
            self.remove_card(cards[1])
            deck.append(cards[0])
            deck.append(cards[1])
            break
        self._log_successful_action_result(ACTION.AMBASSADATE, self)


    def take_turn(self, other_players, deck):
        valid = False
        while not valid:
            action, target = commands_params(self.connection.send_and_receive(TAKE_TURN))[0]

            if not self._check_action_leglity(action, target, other_players):
                pass

            action = all_actions_map()[action]
            self._handle_challenges(action, target, other_players)
            self._handle_blocks(action, target, other_players)

            if action == ACTION.STEAL:
                self._handle_steal(int(target[0]), other_players)
            elif action == ACTION.ASSASSINATE:
                self._handle_assassinate(int(target[0]), other_players)
            elif action == ACTION.FOREIGN_AID:
                self._handle_foreign_aid()
            elif action == ACTION.INCOME:
                self._handle_income()
            elif action == ACTION.TAX:
                self._handle_tax()
            elif action == ACTION.COUP:
                self._handle_coup(int(target[0]), other_players)
            elif action == ACTION.AMBASSADATE:
                self._handle_ambassadate(deck)


class Game:
    def __init__(self, connections):
        self.players = {i: Player(i, c) for i, c in enumerate(connections)}
        for p in self.players.values():
            p.find_name()
            p.player_number(p.number)
        debug_print(f"Players {[p.name for p in self.players.values()]} joined.")
        self.alive_players = list(self.players.values())
        self.deck = []
        for c in all_cards():
            self.deck.extend(EACH_CARD_IN_DECK * [c])

    def setup_player(self, player):
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
            taking_action.take_turn(self.alive_players[1:], self.deck)

            # Eliminate players, and rotate turn
            newly_dead = [p for p in self.alive_players if not len(p.cards)]
            for p in self.players.values():
                for d in newly_dead:
                    p.a_player_is_dead(d)
            self.alive_players = [p for p in self.alive_players[1:] + [self.alive_players[0]] if len(p.cards)]

            if len(self.alive_players) < 2:
                debug_print(f"Winner is {self.alive_players[0]}!")
                for p in self.players.values():
                    p.close()
                break
