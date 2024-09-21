import unittest
from unittest import TestCase

from game.enums.actions import Action
from game.enums.cards import Card, Contessa
from game.gameserver import Game
from game.messages.responses import ForeignAidDecision, CoupDecision
from tests.mocks.mock_connection import get_server_mock_connection
from tests.mocks.mock_logic import MockLogic


class Methods:
    @staticmethod
    def coup_or_fa(self: MockLogic):
        if self.money < 7:
            return ForeignAidDecision()
        else:
            return CoupDecision(self.opponents[0])

    @staticmethod
    def always_fa(self: MockLogic):
        return ForeignAidDecision()

    @staticmethod
    def always_coup(self: MockLogic):
        return CoupDecision(self.opponents[0])

    @staticmethod
    def coup_self(self: MockLogic):
        return CoupDecision(self.number)

class CoupTest(TestCase, Methods):
    def test_basic(self):
        clients = [get_server_mock_connection(MockLogic(Methods.coup_or_fa, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Contessa()] * 4)
        game.setup_players()
        game.players[0].give_money(4)
        game.run_one_turn()
        self.assertEqual(game.players[0].money, 8)
        game.run_one_turn()
        game.run_one_turn()
        self.assertEqual(game.players[0].money, 1)
        self.assertEqual(len(game.players[1].cards), 1)

    def test_die_if_no_money(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_coup, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Contessa()] * 4)
        game.setup_players()
        game.run_one_turn()
        self.assertEqual(game.players[0].cards, [])
        self.assertEqual(len(game.alive_players), 1)

    def test_die_if_not_forced_coup(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_fa, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Contessa()] * 4)
        game.setup_players()
        game.players[0].give_money(8)
        game.run_one_turn()
        self.assertEqual(game.players[0].cards, [])
        self.assertEqual(len(game.alive_players), 1)

    def test_die_if_self_target(self):
        clients = [get_server_mock_connection(MockLogic(Methods.coup_self, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Contessa()] * 4)
        game.setup_players()
        game.players[0].give_money(8)
        game.run_one_turn()
        self.assertEqual(game.players[0].cards, [])
        self.assertEqual(len(game.alive_players), 1)



if __name__ == '__main__':
    unittest.main()