from abc import ABCMeta

from game.enums.actions import Action
from game.enums.cards import Card
from game.messages.common import ParseSubclassNameParameters


class Command(ParseSubclassNameParameters, metaclass=ABCMeta):
    pass


class NoParameterCommand(Command, metaclass=ABCMeta):
    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'NoParameterCommand':
        return cls()

    def write_data_str_list(self) -> list[object]:
        return []

    def __init__(self):
        pass


class DebugMessage(Command):
    message_name = "debug_msg"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'DebugMessage':
        return cls(params[0])

    def write_data_str_list(self) -> list[object]:
        return [self.message]

    def __init__(self, msg: str):
        self.message = msg


class Shutdown(NoParameterCommand):
    message_name = "shutdown"


class AskName(NoParameterCommand):
    message_name = "ask_name"


class AddOpponent(Command):
    message_name = "add_opponent"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'AddOpponent':
        return cls(int(params[0]), params[1])

    def write_data_str_list(self) -> list[object]:
        return [self.number, self.player_name]

    def __init__(self, number: int, name: str):
        self.number = number
        self.player_name = name


class SetPlayerNumber(Command):
    message_name = "set_player_number"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'SetPlayerNumber':
        return cls(int(params[0]))

    def write_data_str_list(self) -> list[object]:
        return [str(self.number)]

    def __init__(self, number: int):
        self.number = number

class AddCard(Command):
    message_name = "add_card"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'AddCard':
        return cls(Card.with_name(params[0]))

    def write_data_str_list(self) -> list[object]:
        return [self.card]

    def __init__(self, card: Card):
        self.card = card


class RemoveCard(Command):
    message_name = "remove_card"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'RemoveCard':
        return cls(Card.with_name(params[0]))

    def write_data_str_list(self) -> list[object]:
        return [self.card]

    def __init__(self, card: Card):
        self.card = card


class ChangeMoney(Command):
    message_name = "change_money"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'ChangeMoney':
        return cls(int(params[0]))

    def write_data_str_list(self) -> list[object]:
        return [str(self.number)]

    def __init__(self, number: int):
        self.number = number


class NewGame(NoParameterCommand):
    message_name = "new_game"


class PlayerLostACard(Command):
    message_name = "player_lost_a_card"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'PlayerLostACard':
        return cls(int(params[0]), Card.with_name(params[1]))

    def write_data_str_list(self) -> list[object]:
        return [self.player, self.card]

    def __init__(self, player: int, card: Card):
        self.player = player
        self.card = card


class PlayerIsDead(Command):
    message_name = "a_player_is_dead"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'PlayerIsDead':
        return cls(int(params[0]))

    def write_data_str_list(self) -> list[object]:
        return [self.number]

    def __init__(self, number: int):
        self.number = number


class PlayerViolatedRules(Command):
    message_name = "rules_violation"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'PlayerViolatedRules':
        return cls(int(params[0]))

    def write_data_str_list(self) -> list[object]:
        return [self.number]

    def __init__(self, number: int):
        self.number = number


class ChooseCardToKill(NoParameterCommand):
    message_name = "choose_card_to_kill"


class ChooseAmbassadorCardsToRemove(NoParameterCommand):
    message_name = "choose_ambassador_cards"


class TakeTurn(NoParameterCommand):
    message_name = "take_turn"


class YourActionIsChallenged(Command):
    message_name = "your_action_is_challenged"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'YourActionIsChallenged':
        return cls(Action.with_name(params[0]), int(params[1]), int(params[2]))

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.target, self.challenger]

    def __init__(self, action: Action, target: int, challenger: int):
        self.action = action
        self.target = target
        self.challenger = challenger


class YourBlockIsChallenged(Command):
    message_name = "your_block_is_challenged"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'YourBlockIsChallenged':
        return cls(Action.with_name(params[0]), int(params[1]), Card.with_name(params[2]), int(params[3]))

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_doer, self.block_card, self.challenger]

    def __init__(self, action: Action, action_doer: int, block_card: Card, challenger: int):
        # Target is not needed, because in coup rules it so happens that all blockable actions either
        # target only the blocker, or are not targeted.
        self.action = action
        self.action_doer = action_doer
        self.block_card = block_card
        self.challenger = challenger


class DoYouBlock(Command):
    message_name = "do_you_block"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'DoYouBlock':
        return cls(Action.with_name(params[0]), int(params[1]))

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_doer]

    def __init__(self, action: Action, action_doer: int):
        self.action = action
        self.action_doer = action_doer


class DoYouChallengeAction(Command):
    message_name = "do_you_challenge_action"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'DoYouChallengeAction':
        return cls(Action.with_name(params[0]), int(params[1]), int(params[2]))

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_doer, self.target]

    def __init__(self, action: Action, action_doer: int, target: int):
        self.action = action
        self.action_doer = action_doer
        self.target = target


class DoYouChallengeBlock(Command):
    message_name = "do_you_challenge_block"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'DoYouChallengeBlock':
        return cls(Action.with_name(params[0]), int(params[1]), int(params[2]), Card.with_name(params[3]),
                   int(params[4]))

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_doer, self.target, self.block_card, self.blocked_by]

    def __init__(self, action: Action, action_doer: int, target: int, block_card: Card, blocked_by: int):
        self.action = action
        self.action_doer = action_doer
        self.target = target
        self.block_card = block_card
        self.blocked_by = blocked_by


class ActionWasTaken(Command):
    message_name = "log_action_was_taken"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'ActionWasTaken':
        return cls(Action.with_name(params[0]), int(params[1]), int(params[2]))

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_doer, self.target]

    def __init__(self, action: Action, action_doer: int, target: int):
        self.action = action
        self.action_doer = action_doer
        self.target = target


class ActionWasBlocked(Command):
    message_name = "log_action_was_blocked"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'ActionWasBlocked':
        return cls(Action.with_name(params[0]), int(params[1]), int(params[2]), Card.with_name(params[3]),
                   int(params[4]))

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_doer, self.target, self.block_card, self.blocked_by]

    def __init__(self, action: Action, action_doer: int, target: int, block_card: Card, blocked_by: int):
        self.action = action
        self.action_doer = action_doer
        self.target = target
        self.block_card = block_card
        self.blocked_by = blocked_by


class ActionWasChallenged(Command):
    message_name = "log_action_was_challenged"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'ActionWasChallenged':
        return cls(Action.with_name(params[0]), int(params[1]), int(params[2]), int(params[3]), params[4] == "True")

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_doer, self.target, self.challenger, self.success]

    def __init__(self, action: Action, action_doer: int, target: int, challenger: int, success: bool):
        self.action = action
        self.action_doer = action_doer
        self.target = target
        self.challenger = challenger
        self.success = success


class BlockWasChallenged(Command):
    message_name = "log_block_was_challenged"

    @classmethod
    def parse_from_params(cls, params: list[str]) -> 'BlockWasChallenged':
        return cls(Action.with_name(params[0]), int(params[1]), int(params[2]), Card.with_name(params[3]),
                   int(params[4]), int(params[5]), params[6] == "True")

    def write_data_str_list(self) -> list[object]:
        return [self.action, self.action_taker, self.target, self.block_card, self.blocked_by, self.challenger,
                self.success]

    def __init__(self, action: Action, action_taker: int, target: int, block_card: Card, blocked_by: int,
                 challenger: int, success: bool):
        self.action = action
        self.action_taker = action_taker
        self.target = target
        self.challenger = challenger
        self.success = success
        self.block_card = block_card
        self.blocked_by = blocked_by
