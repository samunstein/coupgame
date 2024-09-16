from abc import abstractmethod

from common.common import debug_print, commands_params
from config import PARAM_SPLITTER, CONTROL_CHAR_REPLACE, COMMAND_END
from connection.common import OpenSocket
from game.enums.actions import all_actions_map
from game.enums.commands import *
from game.logic.clients import ClientLogic

class PlayerClient:
    def __init__(self, connection: OpenSocket, logic: ClientLogic):
        self.connection = connection
        self.logic = logic

    def run(self):
        while True:
            data = self.connection.receive()
            # debug_print(f"# RAW DATA RECEIVED: {data}")
            if not len(data):
                break

            commands = commands_params(data)

            for command_data in commands:
                command, params = command_data

                # Setup and meta
                if command == DEBUG_MESSAGE:
                    debug_print(params[0])
                elif command == SHUTDOWN:
                    self.connection.close()
                    self.logic.shutdown()
                    return
                elif command == ASK_NAME:
                    self.connection.send(
                        self.logic.ask_name()
                            .replace(PARAM_SPLITTER, CONTROL_CHAR_REPLACE)
                            .replace(COMMAND_END, CONTROL_CHAR_REPLACE))
                elif command == ADD_OPPONENT:
                    self.logic.add_opponent(int(params[0]), params[1])
                elif command == SET_PLAYER_NUMBER:
                    self.logic.set_player_number(int(params[0]))

                # State changes
                elif command == ADD_CARD:
                    self.logic.add_card(params[0])
                elif command == CHANGE_MONEY:
                    self.logic.change_money(int(params[0]))
                elif command == REMOVE_CARD:
                    self.logic.remove_card(params[0])

                # Card decisions
                elif command == CHOOSE_CARD_TO_KILL:
                    card = self.logic.choose_card_to_kill()
                    self.connection.send(card)
                elif command == CHOOSE_AMBASSADOR_CARDS_TO_REMOVE:
                    (card1, card2) = self.logic.choose_ambassador_cards_to_remove()
                    self.connection.send(card1, card2)

                # Turn flow
                elif command == TAKE_TURN:
                    action, target = self.logic.take_turn()
                    self.connection.send(action, target)
                elif command == YOUR_ACTION_IS_CHALLENGED:
                    action, target, challenger = all_actions_map()[params[0]], int(params[1]), int(params[2])
                    decision = self.logic.your_action_is_challenged(action, target, challenger)
                    self.connection.send(decision)
                elif command == YOUR_BLOCK_IS_CHALLENGED:
                    action, taken_by, block_card, challenger = all_actions_map()[params[0]], int(params[1]), params[2], int(params[3])
                    decision = self.logic.your_block_is_challenged(action, taken_by, block_card, challenger)
                    self.connection.send(decision)
                elif command == DO_YOU_BLOCK:
                    action, taken_by = all_actions_map()[params[0]], int(params[1])
                    decision, block_card = self.logic.do_you_block(action, taken_by)
                    self.connection.send(decision, block_card)
                elif command == DO_YOU_CHALLENGE_ACTION:
                    action, taken_by, target = all_actions_map()[params[0]], int(params[1]), int(params[2])
                    decision = self.logic.do_you_challenge_action(action, taken_by, target)
                    self.connection.send(decision)
                elif command == DO_YOU_CHALLENGE_BLOCK:
                    action, taken_by, target, block_card, blocker = all_actions_map()[params[0]], int(params[1]), int(params[2]), params[3], int(params[4])
                    decision = self.logic.do_you_challenge_block(action, taken_by, target, block_card, blocker)
                    self.connection.send(decision)

                # Log
                elif command == ACTION_WAS_TAKEN:
                    action, taken_by, target = all_actions_map()[params[0]], int(params[1]), int(params[2])
                    self.logic.action_was_taken(action, taken_by, target)
                elif command == ACTION_WAS_BLOCKED:
                    action, taken_by, target, block_card, blocker = all_actions_map()[params[0]], int(params[1]), int(params[2]), params[3], int(params[4])
                    self.logic.action_was_blocked(action, taken_by, target, block_card, blocker)
                elif command == ACTION_WAS_CHALLENGED:
                    action, taken_by, target, challenger, success = (
                        all_actions_map()[params[0]], int(params[1]), int(params[2]), int(params[3]), params[4] == "True"
                    )
                    self.logic.action_was_challenged(action, taken_by, target, challenger, success)
                elif command == BLOCK_WAS_CHALLENGED:
                    action, taken_by, target, block_card, blocker, challenger, success = (
                        all_actions_map()[params[0]], int(params[1]), int(params[2]), params[3], int(params[4]), int(params[5]), params[6] == "True"
                    )
                    self.logic.block_was_challenged(action, taken_by, target, block_card, blocker, challenger, success)
                elif command == PLAYER_LOST_A_CARD:
                    player, card = int(params[0]), params[1]
                    self.logic.player_lost_a_card(player, card)
                elif command == A_PLAYER_IS_DEAD:
                    self.logic.a_player_is_dead(int(params[0]))

                else:
                    print("Unknown command", command)
