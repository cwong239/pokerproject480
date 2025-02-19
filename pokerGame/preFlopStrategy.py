from poker import Game
from player import Player

class preFlopOdds:
    def __init__(self, game: Game, player: Player):
        self.agent = player
        self.game = game
        
    def potPercent(self, pot: int, currentBet: int) -> float:
        return pot/currentBet
    
    def getAllBets(self) -> float:
        return sum(player.getBet() for player, _ in self.game.current_players)

    def potOddRatio(self, pot: int, currentBet: int) -> float:
        return (pot + self.getAllBets()) / currentBet if currentBet > 0 else float('inf')

    # might want to implement some sort of hand win logic so that they aren't betting on a duce and a 7
    def potEquity(self, pot: int, currentBet: int):
        """
        The minimum percentage of equity (chance of winning the hand) 
        a player needs to have in order to profitably call 
        a bet based on the current pot size and the bet they are facing
        """
        totalPot = pot + self.getAllBets()
        if currentBet == 0:
            betAmount = min(totalPot * 0.5, totalPot)  
        elif currentBet > 0:
            potOdds = self.potOddRatio(pot, currentBet, totalPot-pot)

            if potOdds < 0.33:
                # If the bet is relatively small compared to the pot, raise aggressively
                betAmount = min(currentBet * 3, totalPot)
            elif potOdds < 0.5:
                # If the bet is moderate, call or raise small
                betAmount = min(currentBet * 2, totalPot)
            else:
                # If the bet is large, only call or fold
                betAmount = currentBet if totalPot > currentBet * 3 else 0  # Fold if the pot is too small

        return betAmount

    def breakEven(self, pot: int, currentBet: int):
        return (currentBet/(pot+currentBet))
    
    def calcOpponentFold(self):
        perc = 0
        currMax = 0
        for oppFold in self.game.opponentFold:
            if oppFold == self.agent:
                pass
            elif self.game.opponentFold[oppFold] > currMax:
                currMax = self.game.opponentFold[oppFold]
        if self.game.rounds == 0:
            return perc
        return (currMax / self.game.rounds)

    def autoProfit(self, pot: int, currentBet: int):
        breakEvenPer = self.breakEven(pot, currentBet)
        oppFoldPer = self.calcOpponentFold()
        return oppFoldPer > breakEvenPer