from reelsFunctions import collect_col_data , generate_slot_matrix
from constants import paylines , paytable , basebet
from UtilityFunc import print_progress

from collections import defaultdict
import concurrent.futures
import os
import math
import time
import multiprocessing


def check_paylines(matrix: list[list[str]], paylines: list[list[int]]):
    """
    Check which paylines match (3+ consecutive same symbols from left).
    
    matrix  : 3 rows x 5 cols  → matrix[row][col]
    paylines: each payline is 5 row-indices (one per reel/col)
    """
    results = {}
    totalWin= 0
    symbolsWins = {
        "AA" : [0,0], # symbols wins and hits
        "BB" : [0,0],
        "CC" : [0,0],
        "DD" : [0,0],
        "EE" : [0,0],
        "FF" : [0,0],
        "GG" : [0,0],
        "HH" : [0,0],
        "WW" : [0,0],
        "SS" : [0,0],
    }

    for i, payline in enumerate(paylines, start=1):
        # Extract symbols along this payline
        symbols = [matrix[row][col] for col, row in enumerate(payline)]

        # Count consecutive matches from left
        match_count = 1
        for j in range(1, len(symbols)):
            if symbols[j] == symbols[0] or symbols[j] =="WW": # checkking for wild match
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

        if(results[i]["match"]):
            symbolsWins[symbols[0]] = [symbolsWins.get(symbols[0],[0,0])[0] + results[i]['payout'],symbolsWins.get(symbols[0],[0,0])[1]+1]

    return results,totalWin, symbolsWins

def runSim(spinCount: int)->int:
    totalWin =0
    
    totalWinningSpins= 0

    totalSymbolsWins = defaultdict(list)
    for i in range (spinCount):

        matrix = generate_slot_matrix()

        # for row in matrix:
        #     print(row)

        results,spinWin , spinSymbolsWin = check_paylines(matrix, paylines)

        if spinWin>0:
            totalWinningSpins +=1
            for key, val in spinSymbolsWin.items():
                totalSymbolsWins[key] = [totalSymbolsWins.get(key, [0,0])[0] + val[0],totalSymbolsWins.get(key, [0,0])[1] + val[1]]
                
            
        # for line_num, result in results.items():
        #     if result["match"]:
        #         print(f"Payline {line_num}: {result['match_count']}x {result['symbol']} → {result['symbols']} win: {result['payout']}")

        # print(f"Spin win : {spinWin}")
        totalWin +=spinWin
    return totalWin,totalWinningSpins , totalSymbolsWins

def runSim_chunked(args):
    """Run a chunk of spins, reporting progress via a queue every 10%"""
    spins, queue = args
    milestone_size = spins // 10  # report every 10% of THIS worker's chunk
    
    totalWin          = 0
    totalWinningSpins = 0
    totalSymbolWins = {}
    next_milestone    = milestone_size

    # Call runSim in sub-chunks instead of 1 spin at a time
    remaining = spins
    done      = 0

    while remaining > 0:
        batch       = min(milestone_size, remaining)
        win, isWin ,symbolWins  = runSim(batch)
        totalWin          += win
        totalWinningSpins += isWin
        for key, val in symbolWins.items():
                totalSymbolWins[key] =[ totalSymbolWins.get(key, [0,0])[0] + val[0],totalSymbolWins.get(key, [0,0])[1] + val[1]]
        done      += batch
        remaining -= batch

        if done >= next_milestone:
            queue.put(done - (next_milestone - milestone_size))  # spins completed
            next_milestone += milestone_size

    queue.put(done)  # final flush
    return totalWin, totalWinningSpins , totalSymbolWins

if __name__ == '__main__':
    start = time.perf_counter()
    
    spinCount = 2000000
    max_workers = max(1, math.floor(os.cpu_count() * 0.8))
    
    spins_per_worker = spinCount // max_workers
    remainder        = spinCount % max_workers
    chunks           = [spins_per_worker + (1 if i < remainder else 0) for i in range(max_workers)]
    manager = multiprocessing.Manager()
    prog_queue = manager.Queue()   # ← renamed from queue to prog_queue

    # ✅ ProcessPoolExecutor — bypasses GIL, true parallel CPU execution
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(runSim_chunked,  (chunk, prog_queue)) for chunk in chunks]

        # ── Progress monitor (main thread) ────────────────────────────
        completed     = 0
        last_printed  = -1
        total_reports = max_workers * 10  # each worker sends 10 updates

        while completed < total_reports:
            prog_queue.get()                          # blocks until a worker reports
            completed += 1
            total_done = int(completed / total_reports * spinCount)
            percent    = int((completed / total_reports) * 100)
            milestone  = (percent // 10) * 10

            if milestone > last_printed:
                last_printed = milestone
                print_progress(total_done, spinCount)


        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    totalWin          = sum(r[0] for r in results)
    totalWinningSpins = sum(r[1] for r in results)
    totalSymbolWins = {}
    for r in results:
        for key, val in r[2].items():
            totalSymbolWins[key] = [ totalSymbolWins.get(key, [0,0])[0] + val[0],totalSymbolWins.get(key, [0,0])[1] + val[1]]

    totalBet= basebet * spinCount
   
    print(f"Total win: {totalWin} ")
    print(f"Total bet: {totalBet} ")
    print(f"RTP : {totalWin/totalBet*100} %")
    print(f"Hitrate : {spinCount/totalWinningSpins} ")
    for sym, val in totalSymbolWins.items():
        print(f"{sym:<6} RTP={val[0]/totalBet*100:.4f}%")
    print(f"Scatter hit rate {spinCount/totalSymbolWins["SS"][1]}")
    print (f"Time elapsed: {time.perf_counter() - start}")