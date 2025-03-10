from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from common.common import debug_print
from game.enums.actions import Action
from game.enums.cards import Card
from game.messages.responses import YouAreChallengedDecision, ActionDecision, DoYouBlockDecision, \
    DoYouChallengeDecision, AssassinateDecision, IncomeDecision, \
    RevealCard, Concede, Block, NoBlock, Challenge, Allow, CardResponse, AmbassadorCardResponse

@dataclass(frozen=True)
class OpponentState:
    number: int
    cards_amount: int
    dead_cards: list[Card]
    money: int

@dataclass(frozen=True)
class ClientState:
    number: int
    cards: list[Card]
    dead_cards: list[Card]
    money: int
    opponents: dict[int, OpponentState]

    def alive_opponents(self) -> dict[int, OpponentState]:
        return {opp.number: opp for opp in self.opponents.values() if opp.cards_amount}

class ClientLogic:
    get_state: Callable[[], ClientState]
    def set_state_fetch_function(self, fn: Callable[[], ClientState]):
        self.get_state = fn

    # Meta and setup
    @abstractmethod
    def debug_message(self, msg: str):
        raise NotImplementedError()

    @abstractmethod
    def shutdown(self):
        raise NotImplementedError()

    @abstractmethod
    def ask_name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def add_opponent(self, number: int, name: str):
        raise NotImplementedError()

    @abstractmethod
    def set_player_number(self, num: int):
        raise NotImplementedError()

    @abstractmethod
    def new_game(self):
        raise NotImplementedError()

    # State changes
    @abstractmethod
    def add_card(self, c: Card):
        raise NotImplementedError()

    @abstractmethod
    def change_money(self, m: int):
        raise NotImplementedError()

    @abstractmethod
    def remove_card(self, c: Card):
        raise NotImplementedError()

    @abstractmethod
    def player_lost_a_card(self, player: int, card: Card):
        raise NotImplementedError()

    @abstractmethod
    def money_changed(self, player: int, amount: int):
        raise NotImplementedError()

    @abstractmethod
    def a_player_violated_rules(self, num: int):
        raise NotImplementedError()

    # Card decisions
    @abstractmethod
    def choose_card_to_kill(self) -> CardResponse:
        raise NotImplementedError()

    @abstractmethod
    def choose_ambassador_cards_to_remove(self) -> AmbassadorCardResponse:
        raise NotImplementedError()

    # Turn flow
    @abstractmethod
    def take_turn(self) -> ActionDecision:
        raise NotImplementedError()

    @abstractmethod
    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        raise NotImplementedError()

    @abstractmethod
    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        raise NotImplementedError()

    @abstractmethod
    def do_you_block(self, action: Action, taken_by: int) -> DoYouBlockDecision:
        raise NotImplementedError()

    @abstractmethod
    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        raise NotImplementedError()

    @abstractmethod
    def do_you_challenge_block(self, action: Action, taken_by: int, target: int, block_card: Card,
                               blocker: int) -> DoYouChallengeDecision:
        raise NotImplementedError()

    # Log
    @abstractmethod
    def action_was_taken(self, action: Action, taken_by: int, target: int):
        raise NotImplementedError()

    @abstractmethod
    def action_was_blocked(self, action: Action, taken_by: int, target: int, block_card: Card, blocker: int):
        raise NotImplementedError()

    @abstractmethod
    def action_was_challenged(self, action: Action, taken_by: int, target: int, challenger: int, successful: bool):
        raise NotImplementedError()

    @abstractmethod
    def block_was_challenged(self, action: Action, taken_by: int, target: int, block_card: Card, blocker: int,
                             challenger: int, successful: bool):
        raise NotImplementedError()


