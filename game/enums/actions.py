import enum
from collections import namedtuple

from game.enums.cards import Card

# Actual game actions
class Action(namedtuple("ACTION", ("name", "targeted", "cost", "requires_card", "blocked_by")) , enum.Enum):
    STEAL = "steal", True, 0, [Card.CAPTAIN], [Card.CAPTAIN, Card.AMBASSADOR]
    ASSASSINATE = "assassinate", True, 3, [Card.ASSASSIN], [Card.CONTESSA]
    FOREIGN_AID = "foreign_aid", False, 0, [], [Card.DUKE]
    INCOME = "income", False, 0, [], []
    TAX = "tax", False, 0, [Card.DUKE], []
    COUP = "coup", True, 7, [], []
    AMBASSADATE = "ambassadate", False, 0, [Card.AMBASSADOR], []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

def all_actions_map():
    return {a.value.name: a.value for a in Action}

class YouAreChallengedDecision(enum.Enum):
    REVEAL_CARD = "show_card"
    CONCEDE = "concede"

    def __str__(self):
        return self.value

class DoYouChallengeDecision(enum.Enum):
    CHALLENGE = "challenge"
    ALLOW = "allow"

    def __str__(self):
        return self.value

class DoYouBlockDecision(enum.Enum):
    BLOCK = "block"
    NO_BLOCK = "no_block"

    def __str__(self):
        return self.value
