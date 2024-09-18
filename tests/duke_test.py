import unittest
from unittest import TestCase

from game.enums.actions import Action
from game.enums.cards import Card
from game.gameclient import PlayerClient
from game.gameserver import Game
from game.logic.clients import ClientLogic
from tests.mocks.mock_connection import get_server_mock_connection
from tests.mocks.mock_logic import MockLogic

class Methods:
    @staticmethod
    def tax_if_duke_or_fa(self: MockLogic):
        if Card.DUKE in self.cards:
            return Action.TAX, self.number
        else:
            return Action.FOREIGN_AID, self.number

    @staticmethod
    def always_fa(self: MockLogic):
        return Action.FOREIGN_AID, self.number

    @staticmethod
    def one_player_with_dukes_other_not(game):
        game.players[1].remove_card(Card.DUKE)
        game.players[1].remove_card(Card.DUKE)
        game.players[1].give_card(Card.CAPTAIN)
        game.players[1].give_card(Card.CAPTAIN)

class DukeTest(TestCase, Methods):
    def test_basic_no_blocks(self):
        clients = [get_server_mock_connection(MockLogic(Methods.tax_if_duke_or_fa, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Card.DUKE] * 4)
        game.setup_players()
        Methods.one_player_with_dukes_other_not(game)

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 5)
        game.run_one_turn()
        self.assertEqual(game.players[1].money, 4)

    def test_challenge(self):
        clients = [get_server_mock_connection(MockLogic(Methods.tax_if_duke_or_fa, True, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Card.DUKE] * 4)
        game.setup_players()
        Methods.one_player_with_dukes_other_not(game)

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 5)
        self.assertEqual(len(game.players[1].cards), 1)

    def test_block(self):
        clients = [get_server_mock_connection(MockLogic(Methods.tax_if_duke_or_fa, False, True, False)) for _ in range(2)]
        game = Game(clients, deck=[Card.CAPTAIN] * 4)
        game.setup_players()

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 2)

    def test_block_challenge(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_fa, True, True, True)) for _ in range(2)]
        game = Game(clients, deck=[Card.DUKE] * 4)
        game.setup_players()
        Methods.one_player_with_dukes_other_not(game)

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 4)
        self.assertEqual(len(game.players[1].cards), 1)

        game.run_one_turn()
        self.assertEqual(len(game.alive_players), 1)


if __name__ == '__main__':
    unittest.main()