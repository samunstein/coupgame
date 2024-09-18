from game.enums.actions import Action, DoYouChallengeDecision, DoYouBlockDecision, YouAreChallengedDecision
from game.enums.cards import Card
from game.logic.clients import ClientLogic


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
        self.cards.append(c)

    def change_money(self, m: int):
        self.money += m

    def remove_card(self, c: Card):
        self.cards.remove(c)

    def choose_card_to_kill(self) -> Card:
        return self.cards[-1]

    def choose_ambassador_cards_to_remove(self) -> (Card, Card):
        return self.cards[-1], self.cards[-2]

    def take_turn(self) -> (Action, int):
        return self.action(self)

    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if action.requires_card[0] in self.cards:
            return YouAreChallengedDecision.REVEAL_CARD
        else:
            return YouAreChallengedDecision.CONCEDE

    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        if blocker in self.cards:
            return YouAreChallengedDecision.REVEAL_CARD
        else:
            return YouAreChallengedDecision.CONCEDE

    def do_you_block(self, action: Action, taken_by: int) -> (DoYouBlockDecision, Card):
        return (DoYouBlockDecision.BLOCK, action.blocked_by[0]) if self.block else (DoYouBlockDecision.NO_BLOCK, "")

    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        return DoYouChallengeDecision.CHALLENGE if self.challenge else DoYouChallengeDecision.ALLOW

    def do_you_challenge_block(self, action: Action, taken_by: int, target: int, block_card: Card,
                               blocker: int) -> DoYouChallengeDecision:
        return DoYouChallengeDecision.CHALLENGE if self.challenge_block else DoYouChallengeDecision.ALLOW

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
