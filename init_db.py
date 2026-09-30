import sqlite3

def init_db():
    conn = sqlite3.connect('workflow_engine.db')
    cursor = conn.cursor()
    
    # Workflows table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            workflow_id TEXT PRIMARY KEY,
            raw_text TEXT,
            summary TEXT,
            tasks TEXT,
            priority_items TEXT,
            processing_time_ms REAL,
            status TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
