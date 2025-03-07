from card import Card
from copy import deepcopy
from handStrategy import HandStrat
from handBuilder import HandVal
from betStrategy import BetStrat, BetType

class Player:
    def __init__(self, name : str, money : int, 
                 hand_strat : HandStrat, bet_strat : BetStrat, is_agent=False) -> None:
        """
        Creates a player in a game of Texas Hold 'em. Can be a bot or human
        """
        self.money = money
        self.pocket_cards : list[Card] = []
        self.bet = 0
        self.name = name
        self.hand_strat = hand_strat
        self.bet_strat = bet_strat
        self.is_agent = is_agent
    
    def getName(self) -> str:
        return self.name
    
    def getMoney(self) -> int:
        return self.money

    def getBet(self) -> int:
        return self.bet
    
    def clearBet(self) -> None:
        self.bet = 0
        return
    
    def recievePot(self, pot : int) -> None:
        if pot <= 0:
            raise Exception("Invalid pot amount!")
        
        self.money += pot
        return
    
    def makeBetManual(self, bet_amount: int) -> bool:
        """
        Manually makes a bet
        """
        if bet_amount > self.getMoney():
            return False
        self.money -= bet_amount
        self.bet += bet_amount
        return True
    
    def makeBet(self, small_blind : int, big_blind : int, current_bet : int,
                community_cards : list[Card]) -> tuple[BetType, list[Card] | int]:
        """
        Bet, Call, Fold, Check, or Raise based on betting strategy, blinds, and shown
        community cards

        Returns a tuple with the bet type and the bet amount (fold returns the pocket hand)
        """

        bet_result = self.bet_strat.determineBet(small_blind, big_blind,
                                                 current_bet,
                                                 deepcopy(self.pocket_cards), 
                                                 deepcopy(community_cards),
                                                 self.name)
        
        if bet_result[0] == BetType.CHECK:
            return (BetType.CHECK, self._check())
        elif bet_result[0] == BetType.FOLD or self.money == 0:
            # Can't do other bet types without money
            return (BetType.FOLD, self._fold())
        elif bet_result[0] == BetType.BET:
            return (BetType.BET, self._bet(bet_result[1]))
        elif bet_result[0] == BetType.CALL:
            return (BetType.CALL, self._call(bet_result[1]))
        else: # only bet type left is raise
            return (BetType.RAISE, self._raiseBet(bet_result[1]))
     
    def _fold(self) -> list[Card]:
        """
        Fold and give up pocket cards
        """
        if not self.pocket_cards:
            assert Exception("Can't fold if there are no pocket cards!")

        old_cards = deepcopy(self.pocket_cards)
        self.clearPocket()
        return old_cards
     
    def _bet(self, amount : int) -> int:
        """
        Bet some amount
        """
        bet_amount = amount
        if self.money < amount:
            bet_amount = self.money

        self.bet += bet_amount
        self.money -= bet_amount
        return self.bet
    
    
    def _check(self) -> int:
        """
        Bet/raise by zero, do nothing
        """
        return 0
    
    def _raiseBet(self, amount : int) -> int:
        """
        Raise bet by amount, return total bet
        """
        raise_amount = amount
        if self.money < amount:
            raise_amount = self.money
        
        self.bet += raise_amount
        self.money -= raise_amount
        return self.bet
    
    def _call(self, amount : int) -> int:
        """
        Match the bet of another player, return total bet
        """
        if self.bet > amount:
            raise Exception("Can't call to less than current bet!")

        return self._raiseBet(amount - self.bet)
    
    def recievePocket(self, card1 : Card, card2 : Card) -> None:
        """
        Recieve the 2 personal cards from dealer
        """
        if len(self.pocket_cards) > 0:
            raise Exception("Can't accept more cards than 2 pocket cards!")

        self.pocket_cards.append(card1)
        self.pocket_cards.append(card2)

    def clearPocket(self) -> None:
        """
        Get rid of pocket cards. For folding or preparing for next round
        """
        self.pocket_cards.clear()

    def constructHand(self, community_cards : list[Card]) -> tuple[list[Card], HandVal]:
        """
        Construct a hand to be presented for showdown
        Uses 5 community cards and 2 "pocket" cards
        """
        if not self.pocket_cards:
            raise Exception("Can't build a hand if there are no pocket cards!")

        all_cards = deepcopy(self.pocket_cards)
        all_cards.extend(community_cards)

        if len(all_cards) != 7:
            raise Exception("Should have exatly 7 cards to build hand: {}".format(all_cards))

        self.hand_strat.takeInCards(all_cards)
        return self.hand_strat.execute()

    def __str__(self):
        return f'Player: {self.name} Cards: {self.pocket_cards} Money: {self.money}'
    
    def print_cards(self):
        return f'{self.name} Cards: {self.pocket_cards}'
