"""SQLite storage for DatingGrowth AI MVP."""
from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("DATINGGROWTH_DB", "data/datinggrowth.sqlite3"))

def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS communities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            notes TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'reviewed',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            community_id INTEGER NOT NULL REFERENCES communities(id),
            body TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT NOT NULL,
            event_type TEXT NOT NULL DEFAULT 'start',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)

def add_community(name: str, url: str, notes: str = "") -> int:
    with connect() as conn:
        cur = conn.execute("INSERT INTO communities(name, url, notes) VALUES (?, ?, ?)",
                           (name.strip(), url.strip(), notes.strip()))
        return int(cur.lastrowid)

def list_communities() -> list[dict[str, Any]]:
    with connect() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT id, name, url, notes, status, created_at FROM communities ORDER BY id DESC"
        ).fetchall()]

def add_draft(community_id: int, body: str) -> int:
    with connect() as conn:
        cur = conn.execute("INSERT INTO drafts(community_id, body) VALUES (?, ?)",
                           (community_id, body.strip()))
        return int(cur.lastrowid)

def list_drafts(status: str | None = None) -> list[dict[str, Any]]:
    with connect() as conn:
        if status:
            rows = conn.execute(
                """SELECT d.id, d.community_id, c.name AS community_name, c.url,
                          d.body, d.status, d.created_at
                   FROM drafts d JOIN communities c ON c.id=d.community_id
                   WHERE d.status=? ORDER BY d.id DESC""", (status,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT d.id, d.community_id, c.name AS community_name, c.url,
                          d.body, d.status, d.created_at
                   FROM drafts d JOIN communities c ON c.id=d.community_id
                   ORDER BY d.id DESC LIMIT 30"""
            ).fetchall()
        return [dict(row) for row in rows]

def review_draft(draft_id: int, decision: str) -> bool:
    if decision not in {"approved", "rejected"}:
        raise ValueError("Unsupported decision")
    with connect() as conn:
        cur = conn.execute(
            """UPDATE drafts SET status=?, reviewed_at=CURRENT_TIMESTAMP
               WHERE id=? AND status='pending'""", (decision, draft_id)
        )
        return cur.rowcount == 1

def record_event(source_code: str, event_type: str = "start") -> None:
    with connect() as conn:
        conn.execute("INSERT INTO events(source_code, event_type) VALUES (?, ?)",
                     (source_code[:100], event_type[:40]))

def stats() -> dict[str, int]:
    with connect() as conn:
        return {
            "communities": conn.execute("SELECT COUNT(*) FROM communities").fetchone()[0],
            "pending": conn.execute("SELECT COUNT(*) FROM drafts WHERE status='pending'").fetchone()[0],
            "approved": conn.execute("SELECT COUNT(*) FROM drafts WHERE status='approved'").fetchone()[0],
            "rejected": conn.execute("SELECT COUNT(*) FROM drafts WHERE status='rejected'").fetchone()[0],
            "tracked_starts": conn.execute("SELECT COUNT(*) FROM events WHERE event_type='start'").fetchone()[0],
        }
