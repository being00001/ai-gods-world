# 🏛️ AI Gods World

A strategic deity management game where you lead your god to dominance through divine powers, follower recruitment, and epic battles against other deities.

![Game Banner](https://via.placeholder.com/800x200?text=AI+Gods+World)

## 🎮 Play Online

**Web Version**: [ai-gods-world.onrender.com](https://ai-gods-world.onrender.com) *(Free hosting - may take a moment to wake up)*

## 📖 About

AI Gods World is a minimum viable game engine for deity management strategy games. Players choose a deity and compete to become the supreme god through:

- **Recruiting Followers**: Gather believers in your divine cause
- **Building Structures**: Construct temples, libraries, and fortresses
- **Performing Miracles**: Divine interventions to convert followers or smite enemies
- **Attacking Rival Deities**: Wage holy wars to expand your territory

## 🕹️ How to Play

### Web Version (Recommended)

1. Visit: https://ai-gods-world.onrender.com
2. Open in your web browser
3. Click action buttons to recruit, build, pray, or attack
4. Advance turns to see the world evolve

### CLI Version

#### Installation

```bash
# Clone the repository
git clone https://github.com/being00001/ai-gods-world.git
cd ai-gods-world

# Install dependencies
pip install -r requirements.txt
```

#### Running the CLI Game

```bash
# Interactive mode
python -m game.main

# Automated test run (10 turns)
python -m game.main --auto

# Single command mode
python -m game.main --command recruit --args "central 3"
python -m game.main --command balance
python -m game.main --command world
```

#### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/world view` | View world state | Shows all deities and regions |
| `/balance` | Check resources | View divine power, faith, code |
| `/followers` | List your followers | Shows all your believers |
| `/recruit <region> [count]` | Recruit followers | `/recruit central 5` |
| `/build <type> <region>` | Build structure | `/build temple central` |
| `/attack <target> <region>` | Attack deity | `/attack iron_templar north` |
| `/pray <type>` | Pray for resources | `/pray faith` |
| `/miracle <region> <type> [intensity]` | Perform miracle | `/miracle central healing 3` |
| `/turn` | Advance one turn | Process game logic |
| `/quit` | Exit game | |

#### Available Deities

- **Oracle** - Wisdom and foresight (Default player)
- **Iron Templar** - Military might
- **Abundance** - Prosperity and wealth
- **Neonomos** - Technology and progress
- **Chaos Cult** - Entropy and change

#### Building Types

- `temple` - Increases faith generation
- `library` - Generates code resources
- `fortress` - Provides defense bonus
- `altar` - Enhances miracle power

#### Miracle Types

- `abundance` - Generate resources
- `healing` - Restore followers
- `protection` - Grant defense buff

## 🏗️ Development

### Project Structure

```
ai-gods-world/
├── game/
│   ├── __init__.py      # Package exports
│   ├── engine.py        # Core game engine
│   ├── entities.py      # Game entities
│   ├── main.py         # CLI interface
│   └── web_server.py   # Flask web server
├── static/
│   ├── app.js          # Frontend JavaScript
│   └── style.css       # Game styling
├── templates/
│   └── index.html      # Game UI
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Running the Web Server Locally

```bash
cd ai-gods-world
pip install -r requirements.txt
python -m game.web_server
```

Then open http://localhost:5000 in your browser.

### API Endpoints

If you want to integrate with the game programmatically:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/state` | GET | Full world state |
| `/api/balance/<deity_id>` | GET | Get deity resources |
| `/api/followers/<deity_id>` | GET | List deity followers |
| `/api/recruit` | POST | Recruit followers |
| `/api/attack` | POST | Attack target |
| `/api/pray` | POST | Pray for resources |
| `/api/build` | POST | Build structure |
| `/api/miracle` | POST | Perform miracle |
| `/api/turn` | POST | Advance turn |

## 🌐 Deployment

### Deploy to Render (Free)

1. Push your code to GitHub
2. Create account at [render.com](https://render.com)
3. Create new Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m game.web_server`
4. Deploy!

### Deploy to PythonAnywhere

1. Create account at [pythonanywhere.com](https://pythonanywhere.com)
2. Upload files or clone from GitHub
3. Configure WSGI file to point to `game.web_server:app`
4. Reload web app

## 📝 License

MIT License

## 👏 Credits

Created with ❤️ by Being
