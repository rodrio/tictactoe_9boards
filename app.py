from flask import Flask, render_template, jsonify, request
import json
import os
import datetime
import logging
try:
    import google.genai as genai
except ImportError:
    genai = None
    print("Warning: google-genai not installed. AI features will be disabled.")

app = Flask(__name__)

# AI availability flag
AI_ENABLED = genai is not None

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
        self.difficulty = 'Noobie'  # 'Noobie', 'Average', 'Expert'
        self.ai_thinking = False
        self.api_key = None  # Store API key dynamically
        self.last_error = None
        self.turn_start_time = None  # Track when current turn started
        self.time_limit = 10  # 10 seconds per turn
        
    def make_move(self, board_idx, row, col):
        if self.game_over:
            self.last_error = "Game is over"
            return False
        
        # Check if turn has timed out
        if self.turn_start_time and self.is_turn_timed_out():
            self.last_error = "Turn timed out"
            self.switch_player()  # Lose turn due to timeout
            return False
            
        board_row = board_idx // 3
        board_col = board_idx % 3
        
        # Validate input ranges
        if not (0 <= board_idx <= 8 and 0 <= row <= 2 and 0 <= col <= 2):
            self.last_error = "Invalid position"
            return False
        
        # Check if move is valid
        if self.boards[board_idx][row][col] != '':
            self.last_error = "Cell already occupied"
            return False
        
        # Check if board is already won or drawn (closed)
        if self.main_board[board_row][board_col] != '':
            self.last_error = "Board is closed"
            return False
            
        # Make the move
        self.boards[board_idx][row][col] = self.current_player
        
        # Log the move for AI games
        if self.game_mode == '1-player':
            self.log_game_move(board_idx, row, col)
            
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
        self.switch_player()
        self.last_error = None
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
    
    def reset_game(self, game_mode='1-player', difficulty='Noobie'):
        self.game_mode = game_mode
        self.difficulty = difficulty
        self.boards = [[['' for _ in range(3)] for _ in range(3)] for _ in range(9)]
        self.main_board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        self.turn_start_time = None
        
        # Clear log file for new game
        self.clear_log_file()
    
    def set_game_mode(self, mode):
        if mode in ['1-player', '2-players']:
            self.game_mode = mode
    
    def set_difficulty(self, difficulty):
        if difficulty in ['Noobie', 'Average', 'Expert']:
            self.difficulty = difficulty
    
    def set_api_key(self, api_key):
        """Set the API key for AI (stored in memory only, not saved to files)"""
        self.api_key = api_key
    
    def clear_api_key(self):
        """Clear the API key (removes from memory only)"""
        self.api_key = None
    
    def get_ai_move(self):
        """Get AI move using Gemini API"""
        if not self.api_key:
            # No API key - use random moves
            return self.get_random_move()
        
        try:
            # Configure Gemini with the provided API key
            import google.genai as genai
            client = genai.Client(api_key=self.api_key)
            
            board_text = self.board_to_text()
            prompt = self.get_ai_prompt(board_text)
            
            # Log the prompt sent to Gemini
            self.log_ai_prompt(prompt)
            
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite-preview',
                contents=prompt
            )
            move_text = response.text.strip()
            
            # Log the response from Gemini
            self.log_ai_response(move_text)
            
            # Parse response
            if ',' in move_text:
                parts = move_text.split(',')
                if len(parts) == 3:
                    try:
                        board_idx = int(parts[0])
                        row = int(parts[1])
                        col = int(parts[2])
                        
                        # Validate move
                        if (0 <= board_idx <= 8 and 0 <= row <= 2 and 0 <= col <= 2 and 
                            self.boards[board_idx][row][col] == ''):
                            return board_idx, row, col
                    except ValueError:
                        pass
            
            # If AI response is invalid, make a random move
            return self.get_random_move()
            
        except Exception as e:
            print(f"AI move error: {e}")
            # Log the error and stop the game
            self.log_ai_error(f"CRITICAL ERROR: {str(e)}")
            print("AI API failure - game stopped. Please restart for AI functionality.")
            return self.get_random_move()
    
    def get_ai_prompt(self, board_text):
        """Generate AI prompt based on difficulty level"""
        
        if self.difficulty == 'Noobie':
            return f"""
You are a Noobie-level 9-Boards Tic-Tac-Toe player. You are still learning the game but understand the basics.

GAME RULES:
1. This is NOT regular tic-tac-toe - it's 9 individual 3x3 boards arranged in a 3x3 grid
2. Players can place their mark (X or O) in any empty cell of any board
3. When a player wins an individual board, that board's position in the main board gets marked with their symbol
4. **IMPORTANT**: Once a board is won or drawn, it CLOSES permanently - no more moves can be made in that board
5. The ULTIMATE GOAL is to win 3 boards in a row on the main board
6. You are playing as O, and it's your turn now

Current board state:
{board_text}

As a Noobie player:
- Focus on making simple, safe moves
- Try to win individual boards when possible
- Block obvious opponent wins
- Remember: won/drawn boards are permanently closed
- Don't overthink - make reasonable moves
- **CRITICAL**: You must respond in less than 9 seconds to avoid timeout

Analyze the board and suggest your best move. Respond with ONLY the move in format: "board_idx,row,col" (e.g., "4,1,2")
Make sure the chosen cell is empty (marked with "." in the individual boards) AND the board is not already closed.
Respond quickly - you have less than 9 seconds!
"""
        
        elif self.difficulty == 'Average':
            return f"""
You are an Average-level 9-Boards Tic-Tac-Toe player. You understand the game well and can play strategically.

GAME RULES:
1. This is 9 individual 3x3 boards arranged in a 3x3 grid (NOT regular tic-tac-toe)
2. Players can place their mark (X or O) in any empty cell of any board
3. Winning an individual board claims that position in the main board
4. **CRITICAL**: Once a board is won or drawn, it CLOSES permanently - no further moves allowed in that board
5. The ULTIMATE GOAL is to win 3 boards in a row on the main board
6. You are playing as O, and it's your turn now

Current board state:
{board_text}

As an Average player:
- Focus on making simple, safe moves
- Look for opportunities to win individual boards
- Block opponent's winning moves on individual boards and pay attention on the main 3x3 board to avoid losing
- Consider the strategic importance of board positions on the main 3x3 board
- Plan ahead for main board victories
- Remember: won/drawn boards are permanently closed - Balance offensive and defensive strategies
- **CRITICAL**: You must respond in less than 9 seconds to avoid timeout

Analyze the board and suggest your best strategic move. Respond with ONLY the move in format: "board_idx,row,col" (e.g., "4,1,2")
Make sure the chosen cell is empty (marked with "." in the individual boards) AND the board is not already closed.
Respond quickly - you have less than 9 seconds!
"""
        
        else:  # Expert
            return f"""
You are an Expert-level 9-Boards Tic-Tac-Toe player. You master the game's complexity and play at the highest level.

GAME RULES:
1. This is 9 individual 3x3 boards arranged in a 3x3 grid - a multi-layered strategic game
2. Players can place their mark (X or O) in any empty cell of any board
3. Winning an individual board claims that position in the main board
4. **FUNDAMENTAL**: Once a board is won or drawn, it CLOSES permanently - no more moves can be made in that board
5. The ULTIMATE GOAL is to win 3 boards in a row on the main board (this is what matters most)
6. You are playing as O, and it's your turn now

Current board state:
{board_text}

As an Expert player:
- Prioritize main board victory over individual board wins when strategic
- Look for opportunities to win individual boards while trying to set up multiple winning threats
- Block opponent's winning moves on individual boards and pay attention on the main 3x3 board to avoid losing
- Balance immediate threats with long-term strategy
- Think several moves ahead considering the strategic importance of board positions on the main 3x3 board
- Create situations where opponent cannot block all winning paths
- Remember: won/drawn boards are permanently closed - Balance offensive and defensive strategies

Analyze the board deeply and suggest your optimal move. Respond with ONLY the move in format: "board_idx,row,col" (e.g., "4,1,2")
Make sure the chosen cell is empty (marked with "." in the individual boards) AND the board is not already closed.
"""
    
    def get_game_state(self):
        """Return the current game state as a dictionary"""
        return {
            'boards': self.boards,
            'main_board': self.main_board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'game_mode': self.game_mode,
            'difficulty': self.difficulty,
            'ai_thinking': self.ai_thinking
        }
    
    def get_last_error(self):
        """Return the last error message"""
        return self.last_error
    
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

    def clear_log_file(self):
        """Clear the AI interaction log file"""
        try:
            with open('ai_interactions.log', 'w', encoding='utf-8') as f:
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === NEW GAME STARTED ===\n")
        except Exception as e:
            logging.error(f"Log clearing error: {e}")
    
    def log_game_move(self, board_idx, row, col):
        """Log game moves for AI analysis"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        player = self.current_player
        position = f"Board {board_idx + 1}, Row {row + 1}, Col {col + 1}"
        
        log_entry = f"[{timestamp}] MOVE: {player} played at {position}\n"
        
        try:
            with open('ai_interactions.log', 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logging.error(f"Move logging error: {e}")
    
    def log_ai_prompt(self, prompt):
        """Log AI prompts sent to Gemini"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"[{timestamp}] PROMPT: {prompt}\n"
        
        try:
            with open('ai_interactions.log', 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logging.error(f"Prompt logging error: {e}")
    
    def log_ai_response(self, response):
        """Log AI responses from Gemini"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"[{timestamp}] RESPONSE: {response}\n"
        
        try:
            with open('ai_interactions.log', 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logging.error(f"Response logging error: {e}")
    
    def log_ai_error(self, error_message):
        """Log AI errors to file"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"[{timestamp}] ERROR: {error_message}\n"
        
        try:
            with open('ai_interactions.log', 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logging.error(f"Error logging error: {e}")
    
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
    
    def switch_player(self):
        """Switch current player and reset turn timer"""
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.turn_start_time = datetime.datetime.now()
    
    def is_turn_timed_out(self):
        """Check if current turn has exceeded time limit"""
        if not self.turn_start_time:
            return False
        elapsed = datetime.datetime.now() - self.turn_start_time
        return elapsed.total_seconds() > self.time_limit
    
    def get_remaining_time(self):
        """Get remaining time for current turn in seconds"""
        if not self.turn_start_time:
            return self.time_limit
        elapsed = datetime.datetime.now() - self.turn_start_time
        remaining = self.time_limit - elapsed.total_seconds()
        return max(0, remaining)
    
    def start_turn(self):
        """Start timing the current turn"""
        self.turn_start_time = datetime.datetime.now()

# Global game instance
game = TicTacToe9Boards()

# Check for environment variable API key
env_api_key = os.environ.get('GOOGLE_API_KEY')
if env_api_key:
    game.set_api_key(env_api_key)

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
        'difficulty': game.difficulty,
        'ai_thinking': game.ai_thinking,
        'ai_enabled': AI_ENABLED,
        'remaining_time': game.get_remaining_time(),
        'time_limit': game.time_limit
    })

