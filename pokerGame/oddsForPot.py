class potOdds:
    def __init__(self):
        from poker import Game
        self.game = Game.getInstance()
        
    def potPercent(self, currentBet: int) -> float:
        return self.game.getPot() / currentBet

    def potOddRatio(self, currentBet: int) -> float:
        return self.game.getPot() / currentBet if currentBet > 0 else float('inf')

    # might want to implement some sort of hand win logic so that they aren't betting on a duce and a 7
    def potEquity(self, currentBet: int) -> float:
        """
        The minimum equity (chance of winning the hand) 
        a player needs to have in order to profitably call 
        a bet based on the current pot size and the bet they are facing
        """
        # if ratio is X:1 then equity percent is 1/(X+1)
        return 1 / (self.potOddRatio(currentBet) + 1)

    def breakEven(self, currentBet: int):
        return (currentBet/(self.game.getPot() + currentBet))
    
    def calcOpponentFold(self, player_name : str) -> float:
        perc = 0
        currMax = 0
        for oppFold in self.game.opponentFold:
            if oppFold.name == player_name:
                pass
            elif self.game.opponentFold[oppFold] > currMax:
                currMax = self.game.opponentFold[oppFold]
        if self.game.rounds == 0:
            return perc
        return (currMax / self.game.rounds)

    def autoProfit(self, currentBet: int, player_name : str):
        """
        Check if player will profit regardless of opponent 
        or player hand
        """
        breakEvenPer = self.breakEven(currentBet)
        oppFoldPer = self.calcOpponentFold(player_name)
        return oppFoldPer > breakEvenPer