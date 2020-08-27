from copy import deepcopy

from base import context

# These will be used in the GUI to let the user know why their board is invalid
ERROR_CODES = {
    0: "No error",
    1: "Duplicate value in row",
    2: "Duplicate value in column",
    3: "Duplicate value in subgrid",
    4: "Value out of range"
}

board_states = []

def save_board_state(input_board):
    board_states.append(deepcopy(input_board))

def initialise_board_states():
    global board_states
    board_states = []

def get_board_states():
    return board_states

def solve(board, board_size, subgrid_height, subgrid_width):
    empty_cell_found = find_empty_cell(board)
    # If algorithm has reached the end and the board is full, it is solved
    if not empty_cell_found:
        return True
    else:
        row, col = empty_cell_found

    for i in range(1, board_size + 1):  # Available nums (1-9 for a 9x9 board)
        if is_valid(board, i, row, col, subgrid_height, subgrid_width)[0]:
            board[row][col] = i  # If a number works, put it in the board
            save_board_state(board)

            # Try to solve with the new board
            if solve(board, board_size, subgrid_height, subgrid_width):
                return True

            board[row][col] = 0

    return False


def return_list_of_empty_cells(board):
    """Traverse the board and return a tuple of positions of empty cells
        Not used in the solving algorithm, but useful for the GUI
    """
    return [(i, j) for i in range(len(board)) for j in range(len(board[i]))
            if board[i][j] == 0]


def find_empty_cell(board):
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                return (i, j)

    return False


def is_valid(board, test_value, row, col, subgrid_height, subgrid_width):
    """If test_value satisfies the constraints of the puzzle, return True
        Otherwise return False
    """
    # Check row
    for i in range(len(board)):
        if board[row][i] == test_value and i != col:
            return False, ERROR_CODES[1]

    # Check column
    for i in range(len(board)):
        if board[i][col] == test_value and i != row:
            return False, ERROR_CODES[2]

    # Check subgrid
    if subgrid_height != 0:
        subgrid_x = (row // subgrid_height) * subgrid_height
        subgrid_y = (col // subgrid_width) * subgrid_width
        for i in range(subgrid_x, subgrid_x + subgrid_height):
            for j in range(subgrid_y, subgrid_y + subgrid_width):
                if board[i][j] == test_value and (i, j) != (row, col):
                    return False, ERROR_CODES[3]

    # All checks passed
    return True, ERROR_CODES[0]


def validate_board(board, board_size, subgrid_height, subgrid_width):
    """Check if given board is valid and can be solved
        Return either True or False
    """
    # First check that every number is within range
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] > board_size:
                return (False, ERROR_CODES[4], i, j)

    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] != 0:
                valid = is_valid(board, board[i][j], i, j, subgrid_height, subgrid_width)
                if not valid[0]:
                    return (valid[0], valid[1], i, j)

    return True, ERROR_CODES[0]


def main(BOARD, board_size, subgrid_height=0, subgrid_width=0):
    # Make a copy of BOARD
    # We can't use board = BOARD, because Python has no block scope and is pass-by-object
    # This means that modifying the board variable here will modify the original, which we don't want
    # Copying over each value solves this problem, though it may not be the most Pythonic way to do it
    board = []
    for i in range(board_size):
        row = []
        for j in range(board_size):
            row.append(BOARD[i][j])
        board.append(row)

    initialise_board_states()
    solve(board, board_size, subgrid_height, subgrid_width)
    return board
