import enum


class Card(enum.Enum):
    DUKE = "duke"
    CONTESSA = "contessa"
    ASSASSIN = "assassin"
    CAPTAIN = "captain"
    AMBASSADOR = "ambassador"

def all_cards():
    return [c.value for c in Card]