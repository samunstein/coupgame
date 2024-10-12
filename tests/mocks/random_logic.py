import random

from config import PARAM_SPLITTER, COMMAND_END
from game.enums.actions import Action
from game.enums.cards import Card, Ambassador
from game.logic.clients import ClientLogic, OpponentState
from game.messages.common import CoupMessage
from game.messages.responses import RevealCard, Concede, YouAreChallengedDecision, Block, NoBlock, DoYouBlockDecision, \
    DoYouChallengeDecision, Challenge, Allow, CardResponse, AmbassadorCardResponse, IncomeDecision, ActionDecision, \
    ForeignAidDecision, TaxDecision, StealDecision, CoupDecision, AssassinateDecision, AmbassadateDecision


class CustomWrongResponse(CoupMessage):
    def serialize(self) -> str:
        return PARAM_SPLITTER.join([str(c) for c in [self.msg_name] + self.data]) + COMMAND_END

    def __init__(self, msg_name: str, data: list[object]):
        self.msg_name = msg_name
        self.data = data


class RandomLogic(ClientLogic):
    def __init__(self, wrong_chance: float = 0.25, only_one_wrong: bool = False):
        self.wrong_chance = wrong_chance
        self.only_one_wrong = only_one_wrong
        self.last_was_wrong = False

    def _correct(self):
        if self.last_was_wrong:
            self.last_was_wrong = False
            return True
        correct = random.random() > self.wrong_chance
        if not correct and self.only_one_wrong:
            self.last_was_wrong = True
        return correct

    def new_game(self):
        pass

    def shutdown(self):
        pass

    def ask_name(self) -> str:
        return "random"

    def add_opponent(self, number: int, name: str):
        pass

    def set_player_number(self, num: int):
        pass

    def add_card(self, c: Card):
        print(self.get_state().number, "Adding", c)
        pass

    def change_money(self, m: int):
        pass

    def remove_card(self, c: Card):
        print(self.get_state().number, "Removing", c)
        pass

    def choose_card_to_kill(self) -> CardResponse:
        card = random.choice(self.get_state().cards)
        if self._correct():
            return CardResponse(card)
        else:
            return random.choice([
                CardResponse(random.choice(Card.all())),
                CardResponse("no"),
                Block("no"),
                CustomWrongResponse(CardResponse.message_name, [])
            ])

    def choose_ambassador_cards_to_remove(self) -> AmbassadorCardResponse:
        if self._correct():
            cards = [c for c in self.get_state().cards]
            random.shuffle(cards)
            card1 = cards.pop()
            card2 = cards.pop()
            return AmbassadorCardResponse(card1, card2)
        else:
            return random.choice([
                AmbassadorCardResponse(random.choice(Card.all()), random.choice(Card.all())),
                AmbassadorCardResponse(1, None),
                IncomeDecision(),
                CustomWrongResponse(AmbassadorCardResponse.message_name, [Ambassador()])
            ])

    def take_turn(self) -> ActionDecision:
        if self._correct():
            opponent: OpponentState = random.choice(list(self.get_state().alive_opponents().values()))
            if self.get_state().money >= 10:
                return CoupDecision(opponent.number)
            else:
                return random.choice([
                                         IncomeDecision(),
                                         ForeignAidDecision(),
                                         TaxDecision(),
                                         StealDecision(opponent.number),
                                         AmbassadateDecision(),
                                     ] + ([AssassinateDecision(opponent.number)] if self.get_state().money >= 3 else []) + (
                                         [CoupDecision(opponent.number)] if self.get_state().money >= 7 else []))
        else:
            return random.choice([
                StealDecision(len(self.get_state().opponents)),
                StealDecision("no"),
                CardResponse(Ambassador()),
                CoupDecision(self.get_state().number),
                CustomWrongResponse(StealDecision.message_name, [])
            ])

    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if self._correct():
            if action.requires_card[0] in self.get_state().cards:
                return RevealCard()
            else:
                return Concede()
        else:
            return random.choice([
                CustomWrongResponse("nothing", [])
            ])

    def your_block_is_challenged(self, action: Action, taken_by: int, blocker: Card,
                                 challenged_by: int) -> YouAreChallengedDecision:
        if self._correct():
            if blocker in self.get_state().cards:
                return RevealCard()
            else:
                return Concede()
        else:
            return random.choice([
                CoupDecision(None),
                CustomWrongResponse("nothing", [])
            ])

    def do_you_block(self, action: Action, taken_by: int) -> DoYouBlockDecision:
        if self._correct():
            # If you are targeted, block 50% of the time. If it's not you (so basically foreign aid block by anyone),
            # use different chances
            if action.targeted:
                if random.random() > 0.5:
                    return Block(random.choice(action.blocked_by))
                else:
                    return NoBlock()
            else:
                # 50% chance someone challenges
                if random.random() > 0.5 ** (1 / len(self.get_state().opponents)):
                    return Block(random.choice(action.blocked_by))
                else:
                    return NoBlock()
        else:
            return random.choice([
                Block(4),
                CustomWrongResponse(Block.message_name, [])
            ])

    def do_you_challenge_action(self, action: Action, taken_by: int, target: int) -> DoYouChallengeDecision:
        if self._correct():
            # 50% chance someone challenges
            if random.random() > 0.5 ** (1 / len(self.get_state().opponents)):
                return Challenge()
            else:
                return Allow()
        else:
            return IncomeDecision()

    def do_you_challenge_block(self, action: Action, taken_by: int, target: int, block_card: Card,
                               blocker: int) -> DoYouChallengeDecision:
        if self._correct():
            # 50% chance someone challenges
            if random.random() > 0.5 ** (1 / len(self.get_state().opponents)):
                return Challenge()
            else:
                return Allow()
        else:
            return IncomeDecision()

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

    def a_player_violated_rules(self, num: int):
        pass

    def money_changed(self, player: int, amount: int):
        pass

    def debug_message(self, msg: str):
        print(f"Debug: {msg}")
