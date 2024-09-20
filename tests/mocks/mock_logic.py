from game.enums.actions import Action
from game.enums.cards import Card
from game.logic.clients import ClientLogic
from game.messages.responses import RevealCard, Concede, YouAreChallengedDecision, Block, NoBlock, DoYouBlockDecision, \
    DoYouChallengeDecision, Challenge, Allow


class MockLogic(ClientLogic):
    def __init__(self, action: lambda self: (Action, int), challenge: bool, block: bool, challenge_block: bool):
        self.opponents = []
        self.cards = []
        self.number = -1

        self.action = action
        self.challenge = challenge
        self.block = block
        self.challenge_block = challenge_block
        self.money = 0

    def shutdown(self):
        pass

    def ask_name(self) -> str:
        return "mock"

    def add_opponent(self, number: int, name: str):
        self.opponents.append(number)

    def set_player_number(self, num: int):
        self.number = num

    def add_card(self, c: Card):
        print("Adding", c)
        self.cards.append(c)

    def change_money(self, m: int):
        self.money += m

    def remove_card(self, c: Card):
        self.cards.remove(c)

    def choose_card_to_kill(self) -> Card:
        return self.cards[-1]

    def choose_ambassador_cards_to_remove(self) -> (Card, Card):
        return self.cards[0], self.cards[1]

    def take_turn(self) -> (Action, int):
        return self.action(self)

    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if action.requires_card[0] in self.cards:
            return RevealCard()
        else:
            return Concede()

    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        if blocker in self.cards:
            return RevealCard()
        else:
            return Concede()

    def do_you_block(self, action: Action, taken_by: int) -> DoYouBlockDecision:
        have_block_card = set(self.cards).intersection(set(action.blocked_by))
        block_card = have_block_card.pop() if have_block_card else action.blocked_by[0]
        return Block(block_card) if self.block else NoBlock()

    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        return Challenge() if self.challenge else Allow()

    def do_you_challenge_block(self, action: Action, taken_by: int, target: int, block_card: Card,
                               blocker: int) -> DoYouChallengeDecision:
        return Challenge() if self.challenge_block else Allow()

    def action_was_taken(self, action: Action, taken_by: int, target: int):
        pass

    def action_was_blocked(self, action: Action, taken_by: int, target: int, block_card: Card, blocker: int):
        pass

    def action_was_challenged(self, action: Action, taken_by: int, target: int, challenger: int, successful: bool):
        pass

    def block_was_challenged(self, action: Action, taken_by: int, target: int, block_card: Card, blocker: int,
                             challenger: int, successful: bool):
        pass

    def player_lost_a_card(self, player: int, card: Card):
        pass

    def a_player_is_dead(self, num: int):
        pass

    def debug_message(self, msg: str):
        print(f"Debug: {msg}")
