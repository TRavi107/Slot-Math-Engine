from openpyxl import load_workbook
from constants import excelFilePath

def get_col_data(col: int) -> list:
    wb = load_workbook(excelFilePath, data_only=True)
    ws = wb.active
    
    return [
        ws.cell(row=row, column=col).value
        for row in range(1, ws.max_row + 1)
        if ws.cell(row=row, column=col).value is not None
    ]

def collect_col_data():
    reels =[]
    for i in range(1,6):
        data = get_col_data(i)
        reels.append(data)

    return reels