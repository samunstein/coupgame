import random
from abc import abstractmethod

from common.common import debug_print
from game.enums.actions import Action, YouAreChallengedDecision, DoYouBlockDecision, DoYouChallengeDecision
from game.enums.cards import Card


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

    # Card decisions
    @abstractmethod
    def choose_card_to_kill(self) -> Card:
        raise NotImplementedError()

    @abstractmethod
    def choose_ambassador_cards_to_remove(self) -> (Card, Card):
        raise NotImplementedError()


    # Turn flow
    @abstractmethod
    def take_turn(self) -> (Action, int):
        raise NotImplementedError()

    @abstractmethod
    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        raise NotImplementedError()

    @abstractmethod
    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card, challenged_by: int) -> YouAreChallengedDecision:
        raise NotImplementedError()

    @abstractmethod
    def do_you_block(self, action: Action, taken_by: int) -> (DoYouBlockDecision, Card):
        raise NotImplementedError()

    @abstractmethod
    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        raise NotImplementedError()

    @abstractmethod
    def do_you_challenge_block(self, action: Action, taken_by: int, target: int, blocker: Card) -> DoYouChallengeDecision:
        raise NotImplementedError()

    # Log
    @abstractmethod
    def action_was_taken(self, action: Action, taken_by: int, target: int):
        raise NotImplementedError()

    @abstractmethod
    def action_was_blocked(self, action: Action, taken_by: int, target: int, blocker: Card):
        raise NotImplementedError()

    @abstractmethod
    def action_was_challenged(self, action: Action, taken_by: int, target: int, challenger: int, successful: bool):
        raise NotImplementedError()

    @abstractmethod
    def block_was_challenged(self, action: Action, taken_by: int, target: int, blocker: Card, challenger: int, successful: bool):
        raise NotImplementedError()

    @abstractmethod
    def player_lost_a_card(self, player: int, card: Card):
        raise NotImplementedError()

    @abstractmethod
    def a_player_is_dead(self, num: int):
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

    # State changes
    def add_card(self, c: Card):
        self.cards.append(c)
        print(f"Given {c} card. Cards now {self.cards}")

    def change_money(self, m: int):
        self.money += m
        print(f"Given {m} money")

    def remove_card(self, c: Card):
        print(f"Removing {c}")
        self.cards.remove(c)

    # Card decisions
    def choose_ambassador_cards_to_remove(self) -> (Card, Card):
        print(f"Choosing {self.cards[0:2]} to shuffle by ambassador")
        return self.cards[0], self.cards[1]

    def choose_card_to_kill(self) -> Card:
        print(f"Choosing {self.cards[0]} to kill")
        return self.cards[0]

    # Turn flow
    def take_turn(self) -> (Action, int):
        if self.money >= 3:
            return Action.ASSASSINATE, list(self.opponents.keys())[0]
        else:
            return Action.INCOME, self.number

    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if action.requires_card[0] in self.cards:
            print("Revealing card to challenge")
            return YouAreChallengedDecision.REVEAL_CARD
        else:
            print("Conceding to challenge")
            return YouAreChallengedDecision.CONCEDE

    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        if blocker in self.cards:
            return YouAreChallengedDecision.REVEAL_CARD
        else:
            return YouAreChallengedDecision.CONCEDE

    def do_you_block(self, action: Action, taken_by: int) -> (DoYouBlockDecision, Card):
        can_block_with = set(action.blocked_by).intersection(set(self.cards))
        if len(can_block_with):
            return DoYouBlockDecision.BLOCK, can_block_with.pop()
        else:
            return DoYouBlockDecision.NO_BLOCK, ""

    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        if target == self.number:
            return DoYouChallengeDecision.CHALLENGE
        else:
            return DoYouChallengeDecision.ALLOW

    def do_you_challenge_block(self, action: Action, taken_by: int, target: int,
                               blocker: Card) -> DoYouChallengeDecision:
        if taken_by == self.number:
            return DoYouChallengeDecision.CHALLENGE
        else:
            return DoYouChallengeDecision.ALLOW

    # Log
    def action_was_taken(self, action: Action, taken_by: int, target: int):
        print(f"Action {action.name} was successfully taken by {taken_by} towards {target}")

    def action_was_blocked(self, action: Action, taken_by: int, target: int, blocker: Card):
        print(f"Action {action.name} was taken by {taken_by} to {target} and blocked with {blocker}")

    def action_was_challenged(self, action: Action, taken_by: int, target: int, challenger: int, successful: bool):
        print(f"Action {action.name} was taken by {taken_by} to {target} and challenged by {challenger} with success {successful}")

    def block_was_challenged(self, action: Action, taken_by: int, target: int, blocker: Card, challenger: int,
                             successful: bool):
        print(
            f"Action {action.name} was taken by {taken_by} to {target} and blocked by {blocker} which was challenged by {challenger} with success {successful}")

    def player_lost_a_card(self, player: int, card: Card):
        print(f"Player {player} lost a card and revealed {card}")

    def a_player_is_dead(self, num: int):
        if num != self.number:
            self.opponents.pop(num)
        print(f"Player {num} is dead.")
