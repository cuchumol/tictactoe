
'''
BOARD
    0  1  2   
 0  0  1  2   
 1  3  4  5 
 2  6  7  8
'''

def create_board():
    return [' '] * 9




def check_winner(board):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # горизонталь
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # вертикаль
        [0, 4, 8], [2, 4, 6], # диагональ
    ]
    for line in lines:
        if board[line[0]] == board[line[1]] == board[line[2]] != ' ':
            return board[line[0]]
    return None



class TicTacToe:
    def __init__(self):
        self.board = create_board()
        self.current_move_index = None

    def clear_board(self):
        self.board = create_board()

    
    def next_states(self, board, player):
        states = []
        for i in range(9):
            if board[i] == ' ':
                new_board = board[:]
                new_board[i] = player
                states.append(new_board)
        return states
    

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        winner = check_winner(board)
        if winner == 'X':
            return -1
        elif winner == 'O':
            return 1
        elif ' ' not in board:
            return 0

        if maximizing_player:
            max_eval = float('-inf')
            for next_board in self.next_states(board, 'O'):
                eval = self.minimax(next_board, depth + 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for next_board in self.next_states(board, 'X'):
                eval = self.minimax(next_board, depth + 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval



    def user_move(self, coord, player):
        self.board[coord] = player
    
    def computer_move(self):
        best_move = None
        best_value = float('-inf')
        for next_board in self.next_states(self.board, 'O'):
            value = self.minimax(next_board, 0, float('-inf'), float('inf'), False)
            if value > best_value:
                best_value = value
                best_move = next_board
        
        for i in range(len(self.board)):
            if self.board[i] != best_move[i]:
                self.current_move_index = i
                break

        self.board = best_move
        return self.current_move_index

