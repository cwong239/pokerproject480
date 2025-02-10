import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from poker import Game  # Assuming your game class is in game.py

class PokerGUI:
    def __init__(self, root, player_count=5):
        self.root = root
        self.root.title("Poker Game")
        
        self.game = Game(player_count)
        self.winner = tk.StringVar()
        
        self.game.flop() #TEMPORARY

        self.create_widgets()
        self.update_display()


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
        self.bet_entry = tk.Entry(self.root)
        self.bet_entry.pack()
        
        # Log Area
        self.log_label = tk.Label(self.root, text="Game Log:")
        self.log_label.pack()
        self.log_text = tk.Text(self.root, height=10, width=50)
        self.log_text.pack()

    def update_display(self):
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
        
        if len(self.game.current_players) == 1:
            print(f"{self.game.current_players[0][0].getName()} Wins!")
            self.winner.set(f"{self.game.current_players[0][0].getName()} Wins!")
            self.game.current_players[0][0].money += self.game.current_pot
            self.game.current_pot = 0
            for widget in self.button_frame.winfo_children():
                widget.destroy()

        self.pot_label.config(text=f"Pot - ${self.game.current_pot}")

        # Update player info
        for i, player in enumerate(self.game.players):
            self.player_labels[i].config(text=f"{player.getName()} - ${player.getMoney()}")

    def check(self):
        self.log(f"{self.game.current_players[self.game.current_turn][0].getName()} checked.")
        self.game.current_turn = (self.game.current_turn + 1) % len(self.game.current_players)
        self.update_display()
    
    def  make_bet(self):
        try:
            amount = int(self.bet_entry.get())
            print(self.game.current_players[self.game.current_turn][0].getName())
            self.game.current_players[self.game.current_turn][0]._bet(amount)
            self.log(f"{self.game.current_players[self.game.current_turn][0].getName()} bet ${amount}.")
            self.game.current_turn = (self.game.current_turn + 1) % len(self.game.current_players)
            self.game.current_pot += amount
            self.update_display()
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid number.")
    
    def fold(self):
        self.log(f"{self.game.current_players[self.game.current_turn][0].getName()} folded.")
        self.game.fold(self.game.current_turn)
        self.game.current_turn = (self.game.current_turn) % len(self.game.current_players)
        self.update_display()

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()