@app.route('/api/start_turn', methods=['POST'])
def start_turn():
    """Start timing the current turn"""
    game.start_turn()
    game_state = game.get_game_state()
    game_state['ai_enabled'] = AI_ENABLED
    return jsonify({
        'game_state': game_state
    })

@app.route('/api/make_move', methods=['POST'])
def make_move():
    """Handle player moves"""
    data = request.json
    board_idx = data.get('board_idx')
    row = data.get('row')
    col = data.get('col')
    
    print(f"DEBUG: make_move called - board_idx: {board_idx}, row: {row}, col: {col}, current_player: {game.current_player}")
    
    if game.make_move(board_idx, row, col):
        print(f"DEBUG: make_move successful")
        
        # Check if it's AI's turn next and game is not over
        if game.is_ai_turn():
            print(f"DEBUG: AI turn detected, making AI move")
            game.ai_thinking = True
            
            # Make AI move
            ai_move = game.get_ai_move()
            if ai_move:
                ai_board_idx, ai_row, ai_col = ai_move
                if game.make_move(ai_board_idx, ai_row, ai_col):
                    print(f"DEBUG: AI move successful - Board {ai_board_idx}, Row {ai_row}, Col {ai_col}")
                else:
                    print(f"DEBUG: AI move failed")
            else:
                print(f"DEBUG: No valid AI moves available")
            
            game.ai_thinking = False
        
        game_state = game.get_game_state()
        game_state['ai_enabled'] = AI_ENABLED
        return jsonify({
            'success': True,
            'game_state': game_state
        })
    else:
        print(f"DEBUG: make_move failed - {game.get_last_error()}")
        return jsonify({
            'success': False,
            'error': game.get_last_error() or 'Invalid move'
        })

