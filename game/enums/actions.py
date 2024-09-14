import enum
from collections import namedtuple

from game.enums.cards import CAPTAIN, AMBASSADOR, ASSASSIN, CONTESSA, DUKE

# Actual game actions
class ACTION(namedtuple("ACTION", ("name", "targeted", "cost", "requires_card", "blocked_by")) ,enum.Enum):
    STEAL = "steal", True, 0, [CAPTAIN], [CAPTAIN, AMBASSADOR]
    ASSASSINATE = "assassinate", True, 3, [ASSASSIN], [CONTESSA]
    FOREIGN_AID = "foreign_aid", False, 0, [], [DUKE]
    INCOME = "income", False, 0, [], []
    TAX = "tax", False, 0, [DUKE], []
    COUP = "coup", True, 7, [], []
    AMBASSADATE = "ambassadate", False, 0, [AMBASSADOR], []

    def __str__(self):
        return self.name

def all_actions_map():
    return {a.value.name: a.value for a in ACTION}

# Extra actions, for resolving conflicts
# Challenges
CHALLENGE = "challenge"
ALLOW = "allow"

# Blocks
BLOCK = "block"
NO_BLOCK = "no_block"

# Someone challenged something
REVEAL_CARD = "show_card"
CONCEDE = "concede"
