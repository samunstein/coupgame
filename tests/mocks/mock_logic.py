from game.enums.actions import Action
from game.enums.cards import Card
from game.logic.clients import ClientLogic
from game.messages.responses import RevealCard, Concede, YouAreChallengedDecision, Block, NoBlock, DoYouBlockDecision, \
    DoYouChallengeDecision, Challenge, Allow, CardResponse, AmbassadorCardResponse, ActionDecision


class MockLogic(ClientLogic):
    def __init__(self, action: lambda self: ActionDecision, challenge: bool, block: bool, challenge_block: bool):
        self.action = action
        self.challenge = challenge
        self.block = block
        self.challenge_block = challenge_block

    def new_game(self):
        pass

    def shutdown(self):
        pass

    def ask_name(self) -> str:
        return "mock"

    def add_opponent(self, number: int, name: str):
        pass

    def set_player_number(self, num: int):
        pass

    def add_card(self, c: Card):
        print("Adding", c)
        pass

    def change_money(self, m: int):
        pass

    def remove_card(self, c: Card):
        pass

    def choose_card_to_kill(self) -> CardResponse:
        return CardResponse(self.get_state().cards[-1])

    def choose_ambassador_cards_to_remove(self) -> AmbassadorCardResponse:
        return AmbassadorCardResponse(self.get_state().cards[0], self.get_state().cards[1])

    def take_turn(self) -> ActionDecision:
        return self.action(self)

    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if action.requires_card[0] in self.get_state().cards:
            return RevealCard()
        else:
            return Concede()

    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        if blocker in self.get_state().cards:
            return RevealCard()
        else:
            return Concede()

    def do_you_block(self, action: Action, taken_by: int) -> DoYouBlockDecision:
        have_block_card = set(self.get_state().cards).intersection(set(action.blocked_by))
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

    def money_changed(self, player: int, amount: int):
        pass

    def a_player_violated_rules(self, num: int):
        pass

    def debug_message(self, msg: str):
        print(f"Debug: {msg}")
