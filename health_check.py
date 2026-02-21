import sqlite3
import os

def check():
    db_exists = os.path.exists('workflow_engine.db')
    print(f"Database status: {'OK' if db_exists else 'MISSING'}")
    
    if db_exists:
        conn = sqlite3.connect('workflow_engine.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM workflows')
        count = cursor.fetchone()[0]
        print(f"Total workflows: {count}")
        conn.close()
    
    scripts = ['ingest_workflow.py', 'process_text.py', 'extract_tasks.py']
    for s in scripts:
        print(f"Script {s}: {'OK' if os.path.exists(s) else 'MISSING'}")

if __name__ == "__main__":
    check()
