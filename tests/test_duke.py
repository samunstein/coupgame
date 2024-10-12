import unittest
from unittest import TestCase

from game.enums.cards import Duke, Captain
from game.gameserver import Game
from game.messages.responses import TaxDecision, ForeignAidDecision
from tests.mocks.mock_connection import get_server_mock_connection
from tests.mocks.mock_logic import MockLogic


class Methods:
    @staticmethod
    def tax_if_duke_or_fa(self: MockLogic):
        if Duke() in self.get_state().cards:
            return TaxDecision()
        else:
            return ForeignAidDecision()

    @staticmethod
    def always_fa(self: MockLogic):
        return ForeignAidDecision()

    @staticmethod
    def one_player_with_dukes_other_not(game):
        game.rule_abiding_players[1].remove_card(Duke())
        game.rule_abiding_players[1].remove_card(Duke())
        game.rule_abiding_players[1].give_card(Captain())
        game.rule_abiding_players[1].give_card(Captain())


class DukeTest(TestCase, Methods):
    def test_basic_no_blocks(self):
        clients = [get_server_mock_connection(MockLogic(Methods.tax_if_duke_or_fa, False, False, False)) for _ in
                   range(2)]
        game = Game(clients, deck=[Duke()] * 4)
        game.setup_players()
        Methods.one_player_with_dukes_other_not(game)

        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[0].money, 5)
        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[1].money, 4)

    def test_challenge(self):
        clients = [get_server_mock_connection(MockLogic(Methods.tax_if_duke_or_fa, True, False, False)) for _ in
                   range(2)]
        game = Game(clients, deck=[Duke()] * 4)
        game.setup_players()
        Methods.one_player_with_dukes_other_not(game)

        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[0].money, 5)
        self.assertEqual(len(game.rule_abiding_players[1].cards), 1)

    def test_block(self):
        clients = [get_server_mock_connection(MockLogic(Methods.tax_if_duke_or_fa, False, True, False)) for _ in
                   range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()

        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[0].money, 2)

    def test_block_challenge(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_fa, True, True, True)) for _ in range(2)]
        game = Game(clients, deck=[Duke()] * 4)
        game.setup_players()
        Methods.one_player_with_dukes_other_not(game)

        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[0].money, 4)
        self.assertEqual(len(game.rule_abiding_players[1].cards), 1)

        game.run_one_turn()
        self.assertEqual(len(game.alive_players), 1)


if __name__ == '__main__':
    unittest.main()
