from common.common import debug_print
from config import PARAM_SPLITTER, PARAM_SPLITTER_REPLACE
from connection.common import OpenSocket
from game.enums.cards import DUKE, CONTESSA
from game.enums.commands import GIVECARD, GIVEMONEY, ASKNAME, DEBUG_MESSAGE, ADDOPPONENT, GIVEPLAYERNUMBER


class ServerClient:
    def __init__(self, number: int, connection: OpenSocket):
        self.cards = []
        self.money = 0
        self.connection = connection
        self.name = ""
        self.number = number

    def close(self):
        self.connection.close()

    def give_card(self, c):
        self.cards.append(c)
        _ = self.connection.send_and_receive(GIVECARD, c)

    def give_money(self, m):
        self.money += m
        _ = self.connection.send_and_receive(GIVEMONEY, m)

    def find_name(self):
        self.name = self.connection.send_and_receive(ASKNAME)
        debug_print(f"{self.name} created")

    def debug_message(self, msg):
        self.connection.send(DEBUG_MESSAGE, msg.replace(PARAM_SPLITTER, PARAM_SPLITTER_REPLACE))

    def add_opponent(self, num, name):
        self.connection.send(ADDOPPONENT, num, name)

    def player_number(self, num):
        self.connection.send(GIVEPLAYERNUMBER, num)

class Game:
    def __init__(self, connections):
        self.players = {i: ServerClient(i, c) for i, c in enumerate(connections)}
        for p in self.players.values():
            p.find_name()
            p.player_number(p.number)
        debug_print(f"Players {[p.name for p in self.players.values()]} joined.")

    def setup_player(self, player):
        player.give_card(DUKE)
        player.give_card(CONTESSA)
        player.give_money(2)
        for other in self.players.values():
            if player.number != other.number:
                player.add_opponent(other.number, other.name)

    def run(self):
        for p in self.players.values():
            self.setup_player(p)
