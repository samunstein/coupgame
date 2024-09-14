from common.common import debug_print
from game.gameclient import ClientLogic


class ConsoleClient(ClientLogic):
    def __init__(self):
        self.money = 0
        self.cards = []
        self.opponents = []

    def give_money(self, m):
        self.money += 1
        print(f"Given {m} money")

    def give_card(self, c):
        self.cards.append(c)
        print(f"Given {c} card. Cards now {self.cards}")

    def ask_name(self) -> str:
        return input("What is your name? ")

    def debug_message(self, msg: str):
        debug_print(msg)

    def set_number(self, num: int):
        print(f"Your player number is {num}")

    def add_opponent(self, num: int, name: str):
        print("Opponent", num, name)
        self.opponents.append((num, name))