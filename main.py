import random
from reelsFunctions import collect_col_data
from constants import paylines , paytable , basebet
import timeit

reels = collect_col_data()

def generate_slot_matrix() -> list[list[str]]:
    """Generate a 3x5 matrix from 5 reel columns."""
    matrix = []
    
    for col in range(5):  # 5 reels
        reel = reels[col]  # your existing function
        
        max_start = len(reel) - 3
        start_idx = random.randint(0, max_start)
        window = reel[start_idx : start_idx + 3]  # 3 consecutive symbols
        
        matrix.append(window)
    
    # matrix is currently 5 cols x 3 rows, transpose to 3 rows x 5 cols
    matrix_3x5 = list(map(list, zip(*matrix)))
    return matrix_3x5

def check_paylines(matrix: list[list[str]], paylines: list[list[int]]) -> (dict,int):
    """
    Check which paylines match (3+ consecutive same symbols from left).
    
    matrix  : 3 rows x 5 cols  → matrix[row][col]
    paylines: each payline is 5 row-indices (one per reel/col)
    """
    results = {}
    totalWin= 0

    for i, payline in enumerate(paylines, start=1):
        # Extract symbols along this payline
        symbols = [matrix[row][col] for col, row in enumerate(payline)]

        # Count consecutive matches from left
        match_count = 1
        for j in range(1, len(symbols)):
            if symbols[j] == symbols[0]:
                match_count += 1
            else:
                break

        results[i] = {
            "symbols"    : symbols,
            "match"      : match_count >= 3,
            "match_count": match_count if match_count >= 3 else 0,
            "symbol"     : symbols[0] if match_count >= 3 else None,
            "payout"     : paytable[symbols[0]][match_count-3] if match_count >=3 else 0
        }
        totalWin += results[i]['payout']

    return results,totalWin

def runSim(spinCount: int)->int:
    totalWin =0
    for i in range (spinCount):

        matrix = generate_slot_matrix()

        # for row in matrix:
        #     print(row)

        results,spinWin = check_paylines(matrix, paylines)

        # for line_num, result in results.items():
        #     if result["match"]:
        #         print(f"Payline {line_num}: {result['match_count']}x {result['symbol']} → {result['symbols']} win: {result['payout']}")

        # print(f"Spin win : {spinWin}")
        totalWin +=spinWin
    return totalWin

spinCount =10000000
totalWin = runSim(spinCount)
totalBet = basebet*spinCount

# execution_time = timeit.timeit(
#     lambda: runSim(1),
#     number=1000000
# )

# print(execution_time)

print(f"Total win: {totalWin} ")
print(f"Total bet: {totalBet} ")
print(f"RTP : {totalWin/totalBet*100} %")