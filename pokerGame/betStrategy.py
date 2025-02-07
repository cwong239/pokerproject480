from card import Card
from enum import IntEnum

class BetType(IntEnum):
    FOLD = 0
    BET = 1
    CHECK = 2
    CALL = 3
    RAISE = 4

class BetStrat:
    """
    A strategy for betting. Core of AI will be a betting strategy
    """
    def __init__(self):
        pass

    def determineBet(self, small_blind : int, big_blind : int, 
                     current_cards : list[Card]) -> tuple[BetType, int]:
        """
        Determine what the bet will be based off the blinds 
        and the current round of betting.

        Returns bet type and amount of bet (if applicable)
        """
        if small_blind < 0 or big_blind < 0:
            raise Exception("Invalid blind values given!")
    
        if len(current_cards) < 2:
            # Can tell game state based on current cards (community + pocket)
            # 2 = pre flop, 5 = flop, 6 = turn, 7 = river
            raise Exception("Can't bet without recieving pocket cards first!")
    
        return (BetType.FOLD, -1)

class BigBlindCallStrat(BetStrat):
    """
    Simple strategy where the big blind is always called regardless
    of cards, small blind, or round of betting
    """
    def __init__(self):
        super().__init__()
    
    def determineBet(self, small_blind, big_blind, current_cards):
        super().determineBet(small_blind, big_blind, current_cards)

        return (BetType.CALL, big_blind)

# TODO: implement custom betting strategy for AI