from abc import abstractmethod

from common.common import debug_print, commands_params
from config import PARAM_SPLITTER, CONTROL_CHAR_REPLACE, COMMAND_END
from connection.common import OpenSocket
from game.enums.commands import ASK_NAME, CHANGE_MONEY, ADD_CARD, DEBUG_MESSAGE, TAKE_TURN, SET_PLAYER_NUMBER, ADD_OPPONENT
from game.logic.clients import ClientLogic


class PlayerClient:
    def __init__(self, connection: OpenSocket, logic: ClientLogic):
        self.connection = connection
        self.logic = logic

    def run(self):
        while True:
            data = self.connection.receive()
            debug_print(f"Received {data}")
            if not len(data):
                break

            commands = commands_params(data)

            for command_data in commands:
                command, params = command_data

                if command == ASK_NAME:
                    self.connection.send(self.logic.ask_name()
                                         .replace(PARAM_SPLITTER, CONTROL_CHAR_REPLACE)
                                         .replace(COMMAND_END, CONTROL_CHAR_REPLACE))
                elif command == CHANGE_MONEY:
                    self.logic.give_money(int(params[0]))
                elif command == ADD_CARD:
                    self.logic.give_card(params[0])
                elif command == DEBUG_MESSAGE:
                    debug_print(params[0])
                elif command == TAKE_TURN:
                    action, target = self.logic.take_turn()
                    self.connection.send(action, target)
                elif command == SET_PLAYER_NUMBER:
                    self.logic.set_number(int(params[0]))
                elif command == ADD_OPPONENT:
                    self.logic.add_opponent(int(params[0]), params[1])
                else:
                    print("Unknown command", command)
