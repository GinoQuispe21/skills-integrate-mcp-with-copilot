import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "app.sqlite"


def _connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed initial activities if necessary."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS activities (
            name TEXT PRIMARY KEY,
            description TEXT,
            schedule TEXT,
            max_participants INTEGER,
            participants TEXT
        )
        """
    )
    conn.commit()

    # If table empty, seed with example activities
    cur.execute("SELECT COUNT(1) as c FROM activities")
    row = cur.fetchone()
    if row and row["c"] == 0:
        _seed_default_activities(conn)

    conn.close()


def _seed_default_activities(conn):
    seed = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        },
        "Basketball Team": {
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        },
        "Art Club": {
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        },
        "Drama Club": {
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        },
        "Math Club": {
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        },
    }

    cur = conn.cursor()
    for name, info in seed.items():
        cur.execute(
            "INSERT INTO activities (name, description, schedule, max_participants, participants) VALUES (?, ?, ?, ?, ?)",
            (
                name,
                info["description"],
                info["schedule"],
                info["max_participants"],
                json.dumps(info["participants"]),
            ),
        )
    conn.commit()


def get_activities() -> Dict[str, Any]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities")
    rows = cur.fetchall()
    result: Dict[str, Any] = {}
    for r in rows:
        result[r["name"]] = {
            "description": r["description"],
            "schedule": r["schedule"],
            "max_participants": r["max_participants"],
            "participants": json.loads(r["participants"] or "[]"),
        }
    conn.close()
    return result


def get_activity(name: str) -> Optional[Dict[str, Any]]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities WHERE name = ?", (name,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "description": r["description"],
        "schedule": r["schedule"],
        "max_participants": r["max_participants"],
        "participants": json.loads(r["participants"] or "[]"),
    }


def signup_for_activity(name: str, email: str) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT participants, max_participants FROM activities WHERE name = ?", (name,))
    r = cur.fetchone()
    if not r:
        conn.close()
        raise ValueError("not_found")

    participants = json.loads(r["participants"] or "[]")
    maxp = r["max_participants"]
    if email in participants:
        conn.close()
        raise ValueError("already_signed_up")
    if len(participants) >= maxp:
        conn.close()
        raise ValueError("full")

    participants.append(email)
    cur.execute("UPDATE activities SET participants = ? WHERE name = ?", (json.dumps(participants), name))
    conn.commit()
    conn.close()


def unregister_from_activity(name: str, email: str) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT participants FROM activities WHERE name = ?", (name,))
    r = cur.fetchone()
    if not r:
        conn.close()
        raise ValueError("not_found")
    participants = json.loads(r["participants"] or "[]")
    if email not in participants:
        conn.close()
        raise ValueError("not_signed_up")
    participants.remove(email)
    cur.execute("UPDATE activities SET participants = ? WHERE name = ?", (json.dumps(participants), name))
    conn.commit()
    conn.close()