@app.route('/api/set_game_mode', methods=['POST'])
def set_game_mode():
    data = request.json
    game_mode = data.get('game_mode', '1-player')
    game.set_game_mode(game_mode)
    game_state = game.get_game_state()
    game_state['ai_enabled'] = AI_ENABLED
    return jsonify({
        'game_state': game_state
    })

@app.route('/api/set_difficulty', methods=['POST'])
def set_difficulty():
    data = request.json
    difficulty = data.get('difficulty', 'Noobie')
    game.set_difficulty(difficulty)
    game_state = game.get_game_state()
    game_state['ai_enabled'] = AI_ENABLED
    return jsonify({
        'game_state': game_state
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the game with specified mode and difficulty"""
    data = request.json
    game_mode = data.get('game_mode', '1-player')
    difficulty = data.get('difficulty', 'Noobie')
    
    game.reset_game(game_mode, difficulty)
    game.start_turn()  # Start timing for first turn
    game_state = game.get_game_state()
    game_state['ai_enabled'] = AI_ENABLED
    return jsonify({
        'game_state': game_state
    })

@app.route('/api/validate_api_key', methods=['POST'])
def validate_api_key():
    """Validate a Gemini API key (key is not logged or stored permanently)"""
    data = request.json
    api_key = data.get('api_key', '')
    
    if not api_key:
        return jsonify({
            'valid': False,
            'error': 'API key is required'
        })
    
    try:
        # Configure Gemini with the provided key
        import google.genai as genai
        client = genai.Client(api_key=api_key)
        
        # Test the API with a simple request
        test_response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents="Hello, are you working?"
        )
        
        if test_response.text:
            return jsonify({
                'valid': True,
                'message': 'API key is valid'
            })
        else:
            return jsonify({
                'valid': False,
                'error': 'API key test failed'
            })
            
    except Exception as e:
        error_message = str(e)
        return jsonify({
            'valid': False,
            'error': f'API key validation failed: {error_message}'
        })

@app.route('/api/set_api_key', methods=['POST'])
def set_api_key():
    """Set the API key for the game"""
    data = request.json
    api_key = data.get('api_key', '')
    
    game.set_api_key(api_key)
    
    return jsonify({
        'success': True,
        'message': 'API key set successfully'
    })

@app.route('/api/get_env_api_key', methods=['GET'])
def get_env_api_key():
    """Return the environment API key if available"""
    env_api_key = os.environ.get('GOOGLE_API_KEY')
    if env_api_key:
        return jsonify({
            'has_env_key': True,
            'api_key': env_api_key
        })
    else:
        return jsonify({
            'has_env_key': False,
            'api_key': None
        })

@app.route('/api/get_game_log', methods=['GET'])
def get_game_log():
    """Return the contents of the AI interactions log file"""
    try:
        with open('ai_interactions.log', 'r', encoding='utf-8') as f:
            log_content = f.read()
        return jsonify({
            'success': True,
            'log_content': log_content
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'No game log file found'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error reading log file: {str(e)}'
        })

@app.route('/api/ai_message', methods=['POST'])
def get_ai_message():
    """Get AI message for post-game interaction"""
    data = request.json
    prompt = data.get('prompt', '')
    game_log = data.get('game_log', 'general')
    
    # Log the interaction
    log_ai_interaction(prompt, game_log)
    
    if not game.api_key:
        return jsonify({
            'success': False,
            'message': 'AI is not available for comments.'
        })
    
    try:
        # Use the game's API key
        import google.genai as genai
        client = genai.Client(api_key=game.api_key)
        
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt
        )
        message = response.text.strip()
        
        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        print(f"AI message endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'AI message failed'
        })

def log_ai_interaction(prompt, game_log):
    """Log AI interactions to file"""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {game_log.upper()}: {prompt}\n"
    
    try:
        with open('ai_interactions.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Logging error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
