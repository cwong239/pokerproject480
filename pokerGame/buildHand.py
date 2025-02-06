from card import Card, Rank, Suit

class buildHand:
    def __init__(self, cards : list[Card]) -> None:
        self.cards = cards
        self.same_value : dict[Rank, list[Card]] = {}
        self.same_suit : dict [Suit, list[Card]] = {}
        self.sequence = []
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
                for j in range(i, i + 5):
                    self.sequence.append(value_sorted[j])
                break

        # add functions for determining the different hands (flush, straight, full house, etc.)
            