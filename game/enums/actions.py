from game.enums.cards import *


class Action:
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def targeted(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def cost(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def requires_card(self) -> list[Card]:
        raise NotImplementedError

    @property
    @abstractmethod
    def blocked_by(self) -> list[Card]:
        raise NotImplementedError

    @classmethod
    def with_name(cls, name: str) -> 'Action':
        return [a for a in cls.all() if a.name == name][0]

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other: 'Action'):
        return self.name == other.name

    @classmethod
    def all(cls) -> list['Action']:
        return [sub() for sub in cls.__subclasses__()]


class Steal(Action):
    name = "steal"
    cost = 0
    targeted = True
    requires_card = [Captain()]
    blocked_by = [Captain(), Ambassador()]

    def __init__(self):
        pass

class Assassinate(Action):
    name = "assassinate"
    cost = 3
    targeted = True
    requires_card = [Assassin()]
    blocked_by = [Contessa()]

    def __init__(self):
        pass

class ForeignAid(Action):
    name = "foreign_aid"
    cost = 0
    targeted = False
    requires_card = []
    blocked_by = [Duke()]

    def __init__(self):
        pass

class Income(Action):
    name = "income"
    cost = 0
    targeted = False
    requires_card = []
    blocked_by = []

    def __init__(self):
        pass

class Tax(Action):
    name = "tax"
    cost = 0
    targeted = False
    requires_card = [Duke()]
    blocked_by = []

    def __init__(self):
        pass

class Coup(Action):
    name = "coup"
    cost = 7
    targeted = True
    requires_card = []
    blocked_by = []

    def __init__(self):
        pass


class Ambassadate(Action):
    name = "ambassadate"
    cost = 0
    targeted = False
    requires_card = [Ambassador()]
    blocked_by = []

    def __init__(self):
        pass

