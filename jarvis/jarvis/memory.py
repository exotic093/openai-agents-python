"""Persistent long-term memory for Jarvis, backed by SQLite."""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .config import MEMORY_DB


@dataclass
class MemoryRecord:
    id: int
    key: str
    value: str
    created_at: float


class MemoryStore:
    def __init__(self, path: Path = MEMORY_DB) -> None:
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key)")
        self._conn.commit()

    def remember(self, key: str, value: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO memory(key, value, created_at) VALUES (?, ?, ?)",
            (key, value, time.time()),
        )
        self._conn.commit()
        return int(cur.lastrowid or 0)

    def recall(self, query: str, limit: int = 10) -> list[MemoryRecord]:
        like = f"%{query}%"
        rows = self._conn.execute(
            """
            SELECT id, key, value, created_at FROM memory
            WHERE key LIKE ? OR value LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (like, like, limit),
        ).fetchall()
        return [MemoryRecord(*r) for r in rows]

    def all(self, limit: int = 50) -> list[MemoryRecord]:
        rows = self._conn.execute(
            "SELECT id, key, value, created_at FROM memory ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [MemoryRecord(*r) for r in rows]

    def forget(self, mem_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM memory WHERE id = ?", (mem_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def context_summary(self, limit: int = 20) -> str:
        items = self.all(limit=limit)
        if not items:
            return "(no prior memories)"
        return "\n".join(f"- [{m.key}] {m.value}" for m in items)


_store: MemoryStore | None = None


def get_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store
