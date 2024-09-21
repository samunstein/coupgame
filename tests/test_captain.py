import unittest
from unittest import TestCase

from game.enums.actions import Action
from game.enums.cards import Captain, Duke, Ambassador
from game.gameserver import Game
from game.messages.responses import StealDecision, Block, DoYouBlockDecision
from tests.mocks.mock_connection import get_server_mock_connection
from tests.mocks.mock_logic import MockLogic


class Methods:
    @staticmethod
    def always_captain(self: MockLogic):
        return StealDecision(self.opponents[0])


class DukeTest(TestCase, Methods):
    def test_basic_no_blocks(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 4)
        self.assertEqual(game.players[1].money, 0)

    def test_one_money(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()
        game.players[1].give_money(-1)

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 3)
        self.assertEqual(game.players[1].money, 0)

    def test_no_money(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()
        game.players[1].give_money(-2)

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 2)
        self.assertEqual(game.players[1].money, 0)

    def test_challenge(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, True, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 4)
        self.assertEqual(game.players[1].money, 0)
        self.assertEqual(len(game.players[1].cards), 1)

    def test_block(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, False, True, False)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 2)
        self.assertEqual(game.players[1].money, 2)

    def test_unsuccessful_block(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, False, True, True)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()
        game.players[1].remove_card(Captain())
        game.players[1].remove_card(Captain())
        game.players[1].give_card(Duke())
        game.players[1].give_card(Duke())

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 4)
        self.assertEqual(game.players[1].money, 0)
        self.assertEqual(len(game.players[1].cards), 1)

    def test_insta_dead(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, True, True, True)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()
        game.players[1].remove_card(Captain())
        game.players[1].remove_card(Captain())
        game.players[1].give_card(Duke())
        game.players[1].give_card(Duke())

        game.run_one_turn()
        self.assertEqual(len(game.alive_players), 1)

    def test_ambassador_block(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_captain, False, True, True)) for _ in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()
        game.players[1].remove_card(Captain())
        game.players[1].remove_card(Captain())
        game.players[1].give_card(Ambassador())
        game.players[1].give_card(Ambassador())

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 2)
        self.assertEqual(game.players[1].money, 2)
        self.assertEqual(len(game.players[0].cards), 1)

    def test_wrong_correct_card_block(self):
        class AmbassadorBlockerLogic(MockLogic):
            def do_you_block(self, action: Action, taken_by: int) -> DoYouBlockDecision:
                return Block(Ambassador())

        clients = [get_server_mock_connection(AmbassadorBlockerLogic(Methods.always_captain, False, True, True)) for _
                   in range(2)]
        game = Game(clients, deck=[Captain()] * 4)
        game.setup_players()

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 4)
        self.assertEqual(game.players[1].money, 0)
        self.assertEqual(len(game.players[1].cards), 1)


if __name__ == '__main__':
    unittest.main()
