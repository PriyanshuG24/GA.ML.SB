# Keep your existing 9x9 logic
def solve_sudoku(grid):
    def is_valid(r, c, num):
        for i in range(9):
            if grid[r][i] == num or grid[i][c] == num or grid[r//3*3 + i//3][c//3*3 + i%3] == num:
                return False
        return True

    def backtrack(r=0, c=0):
        if r == 9:
            return True
        if grid[r][c] != 0:
            return backtrack(r + (c+1)//9, (c+1)%9)
        for num in range(1, 10):
            if is_valid(r, c, num):
                grid[r][c] = num
                if backtrack(r + (c+1)//9, (c+1)%9):
                    return True
                grid[r][c] = 0
        return False

    if backtrack():
        return grid
    else:
        raise Exception("Sudoku cannot be solved")
    
from .geneticAlgoFor9x9 import Sudoku

def solve_sudoku_9x9(grid):
    s = Sudoku()
    s.load_grid(grid)
    solution = s.solve()
    return solution.values.tolist()
from .geneticAlgoFor16x16 import Sudoku

def solve_sudoku_16x16(grid):
    s = Sudoku()
    s.load_grid(grid)
    solution = s.solve()
    return solution.values.tolist()
