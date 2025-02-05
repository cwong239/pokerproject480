"""
Player Class
    Functions
        Fold
        raise
        Check
    Variaels
        Hands
        Money
        Bet
    Agent Inherits that
"""
from card import Card

class Player:
    def __init__(self, name : str, money : int) -> None:
        self.money = money
        self.pocket_cards : list[Card] = []
        self.bet = 0
        self.name = name
    
    # Fold and return cards to dealer 
    def fold(self) -> list[Card]:
        if self.pocket_cards:
            old_cards = self.pocket_cards.copy()
            self.pocket_cards.clear()
            return old_cards
    
    # Bet some amount 
    def bet(self, amount : int) -> int:
        self.bet = amount
        return self.bet
    
    def getBet(self) -> int:
        return self.bet
    
    # Bet of zero
    def check(self) -> int:
        return self.bet(0)
    
    # Raise bet and return amount raised
    def raiseBet(self, amount : int) -> int:
        self.bet += amount
        return amount
    
    # Match the bet of another player
    def call(self, amount : int) -> int:
        return self.bet(amount)
    
    # Recieve the 2 personal cards from dealer
    def recievePocket(self, card1 : Card, card2 : Card) -> None:
        self.pocket_cards.append(card1)
        self.pocket_cards.append(card2)

    # Construct a hand to be presented for showdown
    def constructHand(self, community_cards : list[Card]) -> list[Card]:
        if self.pocket_cards: 
            return community_cards # Add logic for constructing a good hand
    
        return []

    def __str__(self):
        return f'Player: {self.name} Cards: {self.pocket_cards} Money: {self.money}'