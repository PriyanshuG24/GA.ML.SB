from utils.digit_detector9x9 import detect_digits_from_image
from utils.sudoku_utils import solve_sudoku, solve_sudoku_16x16, solve_sudoku_9x9
from utils.digit_detector16x16 import detect_digits_from_image16x16
import copy  # Add this import

def solve_sudoku_image9x9(image_file, size=9):
    grid = detect_digits_from_image(image_file, size=9)
    grid1 = copy.deepcopy(grid)
    solved_grid = solve_sudoku(grid) 
    return grid1, solved_grid
    
def solve_sudoku_image16x16(image_file, size=16):
    # grid = detect_digits_from_image16x16(image_file, size=16)
    grid=[
        [5, 7, 0, 15, 12, 0, 0, 3, 0, 4, 11, 10, 14, 16, 6, 1],
        [6, 0, 14, 0, 10, 4, 7, 0, 0, 13, 15, 16, 9, 5, 8, 11],
        [0, 9, 0, 4, 0, 15, 6, 0, 14, 7, 0, 5, 0, 0, 10, 12],
        [2, 10, 0, 8, 14, 5, 16, 0, 1, 6, 12, 9, 0, 15, 4, 7],
        [10, 12, 0, 0, 1, 11, 13, 5, 4, 9, 6, 0, 16, 0, 2, 0],
        [15, 0, 16, 0, 8, 7, 0, 6, 0, 0, 14, 0, 12, 0, 11, 4],
        [3, 6, 1, 0, 0, 0, 4, 9, 5, 12, 0, 0, 10, 14, 7, 0],
        [4, 13, 8, 9, 2, 12, 3, 14, 0, 0, 16, 11, 5, 1, 0, 0],
        [0, 0, 9, 16, 0, 0, 15, 7, 10, 0, 5, 12, 0, 6, 13, 2],
        [12, 15, 0, 10, 13, 1, 5, 0, 0, 0, 0, 6, 11, 7, 9, 3],
        [0, 3, 0, 13, 9, 6, 0, 10, 11, 15, 0, 0, 8, 0, 0, 0],
        [0, 4, 6, 0, 3, 0, 11, 8, 9, 16, 1, 13, 0, 0, 5, 10],
        [8, 11, 10, 0, 16, 13, 14, 0, 6, 5, 9, 7, 0, 2, 1, 15],
        [13, 16, 0, 2, 6, 0, 1, 11, 0, 8, 3, 4, 0, 0, 14, 5],
        [9, 5, 12, 0, 7, 10, 2, 4, 0, 0, 0, 0, 6, 8, 0, 16],
        [7, 14, 4, 6, 5, 3, 8, 0, 16, 2, 0, 1, 13, 11, 12, 9]
    ]
    if size == 16:
        return solve_sudoku_16x16(grid)
    else:
        raise ValueError("Unsupported Sudoku size")
