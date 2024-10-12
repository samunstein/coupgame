from abc import abstractmethod

from common.common import debug_print
from game.enums.actions import Action
from game.enums.cards import Card
from game.messages.responses import YouAreChallengedDecision, ActionDecision, DoYouBlockDecision, \
    DoYouChallengeDecision, AssassinateDecision, IncomeDecision, \
    RevealCard, Concede, Block, NoBlock, Challenge, Allow, CardResponse, AmbassadorCardResponse


class ClientLogic:
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
    def a_player_is_dead(self, num: int):
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
        self.money = 0
        self.cards = []
        self.opponents = {}
        self.number = -1

    # Meta and setup
    def debug_message(self, msg: str):
        debug_print(msg)

    def shutdown(self):
        debug_print("Goodbye!")

    def ask_name(self) -> str:
        return f"P{self.number}"

    def add_opponent(self, number: int, name: str):
        print("Opponent", number, name)
        self.opponents[number] = name

    def set_player_number(self, num: int):
        self.number = num
        print(f"Your player number is {num}")

    def new_game(self):
        self.cards = []

    # State changes
    def add_card(self, c: Card):
        self.cards.append(c)
        print(f"Given {c} card. Cards now {self.cards}")

    def change_money(self, m: int):
        self.money += m
        print(f"Given {m} money")

    def remove_card(self, c: Card):
        self.cards.remove(c)
        print(f"Removing {c}. Cards now {self.cards}")

    # Card decisions
    def choose_ambassador_cards_to_remove(self) -> AmbassadorCardResponse:
        print(f"Choosing {self.cards[0:2]} to shuffle by ambassador")
        return AmbassadorCardResponse(self.cards[0], self.cards[1])

    def choose_card_to_kill(self) -> CardResponse:
        print(f"Choosing {self.cards[0]} to kill")
        return CardResponse(self.cards[0])

    # Turn flow
    def take_turn(self) -> ActionDecision:
        if self.money >= 3:
            print("Taking action assassinate")
            return AssassinateDecision(list(self.opponents.keys())[0])
        else:
            print("Taking action income")
            return IncomeDecision()

    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if action.requires_card[0] in self.cards:
            print(f"Revealing card {action.requires_card[0]} to challenge")
            return RevealCard()
        else:
            print("Conceding to challenge")
            return Concede()

    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        if blocker in self.cards:
            print("My block is challenged. I have the blocker though")
            return RevealCard()
        else:
            print("My block is challenged. I admit I don't have the blocker")
            return Concede()

    def do_you_block(self, action: Action, taken_by: int) -> DoYouBlockDecision:
        can_block_with = set(action.blocked_by).intersection(set(self.cards))
        if len(can_block_with):
            print(f"I block the {action.name} from {taken_by}")
            return Block(can_block_with.pop())
        else:
            print(f"I don't block the {action.name} from {taken_by}")
            return NoBlock()

    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        if target == self.number:
            print(f"I challenge the {action.name} from {taken_by} to {target}")
            return Challenge()
        else:
            print(f"I don't challenge the {action.name} from {taken_by} to {target}")
            return Allow()

    def do_you_challenge_block(self, action: Action, taken_by: int, target: int,
                               block_card: Card, blocker: int) -> DoYouChallengeDecision:
        if taken_by == self.number:
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

    def a_player_is_dead(self, num: int):
        if num != self.number:
            self.opponents.pop(num)
        print(f"Player {num} is dead.")
