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
    def assassinate_if_money(self: MockLogic):
        if self.money >= 3:
            return Action.ASSASSINATE, self.opponents[0]
        else:
            return Action.INCOME, self.number

class AssassinTest(TestCase, Methods):
    def test_basic_no_blocks(self):
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, False, False)) for _ in range(2)]
        game = Game(clients)
        game.setup_players()

        self.assertEqual(game.players[0].money, 2)
        self.assertEqual(game.players[1].money, 2)

        self.assertEqual(len(game.players[0].cards), 2)
        self.assertEqual(len(game.players[1].cards), 2)

        game.run_one_turn()

        self.assertEqual(game.players[0].money, 3)
        self.assertEqual(game.players[1].money, 2)

        game.run_one_turn()

        self.assertEqual(game.players[0].money, 3)
        self.assertEqual(game.players[1].money, 3)

        game.run_one_turn()

        self.assertEqual(game.players[0].money, 0)
        self.assertEqual(len(game.players[1].cards), 1)

    def test_challenge_no_block(self):
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, True, False)) for _ in range(2)]
        game = Game(clients, deck=[Card.CONTESSA] * 4)
        game.setup_players()
        game.players[0].give_money(1)
        game.players[1].give_money(1)
        game.players[1].give_card(Card.ASSASSIN)
        game.players[1].remove_card(Card.CONTESSA)
        # Leaves the second player with contessa and assassin

        game.run_one_turn()

        # First player was rightfully challenged and lost a card but no money
        self.assertEqual(game.players[0].money, 3)
        self.assertEqual(len(game.players[1].cards), 2)
        self.assertEqual(len(game.players[0].cards), 1)

        game.run_one_turn()
        # Second player was wrongfully challenged, and the first player lost a card and died. The deck is empty, but
        # the assassin in the second player's hand gets first returned and then given back.
        self.assertEqual(len(game.alive_players), 1)
        self.assertEqual(game.alive_players[0].number, 1)
        self.assertEqual(game.alive_players[0].money, 3)
        self.assertEqual(game.alive_players[0].cards, [Card.CONTESSA, Card.ASSASSIN])

    def test_insta_die(self):
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, True, False)) for _ in range(2)]
        game = Game(clients, deck=[Card.ASSASSIN] * 5)
        game.setup_players()
        game.players[0].give_money(1)

        game.run_one_turn()
        self.assertEqual(len(game.alive_players), 1)
        self.assertEqual(game.alive_players[0].number, 0)
        self.assertEqual(game.alive_players[0].money, 0)

if __name__ == '__main__':
    unittest.main()