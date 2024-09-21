import random

from config import PARAM_SPLITTER, COMMAND_END
from game.enums.actions import Action, Steal
from game.enums.cards import Card, Assassin, Ambassador
from game.logic.clients import ClientLogic
from game.messages.common import CoupMessage
from game.messages.responses import RevealCard, Concede, YouAreChallengedDecision, Block, NoBlock, DoYouBlockDecision, \
    DoYouChallengeDecision, Challenge, Allow, CardResponse, AmbassadorCardResponse, IncomeDecision, ActionDecision, \
    ForeignAidDecision, TaxDecision, StealDecision, CoupDecision, AssassinateDecision, AmbassadateDecision, Response

class CustomWrongResponse(CoupMessage):
    def serialize(self) -> str:
        return PARAM_SPLITTER.join([str(c) for c in [self.msg_name] + self.data]) + COMMAND_END

    def __init__(self, msg_name: str, data: list[object]):
        self.msg_name = msg_name
        self.data = data


class RandomLogic(ClientLogic):
    def __init__(self, wrong_chance: float = 0.25, only_one_wrong: bool = False):
        self.opponents: list[int] = []
        self.cards = []
        self.number = -1
        self.money = 0
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

    def shutdown(self):
        pass

    def ask_name(self) -> str:
        return "random"

    def add_opponent(self, number: int, name: str):
        self.opponents.append(number)

    def set_player_number(self, num: int):
        self.number = num

    def add_card(self, c: Card):
        print(self.number, "Adding", c)
        self.cards.append(c)

    def change_money(self, m: int):
        self.money += m

    def remove_card(self, c: Card):
        print(self.number, "Removing", c)
        self.cards.remove(c)

    def choose_card_to_kill(self) -> CardResponse:
        card = random.choice(self.cards)
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
            cards = [c for c in self.cards]
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
            opponent = random.choice(self.opponents)
            if self.money >= 10:
                return CoupDecision(opponent)
            else:
                return random.choice([
                    IncomeDecision(),
                    ForeignAidDecision(),
                    TaxDecision(),
                    StealDecision(opponent),
                    AmbassadateDecision(),
                ] + ([AssassinateDecision(opponent)] if self.money >= 3 else []) + ([CoupDecision(opponent)] if self.money >= 7 else []))
        else:
            return random.choice([
                StealDecision(len(self.opponents)),
                StealDecision("no"),
                CardResponse(Ambassador()),
                CoupDecision(self.number),
                CustomWrongResponse(StealDecision.message_name, [])
            ])


    def your_action_is_challenged(self, action: Action, target: int, challenger: int) -> YouAreChallengedDecision:
        if self._correct():
            if action.requires_card[0] in self.cards:
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
            if blocker in self.cards:
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
                if random.random() > 0.5 ** (1 / len(self.opponents)):
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
            if random.random() > 0.5 ** (1 / len(self.opponents)):
                return Challenge()
            else:
                return Allow()
        else:
            return IncomeDecision()

    def do_you_challenge_block(self, action: Action, taken_by: int, target: int, block_card: Card,
                               blocker: int) -> DoYouChallengeDecision:
        if self._correct():
            # 50% chance someone challenges
            if random.random() > 0.5 ** (1 / len(self.opponents)):
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

    def a_player_is_dead(self, num: int):
        if num != self.number:
            self.opponents.remove(num)

    def debug_message(self, msg: str):
        print(f"Debug: {msg}")
