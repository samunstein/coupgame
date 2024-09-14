from abc import abstractmethod

from common.common import debug_print
from config import PARAM_SPLITTER, PARAM_SPLITTER_REPLACE
from connection.common import OpenSocket
from game.enums.commands import ASKNAME, GIVEMONEY, OK, GIVECARD, DEBUG_MESSAGE, ACTION, GIVEPLAYERNUMBER, ADDOPPONENT
from game.logic.clients import ClientLogic


class PlayerClient:
    def __init__(self, connection: OpenSocket, logic: ClientLogic):
        self.connection = connection
        self.logic = logic

    def run(self):
        while True:
            data = self.connection.receive()
            if not len(data):
                break

            command = data.split(PARAM_SPLITTER)[0]
            params = data.split(PARAM_SPLITTER)[1:]

            if command == ASKNAME:
                self.connection.send(self.logic.ask_name().replace(PARAM_SPLITTER, PARAM_SPLITTER_REPLACE))
            elif command == GIVEMONEY:
                self.logic.give_money(int(params[0]))
                self.connection.send(OK)
            elif command == GIVECARD:
                self.logic.give_card(params[0])
                self.connection.send(OK)
            elif command == DEBUG_MESSAGE:
                debug_print(params[0])
            elif command == ACTION:
                print("TODO: Tee jotain :D")
            elif command == GIVEPLAYERNUMBER:
                self.logic.set_number(int(params[0]))
            elif command == ADDOPPONENT:
                self.logic.add_opponent(int(params[0]), params[1])
            else:
                print("Unknown command", command)
