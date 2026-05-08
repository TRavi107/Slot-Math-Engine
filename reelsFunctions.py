from openpyxl import load_workbook
from constants import excelFilePath
import random

def get_col_data(col: int) -> list:
    wb = load_workbook(excelFilePath, data_only=True)
    ws = wb.active
    
    return [
        ws.cell(row=row, column=col).value
        for row in range(2, ws.max_row + 1)
        if ws.cell(row=row, column=col).value is not None
    ]

def collect_col_data():
    reels =[]
    for i in range(1,6):
        data = get_col_data(i)
        reels.append(data)

    return reels

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

