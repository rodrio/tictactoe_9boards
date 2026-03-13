# Tic-Tac-Toe 9-Boards Game

A web-based implementation of Tic-Tac-Toe with a 9-boards structure, built with Flask and suitable for deployment on Render using Gunicorn.

## Game Rules

- The game consists of a main 3x3 board where each cell contains an individual 3x3 tic-tac-toe board
- Players take turns marking cells in any of the 9 individual boards
- When a player wins an individual board, that board's position in the main board is marked with their symbol
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
   - Create a `.env` file in the project root:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```
   - Without the API key, the AI will use random moves as fallback

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
- **Making Moves**: Click any empty cell in any board to place your mark
- **New Game**: Click the "🔄 New Game" button to restart
- **Rules**: Click "📖 Rules" to see detailed game instructions

### AI Features

The AI opponent includes:
- **Strategic Analysis**: Evaluates board positions and potential moves
- **Offensive Play**: Attempts to win individual boards and the main game
- **Defensive Play**: Blocks opponent's winning moves
- **Board Priority**: Focuses on strategically important board positions
- **Fallback Logic**: If API is unavailable, uses random valid moves

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

## Game Controls

- Click any empty cell in any board to make a move
- The current player is indicated at the top
- Click "New Game" to reset and start over

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Deployment**: Gunicorn WSGI server
- **Hosting**: Render (compatible)

Enjoy playing! 🎮
