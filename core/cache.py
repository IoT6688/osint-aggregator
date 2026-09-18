"""
Lớp cache SQLite tùy chọn. Nếu config.CACHE_ENABLED = False,
dispatcher sẽ không dùng lớp này -- hệ thống vẫn chạy bình thường,
chỉ là gọi API mỗi lần tra cứu thay vì lấy từ cache.
"""

import json
import sqlite3
from datetime import datetime, timezone

from core.base_connector import ConnectorResult
import config


class SQLiteCache:
    def __init__(self, db_path: str = config.CACHE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS connector_cache (
                    connector_name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    PRIMARY KEY (connector_name, target)
                )
                """
            )

    def get(self, connector_name: str, target: str) -> ConnectorResult | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT response_json, fetched_at FROM connector_cache "
                "WHERE connector_name = ? AND target = ?",
                (connector_name, target),
            ).fetchone()

        if row is None:
            return None

        response_json, fetched_at = row
        fetched_dt = datetime.fromisoformat(fetched_at)
        age_seconds = (datetime.now(timezone.utc) - fetched_dt).total_seconds()

        if age_seconds > config.CACHE_TTL_SECONDS:
            return None  # cache đã cũ, coi như không có

        data = json.loads(response_json)
        data["from_cache"] = True
        return ConnectorResult(**data)

    def set(self, connector_name: str, target: str, result: ConnectorResult):
        payload = result.to_dict()
        payload.pop("from_cache", None)  # không lưu cờ from_cache vào cache
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO connector_cache (connector_name, target, response_json, fetched_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(connector_name, target) DO UPDATE SET
                    response_json = excluded.response_json,
                    fetched_at = excluded.fetched_at
                """,
                (connector_name, target, json.dumps(payload), result.fetched_at),
            )
