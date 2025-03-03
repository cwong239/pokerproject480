from enum import IntEnum

class Suit(IntEnum):
    CLUB = 1
    DIAMOND = 2
    HEART = 3
    SPADE = 4

class Rank(IntEnum):
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
    
    def __repr__(self) -> str:
        suit_symbols = {Suit.CLUB: "C", Suit.DIAMOND: "D", Suit.HEART: "H", Suit.SPADE: "S"}
        rank_symbols = {Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4", Rank.FIVE: "5", Rank.SIX: "6", 
                        Rank.SEVEN: "7", Rank.EIGHT: "8", Rank.NINE: "9", Rank.TEN: "10", Rank.JACK: "J", 
                        Rank.QUEEN: "Q", Rank.KING: "K", Rank.ACE: "A"}
        return f"{suit_symbols[self.suit]}{rank_symbols[self.rank]}"
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return (self.getRank().value == other.getRank().value 
                    and self.getSuit().value == other.getSuit().value)
        
        return False
    
    def __gt__(self, other):
        if isinstance(other, Card):
            return self.getRank().value > other.getRank().value

        return False
    
    def __lt__(self, other):
        if isinstance(other, Card):
            return self.getRank().value < other.getRank().value
        
        return False
    
    def __hash__(self):
        return hash(self.rank.value + (100 * self.suit.value))