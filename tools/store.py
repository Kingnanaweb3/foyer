"""Tiny JSON read/write helpers. No database needed for a hackathon MVP."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load(filename: str):
    with open(DATA_DIR / filename) as f:
        return json.load(f)

def save(filename: str, data):
    with open(DATA_DIR / filename, "w") as f:
        json.dump(data, f, indent=2)
