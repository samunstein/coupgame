from abc import ABCMeta

from game.enums.actions import *
from game.enums.cards import Card
from game.messages.common import ParseSubclassNameParameters


class Response(ParseSubclassNameParameters, metaclass=ABCMeta):
    pass


class NameResponse(Response):
    message_name = "name_response"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'NameResponse':
        return cls(params[0])

    def write_data_str_list(self) -> list[object]:
        return [self.player_name]

    def __init__(self, name: str):
        self.player_name = name


class ActionDecision(Response, metaclass=ABCMeta):
    @abstractmethod
    def action(self) -> Action:
        raise NotImplementedError()


class TargetedActionDecision(ActionDecision):
    def write_data_str_list(self) -> list[object]:
        return [self.target()]

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'TargetedActionDecision':
        return cls(int(params[0]))

    @abstractmethod
    def target(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def __init__(self, target: int):
        raise NotImplementedError()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"{self.message_name}:{self.target()}"


class NonTargetedActionDecision(ActionDecision, metaclass=ABCMeta):
    def write_data_str_list(self) -> list[object]:
        return []

    def __repr__(self):
        return f"{self.message_name}"

    def __str__(self):
        return repr(self)

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'NonTargetedActionDecision':
        return cls()


class IncomeDecision(NonTargetedActionDecision):
    message_name = "income_decision"

    def __init__(self):
        pass

    def action(self) -> Action:
        return Income()


class ForeignAidDecision(NonTargetedActionDecision):
    message_name = "foreign_aid_decision"

    def __init__(self):
        pass

    def action(self) -> Action:
        return ForeignAid()


class TaxDecision(NonTargetedActionDecision):
    message_name = "tax_decision"

    def __init__(self):
        pass

    def action(self) -> Action:
        return Tax()


class AmbassadateDecision(NonTargetedActionDecision):
    message_name = "ambassadate_decision"

    def __init__(self):
        pass

    def action(self) -> Action:
        return Ambassadate()


class AssassinateDecision(TargetedActionDecision):
    message_name = "assassinate_decision"

    def __init__(self, target: int):
        self._target: int = target

    def action(self) -> Action:
        return Assassinate()

    def target(self) -> int:
        return self._target


class StealDecision(TargetedActionDecision):
    message_name = "steal_decision"

    def __init__(self, target: int):
        self._target = target

    def action(self) -> Action:
        return Steal()

    def target(self) -> int:
        return self._target


class CoupDecision(TargetedActionDecision):
    message_name = "coup_decision"

    def __init__(self, target: int):
        self._target = target

    def action(self) -> Action:
        return Coup()

    def target(self) -> int:
        return self._target


class YouAreChallengedDecision(Response, metaclass=ABCMeta):
    def write_data_str_list(self) -> list[object]:
        return []

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'YouAreChallengedDecision':
        return cls()

    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.message_name}"


class RevealCard(YouAreChallengedDecision):
    # Because of turn flow structuring (block challenge) and coup rules (action challenge), there is always
    # only one card possible to reveal when this one is asked, so no card parameter is needed.
    message_name = "reveal_card"


class Concede(YouAreChallengedDecision):
    message_name = "concede"


class DoYouChallengeDecision(Response, metaclass=ABCMeta):
    def __repr__(self):
        return f"{self.message_name}"

    def write_data_str_list(self) -> list[object]:
        return []

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'DoYouChallengeDecision':
        return cls()

    def __init__(self):
        pass


class Challenge(DoYouChallengeDecision):
    message_name = "challenge"


class Allow(DoYouChallengeDecision):
    message_name = "allow"


class DoYouBlockDecision(Response, metaclass=ABCMeta):
    pass


class Block(DoYouBlockDecision):
    message_name = "block"

    def write_data_str_list(self) -> list[object]:
        return [self.card]

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'Block':
        return cls(Card.with_name(params[0]))

    def __init__(self, card):
        self.card = card

    def __repr__(self):
        return f"{self.message_name}:{self.card}"


class NoBlock(DoYouBlockDecision):
    message_name = "no_block"

    def write_data_str_list(self) -> list[object]:
        return []

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'NoBlock':
        return cls()

    def __init__(self):
        pass


class CardResponse(Response):
    message_name = "card_message"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'CardResponse':
        return cls(Card.with_name(params[0]))

    def write_data_str_list(self) -> list[object]:
        return [self.card]

    def __init__(self, card: Card):
        self.card = card


class AmbassadorCardResponse(Response):
    message_name = "ambassador_card_message"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'AmbassadorCardResponse':
        return cls(Card.with_name(params[0]), Card.with_name(params[1]))

    def write_data_str_list(self) -> list[object]:
        return [self.card1, self.card2]

    def __init__(self, card1: Card, card2: Card):
        self.card1 = card1
        self.card2 = card2
