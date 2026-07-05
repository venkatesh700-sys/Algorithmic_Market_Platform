import sqlite3
from datetime import datetime

DB_NAME = "quant_trading_desk.db"

def initialize_database():
    """Builds explicit database tables schema for the autonomous ledger network."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Paper Ledger Tracking Tables Schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            wallet_balance REAL,
            active_allocations INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_ledger (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            ticker TEXT,
            strategy_type TEXT,
            direction TEXT,
            entry_price REAL,
            stop_loss REAL,
            target_1 REAL,
            target_2 REAL,
            quantity INTEGER,
            status TEXT,
            exit_price REAL,
            pnl REAL,
            confidence_score REAL
        )
    ''')
    
    # Initialize baseline capital allocations if portfolio is unpopulated
    cursor.execute("SELECT COUNT(*) FROM portfolio")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO portfolio (timestamp, wallet_balance, active_allocations) VALUES (?, ?, ?)",
                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 40000.0, 0))
    
    conn.commit()
    conn.close()
    print("📦 SQLite Database schemas locked and loaded successfully.")

if __name__ == "__main__":
    initialize_database()
