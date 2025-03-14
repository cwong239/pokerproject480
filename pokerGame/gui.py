import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from poker import Game  # Assuming your game class is in game.py
from player import Player
from betStrategy import BetType
import time

class PokerGUI:
    def __init__(self, root, player_count=1, bot_count=2):
        self.root = root
        self.root.title("Poker Game")
        
        self.game = Game(player_count, bot_count)
        self.winner = tk.StringVar()

        self.game.reset_game()
        self.real_player = self.game.players[0]
        self.players_acted = {player: False for player in self.game.current_players} 

        self.create_widgets()
        self.log(f"\nSmall Blind: {self.game.sb_player.getName()}")
        self.log(f"Big Blind: {self.game.bb_player.getName()}\n")
        self.update_display()
        self.play()


    def create_widgets(self):
        self.info_label = tk.Label(self.root, text="Poker Game", font=("Arial", 16))
        self.info_label.pack()

        self.winner_label = tk.Label(self.root, textvariable=self.winner)
        self.winner_label.pack()
        
        # Community Cards Display (no longer needed for text)
        self.community_cards_label = tk.Label(self.root, text="Community Cards:")
        self.community_cards_label.pack()

        # Frame for community cards images
        self.community_cards_frame = tk.Frame(self.root)
        self.community_cards_frame.pack()

        # Player Display
        self.players_frame = tk.Frame(self.root)
        self.players_frame.pack()
        self.player_labels = []
        for player in self.game.players:
            label = tk.Label(self.players_frame, text=f"{player.getName()} - ${player.getMoney()}")
            label.pack()
            self.player_labels.append(label)

        self.pot_frame = tk.Frame(self.root)
        self.pot_frame.pack()
        self.pot_label = tk.Label(self.pot_frame, text=f"Pot - {self.game.current_pot}")
        self.pot_label.pack()
        
        # Action Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()
        self.check_button = tk.Button(self.button_frame, text="Check", command=self.check)
        self.check_button.pack(side=tk.LEFT)
        self.bet_button = tk.Button(self.button_frame, text="Bet", command=self.make_bet)
        self.bet_button.pack(side=tk.LEFT)
        self.fold_button = tk.Button(self.button_frame, text="Fold", command=self.fold)
        self.fold_button.pack(side=tk.LEFT)
        
        # Betting Entry
        self.bet_frame = tk.Frame(self.root)
        self.bet_frame.pack()
        self.bet_entry = tk.Entry(self.bet_frame)
        self.bet_entry.pack()

        self.pocket_cards_label = tk.Label(self.root, text="Pocket Cards:")
        self.pocket_cards_label.pack()

        # Frame for community cards images
        self.pocket_cards_frame = tk.Frame(self.root)
        self.pocket_cards_frame.pack()
        
        # Log Area
        self.log_label = tk.Label(self.root, text="Game Log:")
        self.log_label.pack()
        self.log_text = tk.Text(self.root, height=15, width=50)
        self.log_text.pack()

    def update_money(self):
        self.pot_label.config(text=f"Pot - ${self.game.current_pot + self.game.total_pot}")

        # Update player info
        for i, player in enumerate(self.game.players):
            self.player_labels[i].config(text=f"{player.getName()} - ${player.getMoney()}")

    def update_display(self):
        curr_player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
        if curr_player != 0:
            if curr_player.is_agent == True:
                for widget in self.button_frame.winfo_children():
                    widget.pack_forget()
                self.bet_entry.pack_forget()
            else:
                for widget in self.button_frame.winfo_children():
                    widget.pack(side=tk.LEFT)
                self.bet_entry.pack()

            # Clear the current community card images (and previously shown text)
            for widget in self.community_cards_frame.winfo_children():
                widget.destroy()

            # Display images of community cards

            for card in self.game.field:
                img_path = f"pokerGame/images/{card}.png"  # Get the image path for the card
                try:
                    image = Image.open(img_path)
                    image = image.resize((100, 140))  # Resize the image to fit in the GUI
                    photo = ImageTk.PhotoImage(image)

                    card_label = tk.Label(self.community_cards_frame, image=photo)
                    card_label.image = photo  # Keep a reference to the image object
                    card_label.pack(side=tk.LEFT)
                except FileNotFoundError:
                    print(f"Image for {card} not found.")

            self.update_money()

            for widget in self.pocket_cards_frame.winfo_children():
                widget.destroy()

            for card in self.real_player.pocket_cards:
                img_path = f"pokerGame/images/{card}.png"  # Get the image path for the card
                try:
                    image = Image.open(img_path)
                    image = image.resize((100, 140))  # Resize the image to fit in the GUI
                    photo = ImageTk.PhotoImage(image)

                    card_label = tk.Label(self.pocket_cards_frame, image=photo)
                    card_label.image = photo  # Keep a reference to the image object
                    card_label.pack(side=tk.LEFT)
                except FileNotFoundError:
                    print(f"Image for {card} not found.")

    def check(self):
        curr_player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
        amount = self.game.check(curr_player)
        if amount == 0:
            self.log(f"{curr_player.getName()} checked.")
        else:
            self.log(f"{curr_player.getName()} called for {amount}.")
        self.game.current_turn = (self.game.current_turn + 1) % len(self.game.current_players)
        self.players_acted[curr_player] = True
        self.update_display()
    
    def make_bet(self):
        max_bet = min([(player.getMoney() + player.getBet()) for player in self.game.current_players if player != 0])
        print(max_bet)
        try:
            curr_player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
            amount = int(self.bet_entry.get())
            if amount <= curr_player.money:
                if amount <= max_bet:
                    if amount - self.game.current_bet >= self.game.big_blind_amount:
                        curr_player._bet(amount)
                        self.cpuBet(amount)
                        self.players_acted = {player: False for player in self.game.current_players if player != 0} 
                        self.players_acted[curr_player] = True
                    else:
                        messagebox.showerror("Invalid Input", "You can only raise by at least the big blind")
                else:
                    messagebox.showerror("Invalid Input", "Bet exceeds maximum")
            else:
                messagebox.showerror("Invalid Input", "You don't have enough money")
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid number.")
    
    def fold(self):
        curr_player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
        self.log(f"{curr_player.getName()} folded.")
        self.game.fold(self.game.current_turn)
        self.game.current_turn = (self.game.current_turn) % len(self.game.current_players)
        self.players_acted[curr_player] = True
        self.update_display()
    
    def cpuBet(self, amount : int):
        curr_player : Player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
        self.log(f"{curr_player.getName()} bet ${amount}.")
        self.game.current_turn = (self.game.current_turn + 1) % len(self.game.current_players)
        self.game.current_pot += amount
        self.game.current_bet = curr_player.getBet()
        self.players_acted = {player: False for player in self.game.current_players if player != 0}
        self.players_acted[curr_player] = True
        self.update_display()

    def raiseBet(self, raise_amount : int):
        curr_player : Player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
        print(curr_player.getName())
        self.log(f"{curr_player.getName()} raises by ${raise_amount} to ${curr_player.getBet()}.")
        self.game.current_turn = (self.game.current_turn + 1) % len(self.game.current_players)
        self.game.current_pot += raise_amount
        self.game.current_bet = curr_player.getBet()
        self.update_display()
        self.players_acted = {player: False for player in self.game.current_players if player != 0} 
        self.players_acted[curr_player] = True

    def callBet(self, call_difference : int):
        curr_player : Player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
        print(curr_player.getName())
        self.log(f"{curr_player.getName()} calls previous bet of ${self.game.current_bet}.")
        self.game.current_turn = (self.game.current_turn + 1) % len(self.game.current_players)
        self.game.current_pot += call_difference
        if self.game.current_bet != curr_player.getBet():
            raise Exception("Call is not equal to previous bet!")
        
        self.update_display() 
        self.players_acted[curr_player] = True

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def cpu_move(self):
        curr_player : Player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
        bet_result = curr_player.makeBet(self.game.small_blind_amount, 
                      self.game.big_blind_amount, 
                      self.game.current_bet,
                      self.game.field)
        
        if bet_result[0] == BetType.CHECK:
            self.check()
        elif bet_result[0] == BetType.FOLD:
            self.fold()
        elif bet_result[0] == BetType.BET:
            self.cpuBet(bet_result[1])
        elif bet_result[0] == BetType.RAISE:
            self.raiseBet(bet_result[1])
        else: # must be a call
            self.callBet(bet_result[1])
        for key in self.players_acted:
            if key != 0:
                print(key.getName(), self.players_acted[key])
        print('')

    def play_again(self):
        self.continue_button.destroy()
        self.game.reset_game()
        if self.game.currnum_players <= 1:
            self.log("\n\n\n\n\n\n\n\n\n\n\n\n\nNot enough players to continue.")
            return
        self.players_acted = {player: False for player in self.game.current_players if player != 0} 
        self.winner.set(f"")
        self.log("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nStarting New Match...")
        self.log(f"Small Blind: {self.game.sb_player.getName()}")
        self.log(f"Big Blind: {self.game.bb_player.getName()}")
        self.update_display()
        self.play()

    def game_over(self, winners : list[Player]):
        for player in self.game.current_players:
            if player != 0:
                self.log(f'\n{player.print_cards()}')
        
        for winner in winners:
            self.log(f"\nRound won by {winner.getName()}")
            winner.money += (self.game.total_pot + self.game.current_pot)
            self.winner.set(f"{winner.getName()} Wins!")
            
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()
        self.bet_entry.pack_forget()
        self.continue_button = tk.Button(self.button_frame, text="Continue", command=self.play_again)
        self.continue_button.pack()
        
        self.game.total_pot = 0
        self.game.current_pot = 0
        self.update_money()


    def play(self):
            if self.game.currnum_players <= 1:
                print(self.game.current_players[0])
                self.players_acted = {player: False for player in self.game.players} 
                for player in self.game.current_players:
                    if player != 0:
                        self.game_over([player])
                        return
                return
            
            curr_player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]

            if curr_player != 0:
                if False not in self.players_acted.values() and len(self.players_acted.values()) > 1:
                    for player in self.game.current_players:
                        if player != 0:
                            player.clearBet()
                    self.players_acted = {player: False for player in self.game.current_players if player != 0}
                    self.log("---New Betting Round---")
                    if self.game.game_state == 0:
                        self.game.flop()
                    elif self.game.game_state == 1:
                        self.game.turn()
                    elif self.game.game_state == 2:
                        self.game.river()
                    else:
                        self.game_over(self.game.showdown())
                        return

                self.update_display()
                if self.game.currnum_players == 1:
                    return  # The game is over, stop execution

                curr_player = self.game.current_players[self.game.current_turn % len(self.game.current_players)]
                if curr_player != 0:
                # If the current player is a bot, use a delay before making their move
                    if curr_player.is_agent:
                        # After CPU move is complete, call play again
                        self.root.after(100, self.cpu_move)
                        self.root.after(100, self.play)
                    else:
                        # If it's not a bot's turn, continue the game
                        self.root.after(100, self.play)
                else:
                    self.game.current_turn += 1
                    self.root.after(100, self.play)
            else:
                self.game.current_turn += 1
                self.root.after(100, self.play)



if __name__ == "__main__":
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()
