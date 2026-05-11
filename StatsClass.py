from dataclasses import dataclass , field

@dataclass
class ReelMatrixData:
    SPINCOUNT: int
    BASEBET: int

    totalWins: float = 0
    winningSpins: int = 0
    hitRate: float = 0
    rtp: float = 0
    symbolsData: dict[str,SymbolsData] = field (default_factory=dict)
    winDistribution: dict[str,int] = field (default_factory=dict)

    def __add__(self, other):
        all_symbol_keys = set(self.symbolsData.keys()) | set(other.symbolsData.keys())
        sumSymbolsData = {
            key: self.symbolsData.get(key, SymbolsData(key,self.SPINCOUNT,self.BASEBET)) + 
                                            other.symbolsData.get(key, SymbolsData(key,self.SPINCOUNT,self.BASEBET))
            for key in all_symbol_keys
        }

        all_win_keys = set(self.winDistribution.keys()) | set(other.winDistribution.keys())
        winDistributionData = {
            key: self.winDistribution.get(key, 0) + other.winDistribution.get(key, 0)
            for key in all_win_keys
        }

        return ReelMatrixData(
            SPINCOUNT=self.SPINCOUNT,
            BASEBET=self.BASEBET,
            totalWins=self.totalWins + other.totalWins,
            winningSpins=self.winningSpins + other.winningSpins,
            symbolsData=sumSymbolsData,
            winDistribution=winDistributionData
        )

    def calculate(self):
        self.rtp = self.totalWins/(self.BASEBET*self.SPINCOUNT)
        self.hitRate = self.SPINCOUNT/max(self.winningSpins,1)
        for symbol in self.symbolsData.values():
            symbol.calculate()

    def updateSymbolsData(self,currentWin:float,symbol:str):
        if(currentWin==0):
            return

        symbolData = self.get_or_create_symbolsData(symbol)

        symbolData.winSpinsCount +=1
        symbolData.totalWins += currentWin
    
    def updateWinnings(self,currentWin:float):
        if(currentWin==0):
            return
        self.totalWins +=currentWin
        self.winningSpins +=1
        winMultiplier = currentWin/self.BASEBET

        if(winMultiplier <1):
            self.winDistribution["0-1"] = self.winDistribution.get("0-1",0) +1
        elif(winMultiplier >1 and winMultiplier <2):
            self.winDistribution["1-2"] = self.winDistribution.get("1-2",0) +1
        elif(winMultiplier >2 and winMultiplier <3):
            self.winDistribution["2-3"] = self.winDistribution.get("2-3",0) +1
        elif(winMultiplier >3 and winMultiplier <5):
            self.winDistribution["3-5"] = self.winDistribution.get("3-5",0) +1
        elif(winMultiplier >5 and winMultiplier <10):
            self.winDistribution["5-10"] = self.winDistribution.get("5-10",0) +1
        elif(winMultiplier >10 and winMultiplier <20):
            self.winDistribution["10-20"] = self.winDistribution.get("10-20",0) +1
        elif(winMultiplier >20 and winMultiplier <50):
            self.winDistribution["20-50"] = self.winDistribution.get("20-50",0) +1
        else:
            self.winDistribution["50+"] = self.winDistribution.get("50+",0) +1

    def get_or_create_symbolsData(self, symbol: str) -> SymbolsData:
        return self.symbolsData.setdefault(
            symbol,
            SymbolsData(SYMBOL=symbol, TOTALSPINS=self.SPINCOUNT, BASEBET=self.BASEBET)
        )
    

    
    
@dataclass
class BaseMatrixData(ReelMatrixData):
    pass

@dataclass
class SymbolsData:
    SYMBOL:str
    TOTALSPINS: int
    BASEBET: int

    winSpinsCount: int =0
    totalWins:float = 0
    hitrate:float = 0
    rtp: float = 0

    def __add__(self, other):
        return SymbolsData(
            SYMBOL= self.SYMBOL,
            TOTALSPINS=self.TOTALSPINS,
            BASEBET=self.BASEBET,
            winSpinsCount= self.winSpinsCount + other.winSpinsCount,
            totalWins= self.totalWins + other.totalWins
        )

    def calculate(self):
        self.hitrate = (self.TOTALSPINS/self.winSpinsCount)
        self.rtp = self.totalWins/(self.TOTALSPINS*self.BASEBET)
    
