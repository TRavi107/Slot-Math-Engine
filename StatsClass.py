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

        return self.__class__(
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

    def updateSymbolsData(self,currentWin:float,winningComCount:int,symbol:str):
        if(currentWin==0):
            return

        symbolData = self.get_or_create_symbolsData(symbol)

        symbolData.winSpinsCount +=1
        match winningComCount:
            case 3:
                symbolData.winning3OK +=1
            case 4:
                symbolData.winning4OK +=1
            case 5:
                symbolData.winning5OK +=1
            case _:
                print(f"winning com count is {winningComCount} for {symbol}")

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
class FreeMatrixData(ReelMatrixData):
    freeSpinsCount: int = 0
    
    def __add__(self, other):
        result = super().__add__(other)
        result.freeSpinsCount = self.freeSpinsCount + other.freeSpinsCount 
        return result

    def AddFreeSpins(self,spins:int):
        self.freeSpinsCount +=spins

@dataclass
class SymbolsData:
    SYMBOL:str
    TOTALSPINS: int
    BASEBET: int

    winSpinsCount: int =0
    winning3OK : int =0
    winning4OK : int =0
    winning5OK : int =0
    hitrate3OK : float =0
    hitrate4OK : float =0
    hitrate5OK : float =0
    totalWins:float = 0
    hitrate:float = 0
    rtp: float = 0

    def __add__(self, other):
        return SymbolsData(
            SYMBOL= self.SYMBOL,
            TOTALSPINS=self.TOTALSPINS,
            BASEBET=self.BASEBET,
            winSpinsCount= self.winSpinsCount + other.winSpinsCount,
            totalWins= self.totalWins + other.totalWins,
            winning3OK=self.winning3OK+other.winning3OK,
            winning4OK=self.winning4OK+other.winning4OK,
            winning5OK=self.winning5OK+other.winning5OK
        )

    def calculate(self):
        self.hitrate = (self.TOTALSPINS/self.winSpinsCount)
        self.rtp = self.totalWins/(self.TOTALSPINS*self.BASEBET)
        self.hitrate3OK = self.TOTALSPINS/(self.winning3OK if self.winning3OK else 1)
        self.hitrate4OK = self.TOTALSPINS/(self.winning4OK if self.winning4OK else 1)
        self.hitrate5OK = self.TOTALSPINS/(self.winning5OK if self.winning5OK else 1)
    
