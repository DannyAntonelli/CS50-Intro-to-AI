"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count, o_count = 0, 0

    for row in board:
        x_count += row.count(X)
        o_count += row.count(O)

    if x_count > o_count:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    act = set()

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                act.add((i, j))

    return act


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid action")

    new_board = [row[:] for row in board]
    i, j = action[0], action[1]
    new_board[i][j] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]

    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]

    if board[0][0] == board[1][1] == board[2][2] or board[2][0] == board[1][1] == board[0][2]:
        return board[1][1]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True

    for row in board:
        if EMPTY in row:
            return False
    
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    res = winner(board)
    if res == X:
        return 1
    elif res == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        return max_value(board, -1, 1)[1]
    return min_value(board, -1, 1)[1]


def max_value(board, curr_max, curr_min):
    """
    Returns the value and the move that maximize the score
    """
    if terminal(board):
        return utility(board), None

    value, action = -1, None

    for a in actions(board):
        v = min_value(result(board, a), curr_max, curr_min)[0]
        curr_max = max(curr_max, v)

        if v >= curr_min:
            return v, a

        if v > value:
            value, action = v, a
            
    return value, action


def min_value(board, curr_max, curr_min):
    """
    Return the value and the move that minimize the score
    """
    if terminal(board):
        return utility(board), None

    value, action = 1, None

    for a in actions(board):
        v = max_value(result(board, a), curr_max, curr_min)[0]
        curr_min = min(curr_min, v)

        if v <= curr_max:
            return v, a

        if v < value:
            value, action = v, a

    return value, action