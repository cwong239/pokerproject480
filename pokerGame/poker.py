from player import Player as game_player
from card import Card, Suit, Rank
from handStrategy import BestHandStrat
from betStrategy import BigBlindCallStrat, ArguablyOptimalStrat
from random import shuffle
from collections import deque
from betStrategy import BetType
from handBuilder import HandVal

class Game:
    def __init__(self, player_count: int, bot_count=0):
        """
        Creates a game and initializes players with hands.
        """

        """
        game_state: used to tell what state the game is in
            0: preflop
            1: flop
            2: turn
            3: river
        blind_position: position of the big blind I think
        opponentFold: players that have folded in a give round
        players: players that are in a game
        rounds: idk may be useful for integration to keep track of stuff
            not currently doing anything
        """

        if player_count > 22 or player_count < 1:
            raise ValueError("Player count must be between 1 and 22")
        
        self.players = [game_player("player " + str(x), 800, BestHandStrat(), BigBlindCallStrat()) for x in range(player_count)]
        self.players += [game_player("player " + str(x), 800, BestHandStrat(), BigBlindCallStrat(), is_agent=True) for x in range(player_count, player_count+bot_count)]
        # set the players to agents somewhere here by setting "player".is_agent to True
        self.game_state = 0
        self.moves = ("check", "bet", "fold")
        self.blind_position = 0
        self.opponentFold = {player: 0.0 for player in self.players}
        self.rounds = 0
        #self.reset_game()
        
    def reset_game(self):
        """
        Resets the game state for a new round while keeping player balances.
        """

        """
        deck: the cards in the deck
        field: the cards from the deck that are currently on the field
        current_players: the players that are in the current round
        current_bet: the bet amount that a player needs to exceed to make a bet / the check amount
        max_bet: the max amount of money the poorest player has
            used to avoid split pot logic
        big_blind_amount: i think this and the next are self explanatory
        small_blind_amount
        """
        self.deck = deque([Card(rank, suit) for suit in Suit for rank in Rank])
        self.shuffle_deck()
        self.field = []
        self.current_players = [player for player in self.players if player.money > 0]
        self.current_bet = self.current_turn = self.total_pot = self.current_pot = self.game_state = 0
        self.max_bet = min(player.getMoney() for player in self.players) # the max bet a player can make is the maximum amount of money the poorest player has
        self.big_blind_amount = 20
        self.small_blind_amount = 10
        
        if len(self.current_players) < 2:
            return

        # rotate blinds
        active_players = [p for p in self.players if p.money > 0] 
        # ^ players currently active in a round I'm assuming?
        self.blind_position = (self.blind_position + 1) % len(active_players)

        # blind logic
        self.small_blind = {"bet": self.small_blind_amount, "index": self.blind_position}
        self.big_blind = {"bet": self.big_blind_amount, "index": (self.blind_position + 1) % len(active_players)}
        self.sb_player = active_players[self.small_blind['index']]
        self.bb_player = active_players[self.big_blind['index']]

        print(f"Small Blind: {self.sb_player.getName()}")
        print(f"Big Blind: {self.bb_player.getName()}")

        sb_bet_amount = self.sb_player.getMoney()
        if not self.sb_player.makeBetManual(self.small_blind_amount):
            # if the sb doesn't have enough money, it is considered an "all in"
            self.current_bet = sb_bet_amount
            self.sb_player.makeBetManual(sb_bet_amount)
            self.current_pot+= sb_bet_amount
        else:
            self.current_pot+=self.small_blind_amount
            self.current_bet = self.small_blind_amount

        bb_bet_amount = self.bb_player.getMoney()
        if not self.bb_player.makeBetManual(self.big_blind_amount):
            # if the bb doesn't have enough money, it is considered an "all in"
            if bb_bet_amount>self.current_bet:
                self.current_bet = bb_bet_amount
            self.bb_player.makeBetManual(bb_bet_amount)
            self.current_pot+= bb_bet_amount
        else:
            self.current_pot+= self.big_blind_amount
            self.current_bet = self.big_blind_amount

        # setting the stage
        self.deal()
    
        self.current_turn = (self.big_blind["index"] + 1) % len(active_players)
    
    def shuffle_deck(self) -> None:
        """Shuffles the deck."""
        shuffle(self.deck)
    
    def deal(self) -> None:
        """Deals pocket cards to all active players."""
        for player in self.current_players:
            player.pocket_cards.clear()  
            player.recievePocket(self.deck.popleft(), self.deck.popleft())
    
    def flop(self) -> None:
        self.burn()
        self.current_bet = 0
        self.field.extend([self.deck.popleft() for _ in range(3)])
        self.game_state = 1
        self.current_turn = self.blind_position
    
    def turn(self) -> None:
        self.burn()
        self.current_bet = 0
        self.field.append(self.deck.popleft())
        self.game_state = 2
        self.current_turn = self.blind_position
    
    def river(self) -> None:
        self.current_bet = 0
        self.burn()
        self.field.append(self.deck.popleft())
        self.game_state = 3
        self.current_turn = self.blind_position
    
    def burn(self) -> None:
        self.deck.popleft()
    
    def fold(self, index):

        player = self.current_players[index]
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
    
    def add_to_pot(self, money):
        self.current_pot+=money

    def play_turns(self):
        """Betting Rounds"""

        if self.game_state == 0:
            self.current_turn = (self.blind_position + 2) % len(self.current_players)
        else:
            self.current_turn = self.blind_position

        if len(self.current_players) <= 1:
            return  

        print("\n--- Betting Round ---")

        players_acted = {player: False for player in self.current_players}  

        while True:

            if len(self.current_players) <= 1:
                print(f"{self.current_players[0].getName()} wins the round!")

                self.total_pot+=self.current_pot
                self.current_players[0].money += self.total_pot
                for player in self.current_players:
                    player.clearBet()
                return  

            player = self.current_players[self.current_turn]

            if players_acted[player] and all(p.money == 0 or players_acted[p] for p in self.current_players):
                for player in self.current_players:
                    player.clearBet()
                break  

            # more info in the round
            print(f"The total pot is: ${self.total_pot}.")
            print(f"The current pot is: ${self.current_pot}.")
            print(f"The current bet is : ${self.current_bet}.")
            print(f"The max bet is : ${self.max_bet}.")

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
                        # checks if the bet is more than player money, if so go all in
                        if bet_amount > player.money:
                            print("You don't have enough chips! Using all your money for checks instead.")
                            bet_amount = player.money
                        # checks if bet is more than current bet
                            # this one is currenlt broken and needs fixing, I put comments below
                        if bet_amount < self.current_bet:
                            print("Your bet is not high enough, please try again.")
                        # checks for the max bet
                        elif bet_amount > self.max_bet:
                            print("Your bet amount exceeds the max bet amount, please try again.")
                        else:
                            print(f"Your bet amount of ${bet_amount} was accepted.")
                            break
                    except ValueError:
                        print("Invalid amount. Please enter a number.")
                
                # different betting method if it is an agent
                if player.is_agent:
                    player.makeBet(1, bet_amount, self.current_bet, self.field)
                    # idk how u wanna implement this wiht the pot stuff
                # player uses manual bets
                else:
                    player.makeBetManual(bet_amount)
                    self.add_to_pot(bet_amount)

                self.current_bet = bet_amount # broken, need to change how this works
                self.max_bet = min(player.getMoney() for player in self.players)
                players_acted = {p: False for p in self.current_players}  
            elif action == "check":
                # note that it should never occur that the player cannot check since 
                # it should always check for the least amount of money
                self.check(player) # need to change how current_bet works

            players_acted[player] = True
            self.current_turn = (self.current_turn + 1) % len(self.current_players)  # Rotate 

        print("\n--- Betting done ---")

        for player in self.players:
            print(f"{player.getName()} - Money: ${player.getMoney()}")

        self.total_pot+=self.current_pot
        self.current_pot = 0 # reset current pot for new round
        self.current_bet = 0
    
    def check(self, player):
        self.current_pot += self.current_bet - player.bet
        if self.current_bet - player.bet == 0:
            out = 0
        else:
            out = self.current_bet - player.bet
        player.makeBetManual(self.current_bet - player.bet)
        return out
        

    def prompt_player_action(self, player):
        while True:
            action = input(f"{player.getName()}, (check, bet, fold): ").strip().lower()
            if action in self.moves:
                return action
            print("invalid.")

    def showdown(self) -> list[game_player]:
        """
        All players still in the game compare their best hand, player(s) with 
        best hand wins
        
        If multiple players have the exact same hand (playing the board) 
        then the pot is split between all remaining players
        """
        if len(self.current_players) == 1:
            winner = self.current_players[0]
            print(f"{winner.getName()} wins. Only player left")
            return [winner]

        print("\n--- Showdown ---")
        
        hands = {}
        
        # Get the player(s) associated with each hand
        for player in self.current_players:
            pocket_cards = player.pocket_cards  
            print(f"{player.getName()} shows: {pocket_cards[0]}, {pocket_cards[1]}")
            
            result = player.constructHand(self.field)
            # convert list->tuple so hand can be a dictionary key
            player_hand = (tuple(result[0]), result[1]) 
            print("{} shows: {}, {}, {}, {}, {}".format(player.getName(), 
                                                        player_hand[0][0], 
                                                        player_hand[0][1], 
                                                        player_hand[0][2], 
                                                        player_hand[0][3], 
                                                        player_hand[0][4]))

            if hands.get(player_hand) is not None:
                hands.get(player_hand).append(player)
            else:
                hands[player_hand] = [player]

        # Find the highest hand type (ex: Flush)
        best_value = 0
        for hand in hands.keys():
            if hand[1].value > best_value:
                best_value = hand[1].value
        
        # Get all hands of the highest type (ex: all Flushes)
        best_hands = []
        for hand in hands.keys():
            if hand[1].value == best_value:
                best_hands.append(hand)
        
        # Get the hand with the highest cards (ex: royal flush vs Q-8 Straight Flush)
        highest_hand = ((Card(Rank.TWO, Suit.SPADE),
                         Card(Rank.TWO, Suit.SPADE),
                         Card(Rank.TWO, Suit.SPADE),
                         Card(Rank.TWO, Suit.SPADE),
                         Card(Rank.TWO, Suit.SPADE)), 
                        HandVal.NO_HAND)
        for hand in best_hands:
            if hand[0] > highest_hand[0]:
                highest_hand = hand
        
        # get player(s) associated with the highest hand
        winners : list[game_player] = hands.get(highest_hand)
        print("There are {} winners:".format(len(winners)))
        for best_player in winners:
            print("\n{} wins with the strongest cards.".format(best_player.getName()))
        
        return winners

    def compare_hands(self, hand1, hand2):
        # should be replaced entirely
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

            self.reset_game()
            
            # Player Balances
            print("\n--- Player Balances ---")
            for player in self.players:
                print(f"{player.getName()} - Money: ${player.getMoney()}")

            # Pre-flop betting round
            print("\n--- Pre-Flop Betting Round ---")
            self.play_turns()
            
            if len(self.current_players) <= 1:
                print(f"{self.current_players[0].getName()} wins this round!")
                continue  # Move to next round if only one player remains

            # Flop
            print("\n--- Flop ---")
            self.flop()
            self.display_field()
            self.play_turns()

            if len(self.current_players) <= 1:
                print(f"{self.current_players[0].getName()} wins this round!")
                continue

            # Turn
            print("\n--- Turn ---")
            self.turn()
            self.display_field()
            self.play_turns()

            if len(self.current_players) <= 1:
                print(f"{self.current_players[0].getName()} wins this round!")
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
#g = Game(5)
#g.play_game()


"""Showdown is just pocket cards"""
