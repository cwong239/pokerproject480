from card import Card, Rank, Suit
from enum import IntEnum
from copy import deepcopy

class HandVal(IntEnum):
    NO_HAND = 0
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIRS = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9
    # no royal flush since its just a type of straight flush

class buildHand:
    def __init__(self, cards : list[Card]) -> None:
        self.cards = cards
        self.same_value : dict[Rank, list[Card]] = {}
        self.same_suit : dict [Suit, list[Card]] = {}
        self.sequences : list[list[Card]] = []
        self.processCards()
    
    def processCards(self) -> None:
        """
        Process cards into groups with same value and same suit.
        Also check if there is a sequence of 5 consecutive cards (straight)
        """
        for card in self.cards:
            if card.getRank() not in self.same_value.keys():
                self.same_value[card.getRank()] = [card]
            else:
                self.same_value.get(card.getRank()).append(card)
            
            if card.getSuit() not in self.same_suit.keys():
                self.same_suit[card.getSuit()] = [card]
            else:
                self.same_suit.get(card.getSuit()).append(card)
        
        value_sorted = sorted(self.cards, key=lambda card: card.getRank().value)
        for i in range(3):
            sequence_found = True
            for j in range(i, i + 5):
                if (value_sorted[j].getRank().value + 1 
                   != value_sorted[j + 1].getRank().value):
                    sequence_found = False
                    break
            
            if sequence_found:
                seq = []
                for j in range(i, i + 5):
                    seq.append(value_sorted[j])
                
                self.sequences.append(seq)

    def checkStraightFlush(self) -> tuple[list[Card], HandVal]:
        """
        Return any straight flush hand if possible (Straight + Flush)
        """
        for sequence in self.sequences:
            req_suit = sequence[0].getSuit()
            same_suit = True
            for card in sequence:
                if card.getSuit() != req_suit:
                    same_suit = False
                    break
            
            if same_suit:
                return (sequence, HandVal.STRAIGHT_FLUSH)
        
        return ([], HandVal.NO_HAND)
    
    def checkFOK(self) -> tuple[list[Card], HandVal]:
        """
        Return any Four of a Kind (four same value)
        """
        for vals in self.same_value.values():
            if len(vals) == 4:
                # get another card to complete the hand
                other_cards = list(set(self.cards) - set(vals))
                hand = deepcopy(vals).append(other_cards[0])
                return (hand, HandVal.FOUR_OF_KIND)
        
        return ([], HandVal.NO_HAND)

    def checkFullHouse(self) -> tuple[list[Card], HandVal]:
        """
        Return any Full House (Three of Kind + Pair)
        """
        tok = []
        pair = []
        for vals in self.same_value.values():
            if len(vals) == 3:
                tok = deepcopy(vals)
            if len(vals) == 2:
                pair = deepcopy(vals)

            if tok and pair:
                # TOK and pair found
                break
        
        if tok and pair:
            hand = tok + pair
            return (hand, HandVal.FULL_HOUSE)
    
        return ([], HandVal.NO_HAND)

    def checkFlush(self) -> tuple[list[Card], HandVal]:
        """
        Return any Flush (five cards of same suit)
        """
        for suits in self.same_suit.values():
            if len(suits) == 5:
                return (deepcopy(suits), HandVal.FLUSH)
        
        return ([], HandVal.NO_HAND)
    
    def checkStraight(self) -> tuple[list[Card], HandVal]:
        """
        Return any Straight (five cards in sequential order)
        """
        if self.sequences:
            return (deepcopy(self.sequences[0], HandVal.STRAIGHT))
    
        return ([], HandVal.NO_HAND)

    # do checks for three of kind, two pairs, pair, and high card

