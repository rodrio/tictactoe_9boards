from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

class TicTacToe9Boards:
    def __init__(self):
        # Initialize 9 individual boards (3x3 each)
        self.boards = [[['' for _ in range(3)] for _ in range(3)] for _ in range(9)]
        # Initialize main board (3x3)
        self.main_board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        
    def make_move(self, board_idx, row, col):
        if self.game_over:
            return False
            
        board_row = board_idx // 3
        board_col = board_idx % 3
        
        # Check if the move is valid
        if self.boards[board_idx][row][col] != '':
            return False
            
        # Make the move
        self.boards[board_idx][row][col] = self.current_player
        
        # Check if this move wins the individual board
        if self.check_board_winner(board_idx):
            self.main_board[board_row][board_col] = self.current_player
            
            # Check if this wins the main game
            if self.check_main_winner():
                self.game_over = True
                self.winner = self.current_player
                return True
        
        # Check for draw in individual board
        if self.is_board_full(board_idx) and not self.check_board_winner(board_idx):
            self.main_board[board_row][board_col] = 'D'
            
        # Check for draw in main board
        if self.is_main_board_full() and not self.check_main_winner():
            self.game_over = True
            self.winner = 'Draw'
        
        # Switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True
    
    def check_board_winner(self, board_idx):
        board = self.boards[board_idx]
        
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != '':
                return True
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != '':
                return True
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != '':
            return True
        if board[0][2] == board[1][1] == board[2][0] != '':
            return True
        
        return False
    
    def check_main_winner(self):
        # Check rows
        for row in self.main_board:
            if row[0] == row[1] == row[2] != '' and row[0] != 'D':
                return True
        
        # Check columns
        for col in range(3):
            if self.main_board[0][col] == self.main_board[1][col] == self.main_board[2][col] != '' and self.main_board[0][col] != 'D':
                return True
        
        # Check diagonals
        if self.main_board[0][0] == self.main_board[1][1] == self.main_board[2][2] != '' and self.main_board[0][0] != 'D':
            return True
        if self.main_board[0][2] == self.main_board[1][1] == self.main_board[2][0] != '' and self.main_board[0][2] != 'D':
            return True
        
        return False
    
    def is_board_full(self, board_idx):
        for row in self.boards[board_idx]:
            for cell in row:
                if cell == '':
                    return False
        return True
    
    def is_main_board_full(self):
        for row in self.main_board:
            for cell in row:
                if cell == '':
                    return False
        return True
    
    def get_board_winner(self, board_idx):
        if self.check_board_winner(board_idx):
            # Find who won
            board = self.boards[board_idx]
            # Check rows
            for row in board:
                if row[0] == row[1] == row[2] != '':
                    return row[0]
            # Check columns
            for col in range(3):
                if board[0][col] == board[1][col] == board[2][col] != '':
                    return board[0][col]
            # Check diagonals
            if board[0][0] == board[1][1] == board[2][2] != '':
                return board[0][0]
            if board[0][2] == board[1][1] == board[2][0] != '':
                return board[0][2]
        elif self.is_board_full(board_idx):
            return 'D'
        return None
    
    def reset_game(self):
        self.__init__()

# Global game instance
game = TicTacToe9Boards()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game_state')
def get_game_state():
    return jsonify({
        'boards': game.boards,
        'main_board': game.main_board,
        'current_player': game.current_player,
        'game_over': game.game_over,
        'winner': game.winner
    })

@app.route('/api/make_move', methods=['POST'])
def make_move():
    data = request.json
    board_idx = data['board_idx']
    row = data['row']
    col = data['col']
    
    success = game.make_move(board_idx, row, col)
    
    return jsonify({
        'success': success,
        'game_state': {
            'boards': game.boards,
            'main_board': game.main_board,
            'current_player': game.current_player,
            'game_over': game.game_over,
            'winner': game.winner
        }
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    game.reset_game()
    return jsonify({
        'game_state': {
            'boards': game.boards,
            'main_board': game.main_board,
            'current_player': game.current_player,
            'game_over': game.game_over,
            'winner': game.winner
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
