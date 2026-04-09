"""
Usage statistics for Koda.

Tracks words dictated, time saved, commands used, per-app breakdown.
Stores in the existing SQLite database alongside transcript history.
"""

import os
import sqlite3
from datetime import datetime, timedelta

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "koda_history.db")


def _get_conn():
    return sqlite3.connect(DB_PATH)


def init_stats_db():
    """Create stats table if it doesn't exist."""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_stats (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            event_type TEXT,
            word_count INTEGER DEFAULT 0,
            char_count INTEGER DEFAULT 0,
            duration_seconds REAL DEFAULT 0,
            mode TEXT,
            app_name TEXT,
            profile_name TEXT,
            command_name TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_transcription_stats(text, mode, duration, app_name="", profile_name=""):
    """Log stats for a completed transcription."""
    words = len(text.split()) if text else 0
    chars = len(text) if text else 0
    conn = _get_conn()
    conn.execute(
        "INSERT INTO usage_stats (timestamp, event_type, word_count, char_count, "
        "duration_seconds, mode, app_name, profile_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), "transcription", words, chars, duration, mode, app_name, profile_name),
    )
    conn.commit()
    conn.close()


def log_command_stats(command_name, app_name=""):
    """Log stats for a voice command execution."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO usage_stats (timestamp, event_type, command_name, app_name) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), "command", command_name, app_name),
    )
    conn.commit()
    conn.close()


# --- Queries ---

def get_summary(days=None):
    """Get overall usage summary.

    Returns dict with:
        total_transcriptions, total_words, total_chars, total_duration,
        total_commands, estimated_time_saved, top_apps, top_commands,
        words_per_day, busiest_hour
    """
    conn = _get_conn()

    where = ""
    params = ()
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        where = "WHERE timestamp > ?"
        params = (cutoff,)

    # Transcription stats
    row = conn.execute(
        f"SELECT COUNT(*), COALESCE(SUM(word_count),0), COALESCE(SUM(char_count),0), "
        f"COALESCE(SUM(duration_seconds),0) FROM usage_stats "
        f"{where} {'AND' if where else 'WHERE'} event_type='transcription'",
        params,
    ).fetchone()
    total_trans, total_words, total_chars, total_duration = row

    # Command stats
    total_cmds = conn.execute(
        f"SELECT COUNT(*) FROM usage_stats {where} {'AND' if where else 'WHERE'} event_type='command'",
        params,
    ).fetchone()[0]

    # Estimated time saved: assume typing speed of 40 WPM
    # Voice is ~150 WPM, so time saved ≈ words/40 - words/150
    typing_time = total_words / 40 * 60 if total_words else 0  # seconds at 40 WPM
    speaking_time = total_duration
    time_saved = max(0, typing_time - speaking_time)

    # Top apps
    top_apps = conn.execute(
        f"SELECT app_name, COUNT(*), SUM(word_count) FROM usage_stats "
        f"{where} {'AND' if where else 'WHERE'} event_type='transcription' AND app_name != '' "
        f"GROUP BY app_name ORDER BY COUNT(*) DESC LIMIT 5",
        params,
    ).fetchall()

    # Top commands
    top_commands = conn.execute(
        f"SELECT command_name, COUNT(*) FROM usage_stats "
        f"{where} {'AND' if where else 'WHERE'} event_type='command' AND command_name != '' "
        f"GROUP BY command_name ORDER BY COUNT(*) DESC LIMIT 5",
        params,
    ).fetchall()

    # Words per day (last 7 days)
    words_by_day = conn.execute(
        "SELECT DATE(timestamp), SUM(word_count) FROM usage_stats "
        "WHERE event_type='transcription' AND timestamp > ? "
        "GROUP BY DATE(timestamp) ORDER BY DATE(timestamp)",
        ((datetime.now() - timedelta(days=7)).isoformat(),),
    ).fetchall()

    # Busiest hour
    busiest = conn.execute(
        f"SELECT CAST(SUBSTR(timestamp, 12, 2) AS INTEGER) as hour, COUNT(*) "
        f"FROM usage_stats {where} {'AND' if where else 'WHERE'} event_type='transcription' "
        f"GROUP BY hour ORDER BY COUNT(*) DESC LIMIT 1",
        params,
    ).fetchone()

    conn.close()

    return {
        "total_transcriptions": total_trans,
        "total_words": total_words,
        "total_chars": total_chars,
        "total_duration": total_duration,
        "total_commands": total_cmds,
        "time_saved_seconds": time_saved,
        "top_apps": top_apps,
        "top_commands": top_commands,
        "words_by_day": words_by_day,
        "busiest_hour": busiest[0] if busiest else None,
    }


def get_today_summary():
    """Quick summary for today only."""
    conn = _get_conn()
    today = datetime.now().strftime("%Y-%m-%d")

    row = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(word_count),0), COALESCE(SUM(duration_seconds),0) "
        "FROM usage_stats WHERE event_type='transcription' AND timestamp LIKE ?",
        (f"{today}%",),
    ).fetchone()
    conn.close()

    return {
        "transcriptions": row[0],
        "words": row[1],
        "duration": row[2],
    }
