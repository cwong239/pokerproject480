from card import Card, Rank, Suit
from enum import IntEnum, Enum
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

class HandBuilder:
    """
    Used to build a full hand (5 cards) using the 2 pocket cards 
    and 5 community cards
    """
    def __init__(self, cards : list[Card]) -> None:
        if len(cards) != 7:
            raise Exception("Invalid number of cards for hand construction: {}".format(cards))
        
        self.cards = cards
        self.same_value : dict[Rank, list[Card]] = {}
        self.same_suit : dict [Suit, list[Card]] = {}
        self.sequences : list[list[Card]] = []
        self._processCards()
    
    def _processCards(self) -> None:
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
            for j in range(i, i + 4):
                if (value_sorted[j].getRank().value + 1 
                   != value_sorted[j + 1].getRank().value):
                    sequence_found = False
                    break
            
            if sequence_found:
                seq = []
                for j in range(i, i + 5):
                    seq.append(value_sorted[j])
                
                self.sequences.append(seq)
    
    def _getOtherCards(self, cur_cards : list[Card]) -> list[Card]:
        """
        Get cards not currently in the hand in order from highest to lowest rank
        """
        other_cards = [card for card in self.cards if card not in cur_cards]
        sorted_cards = sorted(other_cards)
        sorted_cards.reverse()
        return sorted_cards

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
                return (deepcopy(sequence), HandVal.STRAIGHT_FLUSH)
        
        return ([], HandVal.NO_HAND)
    
    def checkFOK(self) -> tuple[list[Card], HandVal]:
        """
        Return any Four of a Kind (four same value)
        """
        for vals in self.same_value.values():
            if len(vals) == 4:
                # get another card to complete the hand
                other_cards = self._getOtherCards(vals)
                hand = deepcopy(vals)
                hand.append(other_cards[0])
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
            return (deepcopy(self.sequences[0]), HandVal.STRAIGHT)
    
        return ([], HandVal.NO_HAND)

    def checkTOK(self) -> tuple[list[Card], HandVal]:
        """
        Return any Three of a Kind (three same value)
        """
        for vals in self.same_value.values():
            if len(vals) == 3:
                # get two cards to complete the hand
                other_cards = self._getOtherCards(vals)
                #list(set(self.cards) - set(vals))
                hand = deepcopy(vals)
                hand.extend(other_cards[:2])
                return (hand, HandVal.THREE_OF_KIND)
        
        return ([], HandVal.NO_HAND)
    
    def checkTwoPairs(self) -> tuple[list[Card], HandVal]:
        """
        Return any Two Pairs (Two instances of two cards having the same value)
        """
        pair1 = []
        pair2 = []
        for vals in self.same_value.values():
            if len(vals) == 2:
                if not pair1:
                    pair1 = vals
                elif not pair2:
                    pair2 = vals
                
            if pair1 and pair2:
                break
        
        if pair1 and pair2:
            partial_hand = pair1 + pair2
            # get a card to complete the hand
            other_cards = self._getOtherCards(partial_hand)
            hand = deepcopy(partial_hand)
            hand.append(other_cards[0])
            return (hand, HandVal.TWO_PAIRS)
        
        return ([], HandVal.NO_HAND)
    
    def checkPair(self) -> tuple[list[Card], HandVal]:
        """
        Return a Pair (two same value)
        """
        for vals in self.same_value.values():
            if len(vals) == 2:
                # get three cards to complete the hand
                other_cards = self._getOtherCards(vals)
                hand = deepcopy(vals)
                hand.extend(other_cards[:3])
                return (hand, HandVal.PAIR)
        
        return ([], HandVal.NO_HAND)
                
    def checkHighCard(self) -> tuple[list[Card], HandVal]:
        """
        Return a High Card (highest val card + 4 randoms)
        """
        highest_val = Rank.TWO
        high_card = None
        for card in self.cards:
            if card.getRank().value >= highest_val.value:
                highest_val = card.getRank()
                high_card = card
        
        # get four cards to compelte the hand
        other_cards = self._getOtherCards([high_card])
        hand = [high_card]
        hand.extend(other_cards[:4])
        return (hand, HandVal.HIGH_CARD)
        
