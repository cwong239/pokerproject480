from player import Player as game_player
from card import Card, Suit, Rank
from handStrategy import BestHandStrat
from betStrategy import BigBlindCallStrat
from random import shuffle
from collections import deque

class Game:
    def __init__(self, player_count: int):
        """
        Creates a game and initializes players with hands.
        """
        if player_count > 22 or player_count < 1:
            raise ValueError("Player count must be between 1 and 22")
        
        self.players = [game_player("player " + str(x), 800, 
                                    BestHandStrat(), BigBlindCallStrat()) 
                        for x in range(player_count)]
        self.game_state = 0
        self.moves = ("check", "bet", "fold")
        self.blind_position = 0
        self.opponentFold = {player: 0.0 for player in self.players}
        self.rounds = 0
        self.reset_game()
    
    def reset_game(self):
        """
        Resets the game state for a new round while keeping player balances.
        """
        self.deck = deque([Card(rank, suit) for suit in Suit for rank in Rank])
        self.shuffle_deck()
        self.field = []
        self.current_players = [(player, 0) for player in self.players if player.money > 0]
        self.current_bet = self.current_turn = self.total_pot = self.current_pot = self.max_bet = 0
        
        # Rotate blinds
        self.small_blind = {"bet": 0, "index": self.blind_position % len(self.players)}
        self.big_blind = {"bet": 0, "index": (self.blind_position + 1) % len(self.players)}
        self.blind_position = (self.blind_position + 1) % len(self.players)
        
        # Set the starting turn to the big blind player
        self.current_turn = self.big_blind["index"]
        
        self.deal()
    
    def shuffle_deck(self) -> None:
        """Shuffles the deck."""
        shuffle(self.deck)
    
    def deal(self) -> None:
        """Deals the starting hand out to players."""
        for player in self.players:
            if player.money > 0:
                player.recievePocket(self.deck.popleft(), self.deck.popleft())
    
    def flop(self) -> None:
        self.burn()
        self.field.extend([self.deck.popleft() for _ in range(3)])
    
    def turn(self) -> None:
        self.burn()
        self.field.append(self.deck.popleft())
    
    def river(self) -> None:
        self.burn()
        self.field.append(self.deck.popleft())
    
    def burn(self) -> None:
        self.deck.popleft()
    
    def fold(self, index):
        print(f"{self.current_players[index][0].getName()} has folded.")
        player = self.current_players[index][0]
        self.current_players.pop(index)
        if player in self.opponentFold:
            self.opponentFold[player] += 1 
        self.current_turn %= len(self.current_players) if self.current_players else 0
    
    def play_turns(self):
        while len(self.current_players) > 1:
            player, _ = self.current_players[self.current_turn]
            action = self.prompt_player_action(player)

            if action == "fold":
                self.fold(self.current_turn)
            elif action == "bet":
                bet_amount = int(input(f"{player.getName()}, enter bet amount: "))
                player.makeBet(1, bet_amount, self.field)
                self.current_bet = bet_amount
            
            self.current_turn = (self.current_turn + 1) % len(self.current_players)
            
            if len(self.current_players) == 1:
                print(f"{self.current_players[0][0].getName()} wins the round!")
                break
    
    def prompt_player_action(self, player):
        while True:
            action = input(f"{player.getName()}, (check, bet, fold): ").strip().lower()
            if action in self.moves:
                return action
            print("Invalid choice, try again.")
    
    def play_game(self):
        """
        Plays multiple games until the user inputs 'END'.
        """
        while True:
            print("Starting a new game!")
            self.reset_game()
            self.flop()
            self.turn()
            self.river()
            self.play_turns()
            
            if input("Type 'END' to stop playing or press Enter to continue: ").strip().upper() == "END":
                print("Ending game session.")
                break

# Start game session
g = Game(5)
g.play_game()
