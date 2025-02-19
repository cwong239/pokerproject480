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
                     pocket_cards : list[Card], community_cards : list[Card]) -> tuple[BetType, int]:
        """
        Determine what the bet will be based off the blinds 
        and the current round of betting.

        Returns bet type and amount of bet (if applicable)
        """
        if small_blind < 0 or big_blind < 0:
            raise Exception("Invalid blind values given!")
    
        if len(pocket_cards) != 2:
            # Can tell game state based on current cards (community + pocket)
            # 2 = pre flop, 5 = flop, 6 = turn, 7 = river
            raise Exception("Can't bet before pocket cards are dealt!")
    
        if len(community_cards) > 5:
            raise Exception("Can't have more than 5 community cards")
    
        return (BetType.FOLD, -1)

class BigBlindCallStrat(BetStrat):
    """
    Simple strategy where the big blind is always called regardless
    of cards, small blind, or round of betting
    """
    def __init__(self):
        super().__init__()
    
    def determineBet(self, small_blind, big_blind, pocket_cards, community_cards):
        super().determineBet(small_blind, big_blind, pocket_cards, community_cards)

        return (BetType.CALL, big_blind)

# TODO: implement custom betting strategy for AI