from flask import Flask, render_template, jsonify, request
import json
import os
from google import genai

app = Flask(__name__)

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash-lite-preview-0617')
    AI_ENABLED = True
except Exception as e:
    print(f"Warning: Gemini API not configured. AI mode will be disabled. Error: {e}")
    AI_ENABLED = False

class TicTacToe9Boards:
    def __init__(self):
        # Initialize 9 individual boards (3x3 each)
        self.boards = [[['' for _ in range(3)] for _ in range(3)] for _ in range(9)]
        # Initialize main board (3x3)
        self.main_board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.game_mode = '1-player'  # '1-player' or '2-players'
        self.ai_thinking = False
        
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
    
    def reset_game(self, game_mode='1-player'):
        self.game_mode = game_mode
        self.boards = [[['' for _ in range(3)] for _ in range(3)] for _ in range(9)]
        self.main_board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
    
    def set_game_mode(self, mode):
        if mode in ['1-player', '2-players']:
            self.game_mode = mode
    
    def is_ai_turn(self):
        return self.game_mode == '1-player' and self.current_player == 'O' and not self.game_over
    
    def board_to_text(self):
        """Convert the current board state to a text representation for the AI"""
        text = "9-Boards Tic-Tac-Toe Current State:\n\n"
        
        # Main board status
        text += "Main Board (shows winners of individual boards):\n"
        for row in range(3):
            row_text = ""
            for col in range(3):
                val = self.main_board[row][col]
                if val == '':
                    row_text += "[ ] "
                elif val == 'D':
                    row_text += "[D] "
                else:
                    row_text += f"[{val}] "
            text += row_text.rstrip() + "\n"
        
        text += "\nIndividual Boards:\n"
        for board_idx in range(9):
            text += f"\nBoard {board_idx + 1} (Position {chr(65 + board_idx)}):\n"
            board = self.boards[board_idx]
            for row in board:
                row_text = ""
                for cell in row:
                    if cell == '':
                        row_text += ". "
                    else:
                        row_text += cell + " "
                text += row_text.rstrip() + "\n"
        
        text += f"\nCurrent Player: {self.current_player}\n"
        text += f"Game Mode: {self.game_mode}\n"
        
        return text
    
    def get_ai_move(self):
        """Get AI move using Gemini API"""
        if not AI_ENABLED:
            # Fallback: make a random valid move
            return self.get_random_move()
        
        try:
            board_text = self.board_to_text()
            
            prompt = f"""
You are playing 9-Boards Tic-Tac-Toe. Here are the rules:

1. There are 9 individual 3x3 boards arranged in a 3x3 grid
2. Players can place their mark (X or O) in any empty cell of any board
3. Winning an individual board claims that position in the main board
4. Winning 3 boards in a row on the main board wins the game
5. You are playing as O, the current player

Current board state:
{board_text}

Analyze the board and suggest the best move. Consider:
- Winning individual boards
- Blocking opponent from winning boards
- Strategic positioning on the main board
- Blocking opponent's main board wins

Respond with ONLY the move in format: "board_idx,row,col" (e.g., "4,1,2" for board 5, row 2, column 3)
Make sure the chosen cell is empty (marked with "." in the individual boards).
"""
            
            response = model.generate_content(prompt)
            move_text = response.text.strip()
            
            # Parse the response
            if ',' in move_text:
                parts = move_text.split(',')
                if len(parts) == 3:
                    try:
                        board_idx = int(parts[0])
                        row = int(parts[1])
                        col = int(parts[2])
                        
                        # Validate the move
                        if (0 <= board_idx <= 8 and 0 <= row <= 2 and 0 <= col <= 2 and 
                            self.boards[board_idx][row][col] == ''):
                            return board_idx, row, col
                    except ValueError:
                        pass
            
            # If AI response is invalid, make a random move
            return self.get_random_move()
            
        except Exception as e:
            print(f"AI move error: {e}")
            return self.get_random_move()
    
    def get_random_move(self):
        """Fallback: make a random valid move"""
        valid_moves = []
        for board_idx in range(9):
            for row in range(3):
                for col in range(3):
                    if self.boards[board_idx][row][col] == '':
                        valid_moves.append((board_idx, row, col))
        
        if valid_moves:
            import random
            return random.choice(valid_moves)
        
        return None

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
        'winner': game.winner,
        'game_mode': game.game_mode,
        'ai_thinking': game.ai_thinking,
        'ai_enabled': AI_ENABLED
    })

@app.route('/api/make_move', methods=['POST'])
def make_move():
    data = request.json
    board_idx = data['board_idx']
    row = data['row']
    col = data['col']
    
    success = game.make_move(board_idx, row, col)
    
    response_data = {
        'success': success,
        'game_state': {
            'boards': game.boards,
            'main_board': game.main_board,
            'current_player': game.current_player,
            'game_over': game.game_over,
            'winner': game.winner,
            'game_mode': game.game_mode,
            'ai_thinking': game.ai_thinking,
            'ai_enabled': AI_ENABLED
        }
    }
    
    # If it's AI's turn next and game is not over
    if success and game.is_ai_turn():
        game.ai_thinking = True
        response_data['game_state']['ai_thinking'] = True
        
        # Make AI move
        ai_move = game.get_ai_move()
        if ai_move:
            ai_board_idx, ai_row, ai_col = ai_move
            game.make_move(ai_board_idx, ai_row, ai_col)
            
            response_data['ai_move'] = {
                'board_idx': ai_board_idx,
                'row': ai_row,
                'col': ai_col
            }
            
            # Update game state after AI move
            response_data['game_state'] = {
                'boards': game.boards,
                'main_board': game.main_board,
                'current_player': game.current_player,
                'game_over': game.game_over,
                'winner': game.winner,
                'game_mode': game.game_mode,
                'ai_thinking': False,
                'ai_enabled': AI_ENABLED
            }
    
    return jsonify(response_data)

@app.route('/api/reset', methods=['POST'])
def reset_game():
    data = request.json or {}
    game_mode = data.get('game_mode', '1-player')
    game.reset_game(game_mode)
    return jsonify({
        'game_state': {
            'boards': game.boards,
            'main_board': game.main_board,
            'current_player': game.current_player,
            'game_over': game.game_over,
            'winner': game.winner,
            'game_mode': game.game_mode,
            'ai_thinking': game.ai_thinking,
            'ai_enabled': AI_ENABLED
        }
    })

@app.route('/api/set_game_mode', methods=['POST'])
def set_game_mode():
    data = request.json
    game_mode = data.get('game_mode', '1-player')
    game.set_game_mode(game_mode)
    return jsonify({
        'game_state': {
            'boards': game.boards,
            'main_board': game.main_board,
            'current_player': game.current_player,
            'game_over': game.game_over,
            'winner': game.winner,
            'game_mode': game.game_mode,
            'ai_thinking': game.ai_thinking,
            'ai_enabled': AI_ENABLED
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
