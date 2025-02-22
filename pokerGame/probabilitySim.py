from card import Card, Suit, Rank
from handBuilder import HandVal
from handStrategy import BestHandStrat
from random import sample

class ProbabilitySim:
    """
    Runs a simulation to get card hand probabilities
    """
    DECK = [Card(rank, suit) for suit in Suit for rank in Rank]
    NO_CARD_PROBS = [0, 0.174, 0.438, 0.235, 0.0483, 0.0462, 0.0303, 0.026, 0.00168, 0.000311]

    @staticmethod
    def getProbs(cards : list[Card], cutoff : int = 0) -> list[float]:
        """
        Gets the probabilities of getting certain hands based on the current
        known cards
        
        Will need to use cutoff for pre-flop probabilites (2 cards) as the 
        simulations will take to long otherwise. Will result in a less accurate
        probability prediction
        """
        if len(cards) > 7:
            raise Exception("Invalid number of cards given!")
        
        if len(cards) == 0:
            # can just use probs with no cards
            return ProbabilitySim.NO_CARD_PROBS
        
        # index 0 tracks number of 7 card combinations, 1-9 measures the number
        # of times each hand appears (1 = High card hand, 9 = straigth flush)
        counts = [0] * 10
        ProbabilitySim._simulate(cards, counts, cutoff)
        probs = [0] # filler spot to make getting probabilites easier
        for i in range(1, len(counts)):
            probs.append(counts[i] / counts[0])

        return probs
    
    @staticmethod
    def _simulate(cards : list[Card], counts : list[int], cutoff : int) -> None:
        """
        Searches through all possible 7 card combinations for the best hand for 
        each combination
        """
        if len(cards) == 7:
            # full cards reached, check for best hand
            best_hand_strat = BestHandStrat()
            best_hand_strat.takeInCards(cards)
            hand = best_hand_strat.execute()

            counts[0] += 1              # increase total
            counts[hand[1].value] += 1  # increase hand count
            return

        if cutoff > 0 and counts[0] >= cutoff:
            return # cutoff reached, stop search

        # simualte all potential cards
        remaining_cards = [card for card in ProbabilitySim.DECK if card not in cards]
        for rem_card in remaining_cards:
            ProbabilitySim._simulate(cards + [rem_card], counts, cutoff)

if __name__ == "__main__":
    current_hand = sample(ProbabilitySim.DECK, 2)
    # arbitrary cutoff, change according to acceptable simulation time at cost of accuracy
    pre_flop_cutoff = 500000    

    print("Current hand pre-flop is {}".format(current_hand))
    probs = ProbabilitySim.getProbs(current_hand, pre_flop_cutoff)
    for hand in HandVal:
        print("Probability of {} being best is {:.3f}".format(hand.name, probs[hand.value]))
    
    value = 0
    for i in range(1, len(probs)):
        value += i * probs[i]
    
    print("Average hand value of {}".format(value))

    current_hand = (current_hand + sample([card for card in ProbabilitySim.DECK 
                                           if card not in current_hand],3))
    print("\nCurrent hand post-flop is {}".format(current_hand))
    # Don't need cutoff after flop (5 cards known), runtime will be near instant
    probs = ProbabilitySim.getProbs(current_hand)
    for hand in HandVal:
        print("Probability of {} being best is {:.3f}".format(hand.name, probs[hand.value]))