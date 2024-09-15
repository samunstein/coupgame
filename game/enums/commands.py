# Setup things
DEBUG_MESSAGE = "debug"
SHUTDOWN = "shutdown"
ASK_NAME = "name"
ADD_OPPONENT = "add_opponent"
SET_PLAYER_NUMBER = "player_number"

# State changing actions
ADD_CARD = "add_card"
CHANGE_MONEY = "change_money"
REMOVE_CARD = "remove_card"

# Card decisions
CHOOSE_CARD_TO_KILL = "kill_any_card"
CHOOSE_AMBASSADOR_CARDS_TO_REMOVE = "choose_ambassador_cards"

# Turn flow
TAKE_TURN = "take_turn"
YOUR_ACTION_IS_CHALLENGED = "challenged"
YOUR_BLOCK_IS_CHALLENGED = "block_challenged"
DO_YOU_BLOCK = "ask_block"
DO_YOU_CHALLENGE_ACTION = "ask_challenge"
DO_YOU_CHALLENGE_BLOCK = "ask_challenge_block"

# Log of what has happened
ACTION_WAS_TAKEN = "action_taken"
ACTION_WAS_BLOCKED = "action_blocked"
ACTION_WAS_CHALLENGED = "challenge_result"
BLOCK_WAS_CHALLENGED = "block_challenge_result"
PLAYER_LOST_A_CARD = "card_dead"
A_PLAYER_IS_DEAD = "player_dead"
