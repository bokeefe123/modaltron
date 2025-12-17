# Modaltron Python Server

A Python port of the Curvytron game server, designed to run on [Modal](https://modal.com).

## Overview

This is a complete port of the Node.js Curvytron game server to Python, using:

- **FastAPI** for the HTTP/WebSocket server
- **asyncio** for the game loop and event handling
- **Modal** for serverless deployment

## Project Structure

```
python_server/
├── modal_app.py          # Modal entry point
├── requirements.txt      # Python dependencies
├── server/
│   ├── __init__.py
│   ├── server.py         # Main FastAPI server
│   ├── socket_client.py  # WebSocket client wrapper
│   ├── collection.py     # Collection data structure
│   ├── event_emitter.py  # Event emitter pattern
│   ├── core/             # Core components
│   │   ├── body.py       # Collision body
│   │   ├── avatar_body.py
│   │   ├── island.py     # Spatial partitioning
│   │   ├── world.py      # Physics/collision detection
│   │   └── socket_group.py
│   ├── models/           # Game models
│   │   ├── base_*.py     # Base classes
│   │   ├── avatar.py
│   │   ├── game.py
│   │   ├── room.py
│   │   ├── player.py
│   │   └── bonus/        # Bonus types
│   ├── controllers/      # Game controllers
│   │   ├── game_controller.py
│   │   ├── room_controller.py
│   │   └── rooms_controller.py
│   ├── managers/         # Game managers
│   │   ├── bonus_manager.py
│   │   └── print_manager.py
│   ├── services/         # Utility services
│   └── repositories/     # Data repositories
```

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
cd python_server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
# From the python_server directory
python modal_app.py
```

The server will start at `http://localhost:8080`. Open your browser and navigate to this URL to play the game.

## Deploy to Modal

### Prerequisites

- [Modal account](https://modal.com)
- Modal CLI installed and configured

### Setup Modal

```bash
pip install modal
modal setup  # Follow authentication prompts
```

### Deploy

```bash
cd python_server
modal deploy modal_app.py
```

Modal will provide you with a URL like `https://your-username--modaltron-serve.modal.run`.

## Architecture

### WebSocket Protocol

The server uses the same JSON-based WebSocket protocol as the original Node.js server, ensuring compatibility with the existing client.

Messages are batched and sent as JSON arrays:
```json
[["event_name", data], ["event_name2", data2]]
```

### Game Loop

The game runs at ~60 FPS using Python's `asyncio`:
- Avatar position/angle updates
- Collision detection (spatial partitioning with islands)
- Bonus spawning and collection
- Trail printing logic

### Key Differences from Node.js

1. **Event System**: Uses a custom `EventEmitter` class instead of Node.js events
2. **Async/Await**: Uses Python's native asyncio instead of callbacks
3. **Timers**: Uses `asyncio.TimerHandle` instead of `setTimeout`/`setInterval`

## Configuration

Environment variables:
- `WEB_DIR`: Path to web static files (default: `/root/web` on Modal, auto-detected locally)

## Client Compatibility

The Python server is fully compatible with the existing web client - no client modifications needed. The WebSocket protocol and all game events are preserved exactly as in the original Node.js implementation.

