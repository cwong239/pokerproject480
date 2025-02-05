from enum import Enum

class Suit(Enum):
    CLUB = 1
    DIAMOND = 2
    HEART = 3
    SPADE = 4

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    # All cards have some rank and suit
    def __init__(self, rank : Rank, suit : Suit) -> None:
        self.rank = rank
        self.suit = suit
    
    def getRank(self) -> Rank:
        return self.rank

    def getSuit(self) -> Suit:
        return self.suit