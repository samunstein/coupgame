import unittest
from unittest import TestCase

from game.gameserver import Game
from tests.mocks.mock_connection import get_server_mock_connection
from tests.mocks.random_logic import RandomLogic


class RandomTest(TestCase):
    def test_random_clients(self):
        # If the game runs many times without rule violations, it is good
        for _ in range(500):
            clients = [get_server_mock_connection(RandomLogic(0)) for _ in range(2)]
            game = Game(clients, crash_on_violation=True)
            game.setup_players()

            while len(game.alive_players) > 1:
                game.run_one_turn()

    def test_incorrect_clients(self):
        # The clients do rule violations, but the game should not crash
        for _ in range(500):
            clients = [get_server_mock_connection(RandomLogic(0.2)) for _ in range(2)]
            game = Game(clients, crash_on_violation=False)
            game.setup_players()

            while len(game.alive_players) > 1:
                game.run_one_turn()

    def test_that_single_violations_are_ok(self):
        # The clients do rule violations, but only one at a time
        for _ in range(500):
            clients = [get_server_mock_connection(RandomLogic(0.2, only_one_wrong=True)) for _ in range(2)]
            game = Game(clients, crash_on_violation=True)
            game.setup_players()

            while len(game.alive_players) > 1:
                game.run_one_turn()

    def test_more_than_two_players(self):
        # If the game runs many times without rule violations, it is good
        for _ in range(500):
            clients = [get_server_mock_connection(RandomLogic(0)) for _ in range(4)]
            game = Game(clients, crash_on_violation=True)
            game.setup_players()

            while len(game.alive_players) > 1:
                game.run_one_turn()


if __name__ == '__main__':
    unittest.main()
