from common.common import debug_print
from config import PARAM_SPLITTER, CONTROL_CHAR_REPLACE, COMMAND_END
from connection.common import Connection
from game.messages.commands import *
from game.logic.clients import ClientLogic
from game.messages.responses import *


class PlayerClient:
    def __init__(self, connection: Connection, logic: ClientLogic):
        self.connection = connection
        self.logic = logic
        self.running = True

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
            self.logic.add_opponent(command.number, command.player_name)
        elif isinstance(command, SetPlayerNumber):
            self.logic.set_player_number(command.number)

        # State changes
        elif isinstance(command, AddCard):
            self.logic.add_card(command.card)
        elif isinstance(command, ChangeMoney):
            self.logic.change_money(command.number)
        elif isinstance(command, RemoveCard):
            self.logic.remove_card(command.card)
        elif isinstance(command, PlayerLostACard):
            self.logic.player_lost_a_card(command.player, command.card)
        elif isinstance(command, PlayerIsDead):
            self.logic.a_player_is_dead(command.number)

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
            return self.logic.your_block_is_challenged(command.action, command.action_doer, command.block_card, command.challenger)
        elif isinstance(command, DoYouBlock):
            return self.logic.do_you_block(command.action, command.action_doer)
        elif isinstance(command, DoYouChallengeAction):
            return self.logic.do_you_challenge_action(command.action, command.action_doer, command.target)
        elif isinstance(command, DoYouChallengeBlock):
            return self.logic.do_you_challenge_block(command.action, command.action_doer, command.target, command.block_card, command.blocked_by)

        # Log
        elif isinstance(command, ActionWasTaken):
            self.logic.action_was_taken(command.action, command.action_doer, command.target)
        elif isinstance(command, ActionWasBlocked):
            self.logic.action_was_blocked(command.action, command.action_doer, command.target, command.block_card, command.blocked_by)
        elif isinstance(command, ActionWasChallenged):
            self.logic.action_was_challenged(command.action, command.action_doer, command.target, command.challenger, command.success)
        elif isinstance(command, BlockWasChallenged):
            self.logic.block_was_challenged(command.action, command.action_taker, command.target, command.block_card, command.blocked_by, command.challenger, command.success)
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
