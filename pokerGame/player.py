from card import Card
from copy import deepcopy

class Player:
    def __init__(self, name : str, money : int) -> None:
        """
        Creates a player in a game of Texas Hold 'em. Can be a bot or human
        """
        self.money = money
        self.pocket_cards : list[Card] = []
        self.bet = 0
        self.name = name
    
    def getName(self) -> str:
        return self.name
    
    def getMoney(self) -> int:
        return self.money
     
    def fold(self) -> list[Card]:
        """
        Fold and return cards to dealer
        """
        if self.pocket_cards:
            old_cards = deepcopy(self.pocket_cards)
            self.pocket_cards.clear()
            return old_cards
     
    def bet(self, amount : int) -> int:
        """
        Bet some amount
        """
        self.bet = amount
        return self.bet
    
    def getBet(self) -> int:
        return self.bet
    
    def check(self) -> int:
        """
        Bet of zero
        """
        return self.bet(0)
    
    def raiseBet(self, amount : int) -> int:
        """
        Raise bet, returns amount raised
        """
        self.bet += amount
        return amount
    
    def call(self, amount : int) -> int:
        """
        Match the bet of another player
        """
        return self.bet(amount)
    
    def recievePocket(self, card1 : Card, card2 : Card) -> None:
        """
        Recieve the 2 personal cards from dealer
        """
        self.pocket_cards.append(card1)
        self.pocket_cards.append(card2)

    def constructHand(self, community_cards : list[Card]) -> list[Card]:
        """
        Construct a hand to be presented for showdown
        Uses 5 community cards and 2 "pocket" cards
        """
        if self.pocket_cards: 
            return community_cards # Add logic for constructing a good hand
    
        return []

    def __str__(self):
        return f'Player: {self.name} Cards: {self.pocket_cards} Money: {self.money}'