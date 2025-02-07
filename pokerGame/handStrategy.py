from handBuilder import HandBuilder, HandVal
from card import Card

class HandStrat:
    """
    Represents a strategy for constructing a hand when showdown happens
    """
    def __init__(self):
        self.builder : HandBuilder = None
    
    def takeInCards(self, cards : list[Card]) -> None:
        """
        Take in list of cards for processing in HandBuilder
        """
        self.builder = HandBuilder(cards)

    def execute(self) -> tuple[list[Card], HandVal]:
        """
        Execute on the strategy and construct a hand
        """
        if self.builder is None:
            raise Exception("Can't execute hand building strategy without getting cards first!")

        return ([], HandVal.NO_HAND)

class BestHandStrat(HandStrat):
    """
    Strategy where creating the best hand is attempted
    """
    def __init__(self):
        super().__init__()
        self.hand_order = []
    
    def takeInCards(self, cards) -> None:
        super().takeInCards(cards)

        # check in order of highest val hand to lowest
        self.hand_order.extend([self.builder.checkStraightFlush,
                                self.builder.checkFOK,
                                self.builder.checkFullHouse,
                                self.builder.checkFlush,
                                self.builder.checkStraight,
                                self.builder.checkTOK,
                                self.builder.checkTwoPairs,
                                self.builder.checkPair,
                                self.builder.checkHighCard])
    
    def execute(self) -> tuple[list[Card], HandVal]:
        super().execute()

        result_hand = ([], HandVal.NO_HAND)
        while result_hand[1] == HandVal.NO_HAND:
            checkForHand = self.hand_order.pop(0)
            result_hand = checkForHand()
        
        # current handbuilder no longer needed
        self.builder = None

        return result_hand

class WorstHandStrat(HandStrat):
    """
    Strategy where creating the worst hand is attempted
    (Will only return High Card hands)
    """
    def __init__(self):
        super().__init__()
    
    def execute(self) -> tuple[list[Card], HandVal]:
        super().execute()

        return self.builder.checkHighCard()