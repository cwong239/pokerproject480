from card import Card
from enum import IntEnum
from oddsForPot import potOdds
from probabilitySim import ProbabilitySim
from copy import deepcopy
from random import randint

class BetType(IntEnum):
    FOLD = 0
    BET = 1
    CHECK = 2
    RAISE = 3
    CALL = 4

class BetStrat:
    """
    A strategy for betting. Core of AI will be a betting strategy
    """
    def __init__(self):
        pass

    @staticmethod
    def averageHandValue(hand_probs : list[float]) -> float:
        """
        Get an average of the possible hand values, for comparison
        """
        value = 0
        for i in range(1, len(hand_probs)):
            value += i * hand_probs[i]
        
        return value

    @staticmethod
    def highestHandProb(hand_probs : list[float]) -> float:
        """
        Get the highest hand probability
        """
        highest_prob = 0
        for prob in hand_probs:
            if prob > highest_prob:
                highest_prob = prob
        
        return highest_prob
    
    def probsToBet(self, pocket_cards : list[Card], community_cards : list[Card], 
                   current_bet : int, value_threshold : int, big_blind : int,
                   cutoff : int = 0) -> tuple[BetType, int]:
        self_cards = deepcopy(pocket_cards)
        self_cards.extend(community_cards)
        self_chances = ProbabilitySim.getProbs(self_cards, cutoff)
        opponent_chances = ProbabilitySim.getProbs(community_cards, cutoff)

        self_hand_value = BetStrat.averageHandValue(self_chances)
        opponent_hand_value = BetStrat.averageHandValue(opponent_chances)

        self_highest_prob = BetStrat.highestHandProb(self_chances)

        if current_bet == 0:
            # no bets/only checks
            if opponent_hand_value - self_hand_value > value_threshold:
                return (BetType.CHECK, 0)
            else:
                return (BetType.BET, big_blind)
        else:
            # previous player has made a bet
            if ((opponent_hand_value - self_hand_value <= (value_threshold / 2)) 
                 and (self_highest_prob >= potOdds().potEquity(current_bet))):
                return (BetType.RAISE, current_bet + big_blind)
            elif ((opponent_hand_value - self_hand_value <= (value_threshold * 1.5)) 
                  and (self_highest_prob >= potOdds().potEquity(current_bet))):
                return (BetType.CALL, current_bet)
            else:
                return (BetType.FOLD, 0)

    def determineBet(self, small_blind : int, big_blind : int, 
                     current_bet : int,
                     pocket_cards : list[Card], 
                     community_cards : list[Card],
                     player_name : str) -> tuple[BetType, int]:
        """
        Determine what the bet will be based off the blinds 
        and the current round of betting.

        Returns bet type and amount of bet (if applicable)
        """
        if small_blind < 0 or big_blind < 0 or current_bet < 0:
            raise Exception("Invalid blind/bet values given!")
    
        if len(pocket_cards) != 2:
            # Can tell game state based on current cards (community + pocket)
            # 2 = pre flop, 5 = flop, 6 = turn, 7 = river
            raise Exception("Can't bet before pocket cards are dealt!")
    
        if len(community_cards) > 5:
            raise Exception("Can't have more than 5 community cards")
    
        if player_name is None:
            raise Exception("Player must have a name!")
    
        return (BetType.FOLD, -1)

class RandomStrat(BetStrat):
    """
    Entirely random betting
    """
    def __init__(self):
        super().__init__()
    
    def determineBet(self, small_blind, big_blind, current_bet, 
                     pocket_cards, community_cards, player_name):
        super().determineBet(small_blind, big_blind, current_bet, 
                                    pocket_cards, 
                                    community_cards,
                                    player_name)

        bet = -1
        if current_bet == 0:
            bet = randint(1, 2)
        else:
            bet = randint(3, 8)

        # ~8% fold chance
        if randint(1, 12) == 1:
            return (BetType.FOLD, pocket_cards)
        
        if bet == BetType.BET.value:
            return (BetType.BET, big_blind)
        elif bet == BetType.CHECK.value:
            return (BetType.CHECK, 0)
        elif bet == BetType.RAISE.value:
            return (BetType.RAISE, current_bet + big_blind)
        else: # must be a call
            return (BetType.CALL, current_bet)

# TODO: implement custom betting strategy for AI
class ArguablyOptimalStrat(BetStrat):
    """
    Considers hand chances for self and opponent as well as 
    pot equity to determine bet

    Assumptions: Limit Texas Hold'Em rules for betting simplicity
    """
    def __init__(self):
        super().__init__()
    
    def determineBet(self, small_blind, big_blind, current_bet, 
                     pocket_cards, community_cards, player_name) -> tuple[BetType, int]:
        super().determineBet(small_blind, big_blind, current_bet, 
                             pocket_cards, community_cards, player_name)
        
        sim_cutoff = 500000 # arbitrary cutoff for number of hands to simulate, bigger the better but slower
        value_threshold = 0.5 # acceptable difference in average hand values
        
        if current_bet != 0:
            if potOdds().autoProfit(current_bet, player_name):
                # auto win, so raise to the big blind
                return (BetType.RAISE, big_blind)
        
        # get probabilites from simulation
        return self.probsToBet(pocket_cards, community_cards, 
                                current_bet, value_threshold, 
                                big_blind, sim_cutoff)

if __name__ == "__main__":
    from poker import Game
    game = Game(5)
    player = game.current_players[0]
    game.deal()
    bet = player.makeBet(1, 2, 0, game.field)
    print("Pre flop bet: {}".format(bet))

    if bet[0] != BetType.FOLD:
        game.flop()
        game.pot = 10
        bet = player.makeBet(1, 2, 2, game.field)
        print("Post flop bet: {}".format(bet))

        if bet[0] != BetType.FOLD:
            game.turn()
            game.pot = 20
            bet = player.makeBet(1, 2, 4, game.field)
            print("Turn bet: {}".format(bet))
            
            if bet[0] != BetType.FOLD:
                game.river()
                game.pot = 30
                bet = player.makeBet(1, 2, 6, game.field)
                print("River bet: {}".format(bet))
    
    print("End of betting")