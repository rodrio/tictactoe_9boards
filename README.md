# Tic-Tac-Toe 9-Boards Game

A web-based implementation of Tic-Tac-Toe with a 9-boards structure, built with Flask and suitable for deployment on Render using Gunicorn.

## Game Rules

- The game consists of a main 3x3 board where each cell contains an individual 3x3 tic-tac-toe board
- Players take turns marking cells in any of the 9 individual boards
- When a player wins an individual board, that board's position in the main board is marked with their symbol
- **Board Closing**: Once a board is won or drawn, it closes permanently - no more moves can be made in that board
- The goal is to win three in a row on the main board (horizontally, vertically, or diagonally)
- If an individual board ends in a draw, it's marked with 'D' on the main board

## Features

- Fully responsive web interface
- Real-time game updates
- Visual feedback for board states
- Game state management
- Reset functionality
- **AI Player**: Play against an intelligent AI opponent powered by Google Gemini 1.5 Flash Lite
- **Game Modes**: Choose between 1-player (vs AI) or 2-players (local multiplayer)
- Deploy-ready for Render web services

## Local Development

### Prerequisites
- Python 3.7+
- pip

### Setup

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd tictactoe_9boards
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. **(Optional) Set up AI Player**: 
   - Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - In 1-player mode, enter your API key in the provided field (optional)
   - Click "🔑 Validate Key" to test your API key
   - **Security**: API keys are stored in memory only and never saved to files
   - **No Key**: If left blank, AI will use random moves as fallback
   - **Invalid Key**: System will show error and fallback to random moves

6. Run the application:
   ```bash
   python app.py
   ```

7. Open your browser and navigate to `http://localhost:5000`

## Deployment on Render

### Prerequisites
- Render account
- Git repository with the project code

### Deployment Steps

1. Push your code to a Git repository
2. Create a new Web Service on Render
3. Connect your Git repository
4. Configure the build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --config gunicorn_config.py app:app`
5. Deploy!

The application includes:
- `Procfile` for Render deployment configuration
- `gunicorn_config.py` for Gunicorn settings
- `requirements.txt` for Python dependencies

## How to Play

### Game Modes

**1-Player Mode (vs AI)**
- Default mode - play against an AI opponent
- You play as X, AI plays as O
- AI analyzes the board and makes strategic moves
- AI uses Google Gemini 1.5 Flash Lite for intelligent gameplay

**2-Players Mode**
- Local multiplayer on the same device
- Players take turns as X and O
- Perfect for playing with a friend

### Controls
- **Game Mode Selection**: Click the mode buttons at the top to switch between 1-player and 2-players
- **Difficulty Selection**: In 1-player mode, choose between Noobie, Average, or Expert AI difficulty
- **Making Moves**: Click any empty cell in any board to place your mark
- **New Game**: Click the "🔄 New Game" button to restart
- **Rules**: Click "📖 Rules" to see detailed game instructions

### Victory Celebrations
- **Dynamic Modal**: Automatic victory celebration appears when game ends
- **Context-Aware Messages**: Different content based on game mode and winner
- **AI Interaction**: In 1-player mode, AI generates arrogant/hilarious post-game messages
- **Entertaining**: AI provides unique victory and defeat reactions
- **Visual Feedback**: Beautiful modal design with animations

### API Key Management

**🔑 Secure API Key System**
- **In-Memory Storage**: API keys stored only during game session
- **No File Persistence**: Keys never saved to disk or logs
- **Real-Time Validation**: Test API key before using for AI moves
- **Error Handling**: Clear messages for invalid keys, quota issues, rate limits
- **Flexible Usage**: Can enter key anytime, change during gameplay
- **Automatic Fallback**: Random moves when no valid key provided

**How to Use**
1. Select 1-player mode
2. Enter your Gemini API key in the provided field (optional)
3. Click "🔑 Validate Key" to test the key
4. Green status = valid key, Red status = invalid key
5. Leave blank for random moves only

**Security Features**
- Password field masks input
- Keys stored in server memory only
- No logging of API keys
- Keys lost when game restarts
- Session-based storage

### AI Logging System
- **Complete Tracking**: Every AI prompt and response logged with timestamps
- **Game Moves**: All player moves recorded during AI games
- **Error Handling**: Graceful API failures with fallback mechanisms
- **File Management**: Automatic log clearing for new games
- **Debugging Support**: Comprehensive audit trail in `ai_interactions.log`
- **Game Certification**: Stops play on critical AI failures

### AI Features

The AI opponent includes:
- **Strategic Analysis**: Evaluates board positions and potential moves
- **Offensive Play**: Attempts to win individual boards and main game
- **Defensive Play**: Blocks opponent's winning moves
- **Board Priority**: Focuses on strategically important board positions
- **API Key Management**: Secure in-memory API key storage with validation
- **Fallback Logic**: If API key is invalid or missing, uses random valid moves
- **Complete Logging**: All AI prompts and responses are logged to `ai_interactions.log`
- **Error Handling**: Graceful fallbacks and proper error reporting
- **Game Certification**: Stops game on critical AI failures
- **Security-First**: API keys never saved to files, stored in memory only

### Difficulty Levels

**🌱 Noobie**
- Simple, safe moves
- Basic understanding of rules
- Focuses on obvious wins and blocks
- Good for beginners

**🎯 Average**
- Balanced offensive/defensive strategy
- Considers board position importance
- Plans ahead for main board victories
- Challenging but fair gameplay

**🔥 Expert**
- Advanced tactical play
- Sets up multiple winning threats
- Controls key board positions
- Thinks several moves ahead
- Creates forced move situations

```
tictactoe_9boards/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # HTML template with embedded CSS and JavaScript
├── requirements.txt       # Python dependencies
├── gunicorn_config.py    # Gunicorn configuration
├── Procfile             # Render deployment configuration
└── README.md            # This file
```

## API Endpoints

- `GET /` - Main game page
- `GET /api/game_state` - Get current game state
- `POST /api/make_move` - Make a move (expects JSON with board_idx, row, col)
- `POST /api/reset` - Reset the game
- `POST /api/set_game_mode` - Set game mode (1-player or 2-players)
- `POST /api/set_difficulty` - Set AI difficulty (Noobie, Average, Expert)
- `POST /api/validate_api_key` - Validate Gemini API key
- `POST /api/set_api_key` - Set API key for AI (stored in memory only)
- `POST /api/clear_api_key` - Clear API key from memory
- `POST /api/ai_message` - Get AI post-game message

## Game Controls

- **Game Mode Selection**: Click mode buttons to switch between 1-player and 2-players
- **API Key Management**: In 1-player mode, enter and validate Gemini API key (optional)
- **Difficulty Selection**: Choose AI difficulty level (Noobie, Average, Expert)
- **Making Moves**: Click any empty cell in any board to place your mark
- **New Game**: Click "🔄 New Game" button to reset and start over
- **Rules**: Click "📖 Rules" to see detailed game instructions

### API Key Controls
- **Enter Key**: Type your Gemini API key in the password field
- **Validate Key**: Click "🔑 Validate Key" to test API key validity
- **Status Indicators**: Green = valid, Red = invalid, Blue = info
- **Clear Key**: Leave field blank or clear to use random moves only

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Deployment**: Gunicorn WSGI server
- **Hosting**: Render (compatible)

Enjoy playing! 🎮
