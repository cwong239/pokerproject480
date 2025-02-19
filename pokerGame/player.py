from card import Card
from copy import deepcopy
from handStrategy import HandStrat
from handBuilder import HandVal
from betStrategy import BetStrat, BetType

class Player:
    def __init__(self, name : str, money : int, 
                 hand_strat : HandStrat, bet_strat : BetStrat) -> None:
        """
        Creates a player in a game of Texas Hold 'em. Can be a bot or human
        """
        self.money = money
        self.pocket_cards : list[Card] = []
        self.bet = 0
        self.name = name
        self.hand_strat = hand_strat
        self.bet_strat = bet_strat
    
    def getName(self) -> str:
        return self.name
    
    def getMoney(self) -> int:
        return self.money

    def getBet(self) -> int:
        return self.bet
    
    def makeBet(self, small_blind : int, big_blind : int, 
                community_cards : list[Card]) -> tuple[BetType, list[Card] | int]:
        """
        Bet, Call, Fold, Check, or Raise based on betting strategy, blinds, and shown
        community cards

        Returns a tuple with the bet type and the bet amount (fold returns the pocket hand)
        """

        bet_result = self.bet_strat.determineBet(small_blind, big_blind, 
                                                 deepcopy(self.pocket_cards), 
                                                 deepcopy(community_cards))
        
        if bet_result[0] == BetType.FOLD:
            return (BetType.FOLD, self._fold())
        elif bet_result[0] == BetType.BET:
            return (BetType.BET, self._bet(bet_result[1]))
        elif bet_result[0] == BetType.CHECK:
            return (BetType.CHECK, self._check())
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
        self.pocket_cards.clear()
        return old_cards
     
    def _bet(self, amount : int) -> int:
        """
        Bet some amount
        """
        self.bet = amount
        self.money -= amount
        return self.bet
    
    
    def _check(self) -> int:
        """
        Bet of zero
        """
        return self._bet(0)
    
    def _raiseBet(self, amount : int) -> int:
        """
        Raise bet, returns amount raised
        """
        self.bet += amount
        return amount
    
    def _call(self, amount : int) -> int:
        """
        Match the bet of another player
        """
        return self._bet(amount)
    
    def recievePocket(self, card1 : Card, card2 : Card) -> None:
        """
        Recieve the 2 personal cards from dealer
        """
        self.pocket_cards.append(card1)
        self.pocket_cards.append(card2)

    def constructHand(self, community_cards : list[Card]) -> tuple[list[Card], HandVal]:
        """
        Construct a hand to be presented for showdown
        Uses 5 community cards and 2 "pocket" cards
        """
        if not self.pocket_cards:
            assert Exception("Can't build a hand if there are no pocket cards!")

        all_cards = deepcopy(self.pocket_cards)
        all_cards.extend(community_cards)

        self.hand_strat.takeInCards(all_cards)
        return self.hand_strat.execute()

    def __str__(self):
        return f'Player: {self.name} Cards: {self.pocket_cards} Money: {self.money}'