class ExtremelySimpleTestClient(ClientLogic):
    def __init__(self):
        pass
    # Meta and setup
    def debug_message(self, msg: str):
        debug_print(msg)

    def shutdown(self):
        debug_print("Goodbye!")

    def ask_name(self) -> str:
        return f"P{self.get_state().number}"

    def add_opponent(self, number: int, name: str):
        print("Opponent", number, name)

    def set_player_number(self, num: int):
        print(f"Your player number is {num}")

    def new_game(self):
        print("New game")

    # State changes
    def add_card(self, c: Card):
        print(f"Given {c} card. Cards now {self.get_state().cards}")

    def change_money(self, m: int):
        print(f"Given {m} money")

    def remove_card(self, c: Card):
        print(f"Removing {c}. Cards now {self.get_state().cards}")

    # Card decisions
    def choose_ambassador_cards_to_remove(self) -> AmbassadorCardResponse:
        print(f"Choosing {self.get_state().cards[0:2]} to shuffle by ambassador")
        return AmbassadorCardResponse(self.get_state().cards[0],self.get_state().cards[1])

    def choose_card_to_kill(self) -> CardResponse:
        print(f"Choosing {self.get_state().cards[0]} to kill")
        return CardResponse(self.get_state().cards[0])

    # Turn flow
    def take_turn(self) -> ActionDecision:
        if self.get_state().money >= 3:
            print("Taking action assassinate")
            return AssassinateDecision(list(self.get_state().alive_opponents().keys())[0])
        else:
            print("Taking action income")
            return IncomeDecision()

    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if action.requires_card[0] in self.get_state().cards:
            print(f"Revealing card {action.requires_card[0]} to challenge")
            return RevealCard()
        else:
            print("Conceding to challenge")
            return Concede()

    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        if blocker in self.get_state().cards:
            print("My block is challenged. I have the blocker though")
            return RevealCard()
        else:
            print("My block is challenged. I admit I don't have the blocker")
            return Concede()

    def do_you_block(self, action: Action, taken_by: int) -> DoYouBlockDecision:
        can_block_with = set(action.blocked_by).intersection(set(self.get_state().cards))
        if len(can_block_with):
            print(f"I block the {action.name} from {taken_by}")
            return Block(can_block_with.pop())
        else:
            print(f"I don't block the {action.name} from {taken_by}")
            return NoBlock()

    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        if target == self.get_state().number:
            print(f"I challenge the {action.name} from {taken_by} to {target}")
            return Challenge()
        else:
            print(f"I don't challenge the {action.name} from {taken_by} to {target}")
            return Allow()

    def do_you_challenge_block(self, action: Action, taken_by: int, target: int,
                               block_card: Card, blocker: int) -> DoYouChallengeDecision:
        if taken_by == self.get_state().number:
            print(f"I challenge the block of {action.name} from {taken_by} to {target} with {block_card} by {blocker}")
            return Challenge()
        else:
            print(
                f"I don't challenge the block of {action.name} from {taken_by} to {target} with {block_card} by {blocker}")
            return Allow()

    # Log
    def action_was_taken(self, action: Action, taken_by: int, target: int):
        print(f"Log: Action {action.name} was successfully taken by {taken_by} towards {target}")

    def action_was_blocked(self, action: Action, taken_by: int, target: int, block_card: Card, blocker: int):
        print(f"Log: Action {action.name} was blocked with {blocker} by {blocker}. Taken by {taken_by} to {target}.")

    def action_was_challenged(self, action: Action, taken_by: int, target: int, challenger: int, successful: bool):
        print(
            f"Log: Action {action.name} was challenged by {challenger} with success {successful}. Taken by {taken_by} to {target}")

    def block_was_challenged(self, action: Action, taken_by: int, target: int, block_card: Card, blocker: int,
                             challenger: int,
                             successful: bool):
        print(
            f"Log: Action {action.name} block with {block_card} by {blocker} was challenged by {challenger} with success {successful}. Taken by {taken_by} to {target}")

    def player_lost_a_card(self, player: int, card: Card):
        print(f"Player {player} lost a card and revealed {card}")

    def money_changed(self, player: int, amount: int):
        pass

    def a_player_violated_rules(self, num: int):
        print(f"Player {num} violated rules")
