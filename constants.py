

reelsetSymbolsCount = {
    "AA" : [2,2,2,2,2],
    "BB" : [2,4,2,4,2],
    "CC" : [4,2,4,2,4],
    "DD" : [4,2,4,4,6],
    "EE" : [4,6,4,6,4],
    "FF" : [8,8,6,8,6],
    "GG" : [10,8,6,8,6],
    "HH" : [12,8,8,10,8],
    "WW" : [4,4,2,4,4],
    "SS" : [6,4,4,6,6],
}

paytable = {
    "AA" : [50,100,200],
    "BB" : [40,80,150],
    "CC" : [35,60,100],
    "DD" : [25,50,80],
    "EE" : [15,35,60],
    "FF" : [12,25,40],
    "GG" : [9,20,30],
    "HH" : [7,15,25],
    "WW" : [0,0,0],
    "SS" : [0,0,0],
}
basebet = 20
excelFilePath = "3x3practice.xlsx"

paylines = [
    [1, 1, 1, 1, 1],  # 1  - Middle straight
    [0, 0, 0, 0, 0],  # 2  - Top straight
    [2, 2, 2, 2, 2],  # 3  - Bottom straight
    [0, 1, 2, 1, 0],  # 4  - V-shape
    [2, 1, 0, 1, 2],  # 5  - Inverted V
    [0, 0, 1, 2, 2],  # 6  - Diagonal down
    [2, 2, 1, 0, 0],  # 7  - Diagonal up
    [0, 1, 1, 1, 2],  # 8  - Slight down
    [2, 1, 1, 1, 0],  # 9  - Slight up
    [1, 0, 0, 0, 1],  # 10 - Top dip
    [1, 2, 2, 2, 1],  # 11 - Bottom dip
    [0, 0, 0, 1, 1],  # 12 - Step down right
    [2, 2, 2, 1, 1],  # 13 - Step up right
    [1, 0, 1, 2, 1],  # 14 - Zigzag up
    [1, 2, 1, 0, 1],  # 15 - Zigzag down
    [0, 1, 2, 2, 1],  # 16 - Down then flat
    [2, 1, 0, 0, 1],  # 17 - Up then flat
    [0, 0, 1, 1, 2],  # 18 - Double step down
    [2, 2, 1, 1, 0],  # 19 - Double step up
    [1, 1, 0, 1, 1],  # 20 - Top bump
]