# Knights of Eldoria Simulation

A grid-based simulation featuring knights, treasure hunters, and various game mechanics.

## Features

- Dynamic grid system with wraparound functionality
- Multiple entity types (Knights, Hunters, Treasures, Hideouts, Garrisons)
- Complex treasure hunting and patrol mechanics
- Team-based hunter behavior with skill specialization
- Energy and stamina management systems
- Comprehensive performance tracking

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- Unix/MacOS: `source .venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Simulation

```bash
python main.py
```

## Testing

```bash
pytest tests/
``` 