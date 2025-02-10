from player import Player as game_player
from card import Card, Suit, Rank
from handStrategy import BestHandStrat
from betStrategy import BigBlindCallStrat
from random import shuffle
from collections import deque

class Game:
    def __init__(self, player_count: int):
        """
        Creates a game and initalizes players with hands.
        """
        if player_count > 22 or player_count < 1:
            raise
        self.players = [game_player("player " + str(x), 800, 
                                    BestHandStrat(), BigBlindCallStrat()) 
                        for x in range(player_count)]
        self.game_state = 0
        self.deck = deque([Card(rank, suit) for suit in Suit for rank in Rank])
        self.shuffle_deck()
        self.deal()
        self.player_action = ["check" for x in range(player_count)]
        self.moves = ("check", "bet", "fold")
        self.field = []
        self.current_players = []
        self.reset_current_players()
        self.current_bet = self.current_turn = self.total_pot = self.current_pot = self.max_bet = 0

        self.big_blind = {"bet": 0, "index": 1}
        self.small_blind = {"bet": 0, "index": 0}

    def shuffle_deck(self) -> None:
        """
        Shuffles the deck
        """
        shuffle(self.deck)

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

    def reset_current_players(self) -> None:
        self.current_players = [(player, 0) for player in self.players]

    def fold(self, index) -> None:
        self.current_players.pop(index)

    def loss(self, remove_players: list[int]) -> None:
        reversed_sorted = sorted(remove_players, key=lambda x: x, reverse=True)
        for player in reversed_sorted:
            self.players.pop(player)

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

# example betting
for player in g.players:
    result = player.makeBet(1, 10, g.field)
    print("Player: {} does a {} of {}".format(player.getName(), 
                                              result[0].name, 
                                              result[1]))

# example hand construction
for player in g.players:
    result = player.constructHand(g.field)
    print("Player: {} created hand {} of type {}".format(player.getName(),
                                                          result[0],
                                                          result[1].name))
