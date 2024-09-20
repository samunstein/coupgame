from abc import abstractmethod


class Card:
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @classmethod
    def with_name(cls, name: str) -> 'Card':
        return [c for c in cls.all() if c.name == name][0]

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other: 'Card'):
        return self.name == other.name

    @classmethod
    def all(cls) -> list['Card']:
        return [sub() for sub in cls.__subclasses__()]

    def __hash__(self):
        return hash(self.name)


class Duke(Card):
    name = "duke"

    def __init__(self):
        pass

class Contessa(Card):
    name = "contessa"

    def __init__(self):
        pass

class Assassin(Card):
    name = "assassin"

    def __init__(self):
        pass

class Captain(Card):
    name = "captain"

    def __init__(self):
        pass

class Ambassador(Card):
    name = "ambassador"

    def __init__(self):
        pass
