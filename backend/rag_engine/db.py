# This module handles storing and retrieving conversation history with users
# It also logs any escalations that occur during the interaction
import sqlite3
from datetime import datetime

DB_PATH = "conversation_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_id TEXT,
            question TEXT,
            context TEXT,
            answer TEXT,
            escalated INTEGER DEFAULT 0  -- 0 = not escalated, 1 = escalated
        )
    ''')
    conn.commit()
    conn.close()


def save_conversation(user_id, question, context, answer, escalated=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO conversation (timestamp, user_id, question, context, answer, escalated)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.utcnow().isoformat(), user_id, question, context, answer, int(escalated)))
    conn.commit()
    conn.close()



def get_history_by_user(user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT question, answer FROM conversation
        WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
    ''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def get_total_escalations():
    conn = sqlite3.connect("conversation_memory.db")
    c = conn.cursor()
    c.execute('SELECT COUNT(DISTINCT user_id) FROM conversation WHERE escalated = 1')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_total_escalation_cases():
    conn = sqlite3.connect("conversation_memory.db")
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM conversation WHERE escalated = 1')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_total_users():
    conn = sqlite3.connect("conversation_memory.db")
    c = conn.cursor()
    c.execute('SELECT COUNT(DISTINCT user_id) FROM conversation')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_total_questions():
    conn = sqlite3.connect("conversation_memory.db")
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM conversation')
    total = c.fetchone()[0]
    conn.close()
    return total
