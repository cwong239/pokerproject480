from player import Player as game_player
from card import Card, Suit, Rank
from handStrategy import WorstHandStrat, BestHandStrat
import random
from collections import deque

class Game:
    def __init__(self, player_count: int):
        """
        Creates a game and initalizes players with hands.
        """
        if player_count > 22 or player_count < 1:
            raise
        self.players = [game_player("player " + str(x), "800", BestHandStrat()) for x in range(player_count)]
        self.game_state = 0
        self.deck = deque([Card(rank, suit) for suit in Suit for rank in Rank])
        self.shuffle_deck()
        self.deal()
        self.player_action = ["check" for x in range(player_count)]
        self.moves = ("check", "bet", "fold")
        self.field = []

    def shuffle_deck(self) -> None:
        """
        Shuffles the deck
        """
        random.shuffle(self.deck)

    def print_deck(self) -> None:
        print("field: ")
        print(", ".join(str(card) for card in self.deck))

    def print_field(self) -> None:
        print(", ".join(str(card) for card in self.field))

    def deal(self) -> None:
        """
        Deals the starting hand out to players
        """
        for player in self.players:
            player.recievePocket(self.deck.popleft(), self.deck.popleft())
            print(player)
    
    def flop(self) -> None:
        self.burn()
        self.field.extend([self.deck.popleft() for x in range(3)])

    def turn(self) -> None:
        self.burn()
        self.field.append(self.deck.popleft())

    def river(self) -> None:
        self.burn()
        self.field.append(self.deck.popleft())

    def burn(self) -> None:
        self.deck.popleft()

g = Game(5)
g.print_deck()
g.shuffle_deck()
g.print_deck()
g.flop()
g.print_field()
g.turn()
g.print_field()
g.river()
g.print_field()

for player in g.players:
    result = player.constructHand(g.field)
    print("Player: {} created hand {} of type {}".format(player.getName(),
                                                          result[0],
                                                          result[1].name))