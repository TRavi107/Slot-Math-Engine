from reelsFunctions import generate_slot_matrix
from constants import paylines , paytable , basebet
from UtilityFunc import print_progress
from StatsClass import BaseMatrixData

import concurrent.futures
import os
import math
import time
import multiprocessing

def check_paylines(matrix: list[list[str]], paylines: list[list[int]], baseReelMatrix:BaseMatrixData):
    
    results = {}
    totalWin= 0
   
    for i, payline in enumerate(paylines, start=1):
        # Extract symbols along this payline
        symbols = [matrix[row][col] for col, row in enumerate(payline)]

        # skip for scatter symbols on payline
        if symbols[0]=="SS":
            continue

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

        baseReelMatrix.updateSymbolsData(results[i]['payout'],symbols[0])
    baseReelMatrix.updateWinnings(totalWin)

    return results,totalWin

def check_scatter(matrix: list[list[str]]):
    row = len(matrix)
    col = len(matrix[0])
    scatterCount = 0
    #check for consecutive ss symbol on any row of first col
    for j in range(col):
        hasScatter = False
        for i in range(row):
            if(matrix[i][j])=="SS":
                scatterCount +=1
                hasScatter = True # count single scatter per col even multiple are present
                break
        if (not hasScatter):
            break
            
    return scatterCount

def runSim(spinCount: int)->int:
    baseReelMatrix  = BaseMatrixData(spinCount,basebet)
    scatterWinCount = 0
    for i in range (spinCount):

        matrix = generate_slot_matrix()

        # matrix = [
        #     ["SS", "BB", "CC", "SS", "EE"],  # SS in col 3
        #     ["WW", "AA", "GG", "HH", "AA"],  # SS in col 1
        #     ["SS", "CC", "SS", "WW", "DD"],  # SS in col 2
        # ]

        check_paylines(matrix, paylines, baseReelMatrix)
        scatterSymbolCount = check_scatter(matrix)

        if(scatterSymbolCount>=3):
            #goto free game
            scatterWinCount +=1


    return baseReelMatrix , scatterWinCount

def runSim_chunked(args):
    """Run a chunk of spins, reporting progress via a queue every 10%"""
    spins, queue = args
    milestone_size = spins // 10  # report every 10% of THIS worker's chunk
    
    scatterWinCount = 0

    baseReelMatrix  = BaseMatrixData(spins,basebet)

    next_milestone    = milestone_size

    # Call runSim in sub-chunks instead of 1 spin at a time
    remaining = spins
    done      = 0

    while remaining > 0:
        batch       = min(milestone_size, remaining)
        baseReelMatrixData ,scatterSymbolCount  = runSim(batch)
        baseReelMatrix = baseReelMatrix + baseReelMatrixData
        scatterWinCount =scatterWinCount+ scatterSymbolCount
       
        done      += batch
        remaining -= batch

        if done >= next_milestone:
            queue.put(done - (next_milestone - milestone_size))  # spins completed
            next_milestone += milestone_size

    queue.put(done)  # final flush
    # print(baseReelMatrix)
    return baseReelMatrix, scatterWinCount

if __name__ == '__main__':
    start = time.perf_counter()
    

    spinCount = 2000000
    baseMatrixData = BaseMatrixData(spinCount,basebet)

    max_workers = max(1, math.floor(os.cpu_count() * 0.8))
    
    spins_per_worker = spinCount // max_workers
    remainder        = spinCount % max_workers
    chunks           = [spins_per_worker + (1 if i < remainder else 0) for i in range(max_workers)]
    manager = multiprocessing.Manager()
    prog_queue = manager.Queue()

    # # ✅ ProcessPoolExecutor — bypasses GIL, true parallel CPU execution
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

    for r in results:
        baseMatrixData = baseMatrixData+r[0]

    # baseMatrixData,_ = runSim(2000000)
    
    scatterWInCount = sum(r[1] for r in results)

    baseMatrixData.calculate()

    print(f"Total win: {baseMatrixData.totalWins} ")
    print(f"Total bet: {baseMatrixData.BASEBET*baseMatrixData.SPINCOUNT} ")
    print(f"RTP : {baseMatrixData.rtp:.4f} %")
    print(f"Hitrate : {baseMatrixData.hitRate} ")

    print(f"ScatterHitRate: {spinCount/(scatterWInCount if scatterWInCount>0 else 1)}")

    for symbols in sorted(baseMatrixData.symbolsData.values(), key=lambda s: s.SYMBOL):
        print(f"{symbols.SYMBOL:<10} {symbols.hitrate:>10.4f} {symbols.rtp:>10.4f}%")

    print (f"Time elapsed: {time.perf_counter() - start}")