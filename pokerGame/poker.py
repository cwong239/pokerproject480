from player import Player as game_player
from card import Card, Suit, Rank
from handStrategy import BestHandStrat
from betStrategy import BigBlindCallStrat
from random import shuffle
from collections import deque
from betStrategy import BetType

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

        if len(self.current_players) < 2:
            return

        # rotate blinds
        active_players = [p for p in self.players if p.money > 0]
        self.blind_position = (self.blind_position + 1) % len(active_players)

        # blinds
        self.small_blind = {"bet": 10, "index": self.blind_position}
        self.big_blind = {"bet": 20, "index": (self.blind_position + 1) % len(active_players)}

        print(f"Small Blind: {active_players[self.small_blind['index']].getName()}")
        print(f"Big Blind: {active_players[self.big_blind['index']].getName()}")

        self.deal()
    
        self.current_turn = (self.big_blind["index"] + 1) % len(active_players)
    
    def shuffle_deck(self) -> None:
        """Shuffles the deck."""
        shuffle(self.deck)
    
    def deal(self) -> None:
        """Deals pocket cards to all active players."""
        for player, _ in self.current_players:
            player.pocket_cards.clear()  
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

        player = self.current_players[index][0]
        print(f"{player.getName()} has folded.")

        # removes player
        self.current_players.pop(index)

        # fold stuff
        if player in self.opponentFold:
            self.opponentFold[player] += 1

        # turns
        if len(self.current_players) > 0:
            self.current_turn %= len(self.current_players)  
        else:
            self.current_turn = 0  

        return player._fold()  
    
    def play_turns(self):
        """Betting Rounds"""
        if len(self.current_players) <= 1:
            return  

        print("\n--- Betting Round ---")

        self.current_bet = 0  
        self.max_bet = 0   
        players_acted = {player[0]: False for player in self.current_players}  

        while True:
            if len(self.current_players) <= 1:
                print(f"{self.current_players[0][0].getName()} wins the round!")
                return  

            player, _ = self.current_players[self.current_turn]

            if players_acted[player] and all(p.money == 0 or players_acted[p] for p, _ in self.current_players):
                break  

            # prompt
            while True:
                action = input(f"{player.getName()}, enter action (check, bet, fold): ").strip().lower()
                if action in self.moves:
                    break
                print("Invalid choice, try again.")

            if action == "fold":
                self.fold(self.current_turn)
                continue  
            elif action == "bet":
                while True:
                    try:
                        bet_amount = int(input(f"{player.getName()}, enter bet amount: "))
                        if bet_amount > player.money:
                            print("You don't have enough chips! Betting all-in instead.")
                            bet_amount = player.money
                        break
                    except ValueError:
                        print("Invalid amount. Please enter a number.")
                
                player.makeBet(1, bet_amount, self.current_bet, self.field)
                self.current_bet = bet_amount
                self.max_bet = max(self.max_bet, bet_amount)
                players_acted = {p[0]: False for p in self.current_players}  

            players_acted[player] = True
            self.current_turn = (self.current_turn + 1) % len(self.current_players)  # Rotate 

        print("\n--- Betting done ---")
    
    def prompt_player_action(self, player):
        while True:
            action = input(f"{player.getName()}, (check, bet, fold): ").strip().lower()
            if action in self.moves:
                return action
            print("invalid.")

    def showdown(self):
        """1v1 at the end"""
        if len(self.current_players) == 1:
            winner = self.current_players[0][0]
            print(f"{winner.getName()} wins.")
            return winner

        print("\n--- Showdown ---")
        
        best_player = None
        best_cards = None  
        
        for player, _ in self.current_players:
            pocket_cards = player.pocket_cards  
            print(f"{player.getName()} shows: {pocket_cards[0]}, {pocket_cards[1]}")
            
            if best_cards is None or self.compare_hands(pocket_cards, best_cards) > 0:
                best_cards = pocket_cards
                best_player = player

        print(f"\n{best_player.getName()} wins with the strongest cards.")
        return best_player

    def compare_hands(self, hand1, hand2):
 
        hand1_sorted = sorted(hand1, key=lambda card: card.rank.value, reverse=True)
        hand2_sorted = sorted(hand2, key=lambda card: card.rank.value, reverse=True)

        for card1, card2 in zip(hand1_sorted, hand2_sorted):
            if card1.rank.value > card2.rank.value:
                return 1
            elif card1.rank.value < card2.rank.value:
                return -1
        return 0  


    def play_game(self):
        """
        Plays multiple rounds of Texas Hold'em until only one player remains.
        """
        while True:
            if len([p for p in self.players if p.money > 0]) < 2:
                print("Not enough players to continue. Game Over!")
                break

            print("\n===== Starting a New Round =====")
            
            # Player Balances
            print("\n--- Player Balances ---")
            for player in self.players:
                print(f"{player.getName()} - Money: ${player.getMoney()}")

            self.reset_game()

            # Pre-flop betting round
            print("\n--- Pre-Flop Betting Round ---")
            self.play_turns()
            
            if len(self.current_players) <= 1:
                print(f"{self.current_players[0][0].getName()} wins this round!")
                continue  # Move to next round if only one player remains

            # Flop
            print("\n--- Flop ---")
            self.flop()
            self.display_field()
            self.play_turns()

            if len(self.current_players) <= 1:
                print(f"{self.current_players[0][0].getName()} wins this round!")
                continue

            # Turn
            print("\n--- Turn ---")
            self.turn()
            self.display_field()
            self.play_turns()

            if len(self.current_players) <= 1:
                print(f"{self.current_players[0][0].getName()} wins this round!")
                continue

            # River
            print("\n--- River ---")
            self.river()
            self.display_field()
            self.play_turns()

            # Determine winner if multiple players remain
            if len(self.current_players) > 1:
                self.showdown()

            input("\nPress Enter to start the next round...")


    def display_field(self):
        """displays cards"""
        print("Cards:", " ".join(str(card) for card in self.field))


# Start game session
g = Game(5)
g.play_game()


"""
Add checks for current bet so it doesn't surpass the player with the least money
    also other bets
Add small blind turn change
Add more information
Add the blind bet amounts
Showdown is just pocket cards
"""