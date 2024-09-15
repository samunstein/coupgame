from abc import abstractmethod

from common.common import debug_print
from game.enums.actions import ACTION


class ClientLogic:
    @abstractmethod
    def give_card(self, c: str):
        pass

    @abstractmethod
    def give_money(self, m: int):
        pass

    @abstractmethod
    def ask_name(self) -> str:
        pass

    @abstractmethod
    def debug_message(self, msg: str):
        pass

    @abstractmethod
    def set_number(self, num: int):
        pass

    @abstractmethod
    def add_opponent(self, num: int, name: str):
        pass

    @abstractmethod
    def take_turn(self) -> (ACTION, int):
        pass

class ExtremelySimpleTestClient(ClientLogic):
    def __init__(self):
        self.money = 0
        self.cards = []
        self.opponents = {}
        self.number = -1

    def give_money(self, m):
        self.money += m
        print(f"Given {m} money")

    def give_card(self, c):
        self.cards.append(c)
        print(f"Given {c} card. Cards now {self.cards}")

    def ask_name(self) -> str:
        return "A"# input("What is your name? ")

    def debug_message(self, msg: str):
        debug_print(msg)

    def set_number(self, num: int):
        self.number = num
        print(f"Your player number is {num}")

    def add_opponent(self, num: int, name: str):
        print("Opponent", num, name)
        self.opponents[num] = name

    def take_turn(self) -> (ACTION, int):
        if self.money >= 3:
            return ACTION.ASSASSINATE, list(self.opponents.keys())[0]
        else:
            return ACTION.INCOME, self.number