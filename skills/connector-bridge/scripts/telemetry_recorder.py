#!/usr/bin/env python3
"""
Telemetry Recorder
Records latency, token consumption, status telemetry into local connection cache.
"""

import json
import sqlite3
import time
import threading
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from contextlib import contextmanager


class TelemetryEventType(Enum):
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    REQUEST_ERROR = "request_error"
    RATE_LIMIT_HIT = "rate_limit_hit"
    CIRCUIT_OPEN = "circuit_open"
    CIRCUIT_CLOSE = "circuit_close"
    TOKEN_USAGE = "token_usage"


@dataclass
class TelemetryEvent:
    event_type: TelemetryEventType
    timestamp: float
    endpoint: str
    operation: str
    latency_ms: Optional[float] = None
    status_code: Optional[int] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class TelemetryRecorder:
    """Thread-safe telemetry recorder with SQLite backend."""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path.home() / ".connector_bridge_telemetry.db"
        self.lock = threading.RLock()
        self._init_db()
        self._buffer: List[TelemetryEvent] = []
        self._buffer_size = 100
        self._flush_interval = 5.0
        self._last_flush = time.time()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    endpoint TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    latency_ms REAL,
                    status_code INTEGER,
                    tokens_used INTEGER,
                    error TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_telemetry_endpoint_time 
                ON telemetry(endpoint, timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_telemetry_type_time 
                ON telemetry(event_type, timestamp)
            """)
    
    def record(self, event: TelemetryEvent):
        """Record telemetry event (buffered)."""
        with self.lock:
            self._buffer.append(event)
            
            # Auto-flush if buffer full or interval elapsed
            if len(self._buffer) >= self._buffer_size or \
               time.time() - self._last_flush > self._flush_interval:
                self._flush_unlocked()
    
    def _flush_unlocked(self):
        """Flush buffer to database (must hold lock)."""
        if not self._buffer:
            return
        
        events = self._buffer
        self._buffer = []
        self._last_flush = time.time()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                for event in events:
                    conn.execute(
                        """INSERT INTO telemetry 
                           (event_type, timestamp, endpoint, operation, latency_ms, status_code, tokens_used, error, metadata)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            event.event_type.value,
                            event.timestamp,
                            event.endpoint,
                            event.operation,
                            event.latency_ms,
                            event.status_code,
                            event.tokens_used,
                            event.error,
                            json.dumps(event.metadata)
                        )
                    )
        except Exception:
            # Re-add to buffer on failure
            self._buffer = events + self._buffer
    
    def flush(self):
        """Force flush buffer."""
        with self.lock:
            self._flush_unlocked()
    
    def query(self, endpoint: str = None, event_type: TelemetryEventType = None,
              since: float = None, until: float = None, limit: int = 1000) -> List[Dict]:
        """Query telemetry events."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM telemetry WHERE 1=1"
            params = []
            
            if endpoint:
                query += " AND endpoint = ?"
                params.append(endpoint)
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)
            if since:
                query += " AND timestamp >= ?"
                params.append(since)
            if until:
                query += " AND timestamp <= ?"
                params.append(until)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_summary(self, endpoint: str = None, hours: int = 24) -> Dict:
        """Get telemetry summary for period."""
        since = time.time() - (hours * 3600)
        events = self.query(endpoint=endpoint, since=since)
        
        if not events:
            return {"period_hours": hours, "total_events": 0}
        
        summary = {
            "period_hours": hours,
            "total_events": len(events),
            "by_type": {},
            "by_endpoint": {},
            "avg_latency_ms": 0,
            "error_rate": 0,
            "total_tokens": 0
        }
        
        latencies = []
        errors = 0
        tokens = 0
        
        for e in events:
            # By type
            t = e["event_type"]
            summary["by_type"][t] = summary["by_type"].get(t, 0) + 1
            
            # By endpoint
            ep = e["endpoint"]
            summary["by_endpoint"][ep] = summary["by_endpoint"].get(ep, 0) + 1
            
            # Latency
            if e["latency_ms"] is not None:
                latencies.append(e["latency_ms"])
            
            # Errors
            if e["event_type"] == "request_error":
                errors += 1
            
            # Tokens
            if e["tokens_used"]:
                tokens += e["tokens_used"]
        
        if latencies:
            summary["avg_latency_ms"] = round(sum(latencies) / len(latencies), 2)
        if events:
            summary["error_rate"] = round(errors / len(events), 4)
        summary["total_tokens"] = tokens
        
        return summary
    
    @contextmanager
    def track(self, endpoint: str, operation: str, metadata: Dict = None):
        """Context manager to track request latency."""
        start = time.time()
        error = None
        try:
            yield
        except Exception as e:
            error = str(e)
            raise
        finally:
            latency = (time.time() - start) * 1000
            self.record(TelemetryEvent(
                event_type=TelemetryEventType.REQUEST_ERROR if error else TelemetryEventType.REQUEST_END,
                timestamp=time.time(),
                endpoint=endpoint,
                operation=operation,
                latency_ms=latency,
                error=error,
                metadata=metadata or {}
            ))


# Global recorder instance
RECORDER = TelemetryRecorder()


def main():
    if len(sys.argv) < 2:
        print("Usage: telemetry_recorder.py <command> [args...]")
        print("Commands:")
        print("  summary [endpoint] [hours]  - Show telemetry summary")
        print("  query [endpoint] [type]     - Query raw events")
        print("  flush                       - Flush buffer to disk")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "summary":
        endpoint = sys.argv[2] if len(sys.argv) > 2 else None
        hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        print(json.dumps(RECORDER.get_summary(endpoint, hours), indent=2))
    
    elif command == "query":
        endpoint = sys.argv[2] if len(sys.argv) > 2 else None
        event_type = TelemetryEventType(sys.argv[3]) if len(sys.argv) > 3 else None
        hours = int(sys.argv[4]) if len(sys.argv) > 4 else 24
        since = time.time() - (hours * 3600)
        events = RECORDER.query(endpoint=endpoint, event_type=event_type, since=since)
        print(json.dumps(events, indent=2))
    
    elif command == "flush":
        RECORDER.flush()
        print("Flushed")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
