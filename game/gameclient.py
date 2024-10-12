from dataclasses import dataclass

from common.common import debug_print
from config import PARAM_SPLITTER, CONTROL_CHAR_REPLACE, COMMAND_END, START_MONEY, START_CARDS_AMOUNT
from connection.common import Connection
from game.logic.clients import ClientLogic, OpponentState, ClientState
from game.messages.commands import *
from game.messages.responses import *


@dataclass
class MutableOpponentState:
    money: int
    cards_amount: int
    dead_cards: list[Card]
    number: int
    name: str

    def reset(self):
        self.money = START_MONEY
        self.cards_amount = START_CARDS_AMOUNT
        self.dead_cards = []

    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name
        self.reset()


class PlayerClient:
    def __init__(self, connection: Connection, logic: ClientLogic):
        self.connection: Connection = connection
        self.logic: ClientLogic = logic
        self.running: bool = True

        # Public and own state
        self.opponents: dict[int, MutableOpponentState] = {}
        self.dead_cards: list[Card] = []
        self.cards: list[Card] = []
        self.money: int = 0
        self.number: int = -1

        self.logic.set_state_fetch_function(self.get_client_state)

    def get_client_state(self) -> ClientState:
        opponents = {opp.number: OpponentState(opp.number, opp.cards_amount, opp.dead_cards, opp.money) for opp in
                     self.opponents.values()}
        return ClientState(self.number, self.cards, self.dead_cards, self.money, opponents)

    def reset_state(self):
        self.cards = []
        self.money = 0
        self.dead_cards = []

    def run_command(self, command: Command) -> Response | None:
        # Setup and meta
        if isinstance(command, DebugMessage):
            debug_print(command.message)
        elif isinstance(command, Shutdown):
            self.connection.close()
            self.logic.shutdown()
            self.running = False
        elif isinstance(command, AskName):
            return NameResponse(self.logic.ask_name()
                                .replace(PARAM_SPLITTER, CONTROL_CHAR_REPLACE)
                                .replace(COMMAND_END, CONTROL_CHAR_REPLACE))
        elif isinstance(command, AddOpponent):
            self.opponents[command.number] = MutableOpponentState(command.number, command.player_name)
            self.logic.add_opponent(command.number, command.player_name)
        elif isinstance(command, SetPlayerNumber):
            self.number = command.number
            self.logic.set_player_number(command.number)
        elif isinstance(command, NewGame):
            self.reset_state()
            self.logic.new_game()

        # State changes
        elif isinstance(command, AddCard):
            self.cards.append(command.card)
            self.logic.add_card(command.card)
        elif isinstance(command, ChangeMoney):
            self.money += command.amount
            self.logic.change_money(command.amount)
        elif isinstance(command, RemoveCard):
            self.cards.remove(command.card)
            self.logic.remove_card(command.card)
        elif isinstance(command, PlayerLostACard):
            if command.player in self.opponents:
                opp = self.opponents[command.player]
                opp.cards_amount -= 1
                opp.dead_cards.append(command.card)
            self.logic.player_lost_a_card(command.player, command.card)
        elif isinstance(command, MoneyChanged):
            if command.player in self.opponents:
                self.opponents[command.player].money += command.amount
            self.logic.money_changed(command.player, command.amount)
        elif isinstance(command, PlayerViolatedRules):
            if command.number in self.opponents:
                self.opponents.pop(command.number)
            self.logic.a_player_violated_rules(command.number)

        # Card decisions
        elif isinstance(command, ChooseCardToKill):
            return self.logic.choose_card_to_kill()
        elif isinstance(command, ChooseAmbassadorCardsToRemove):
            return self.logic.choose_ambassador_cards_to_remove()

        # Turn flow
        elif isinstance(command, TakeTurn):
            return self.logic.take_turn()
        elif isinstance(command, YourActionIsChallenged):
            return self.logic.your_action_is_challenged(command.action, command.target, command.challenger)
        elif isinstance(command, YourBlockIsChallenged):
            return self.logic.your_block_is_challenged(command.action, command.action_doer, command.block_card,
                                                       command.challenger)
        elif isinstance(command, DoYouBlock):
            return self.logic.do_you_block(command.action, command.action_doer)
        elif isinstance(command, DoYouChallengeAction):
            return self.logic.do_you_challenge_action(command.action, command.action_doer, command.target)
        elif isinstance(command, DoYouChallengeBlock):
            return self.logic.do_you_challenge_block(command.action, command.action_doer, command.target,
                                                     command.block_card, command.blocked_by)

        # Log
        elif isinstance(command, ActionWasTaken):
            self.logic.action_was_taken(command.action, command.action_doer, command.target)
        elif isinstance(command, ActionWasBlocked):
            self.logic.action_was_blocked(command.action, command.action_doer, command.target, command.block_card,
                                          command.blocked_by)
        elif isinstance(command, ActionWasChallenged):
            self.logic.action_was_challenged(command.action, command.action_doer, command.target, command.challenger,
                                             command.success)
        elif isinstance(command, BlockWasChallenged):
            self.logic.block_was_challenged(command.action, command.action_taker, command.target, command.block_card,
                                            command.blocked_by, command.challenger, command.success)
        else:
            print("Unknown command", command)

    def run(self):
        while self.running:
            data = self.connection.receive()
            debug_print(f"# RAW DATA RECEIVED: {data}")
            if not len(data):
                break

            commands = [c for c in data.split(COMMAND_END) if c]

            for serialized_command in commands:
                command = Command.deserialize(serialized_command)
                response = self.run_command(command)
                if response is not None:
                    self.connection.send(response)
