import time
import sqlite3
import random
import string
from process_text import process_workflow

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_benchmark(num_iterations=50):
    conn = sqlite3.connect('workflow_engine.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            workflow_id TEXT PRIMARY KEY,
            raw_text TEXT,
            summary TEXT,
            tasks TEXT,
            priority_items TEXT,
            processing_time_ms REAL,
            status TEXT
        )
    ''')

    workflow_ids = []
    for i in range(num_iterations):
        wid = f"bench_{i}"
        text = "assign some task. review this document. " + generate_random_string(1000)
        cursor.execute('INSERT OR REPLACE INTO workflows (workflow_id, raw_text, status) VALUES (?, ?, ?)', (wid, text, 'PENDING'))
        workflow_ids.append(wid)

    conn.commit()
    conn.close()

    start_time = time.time()
    for wid in workflow_ids:
        process_workflow(wid)
    end_time = time.time()

    total_time = end_time - start_time
    print(f"Total time for {num_iterations} iterations: {total_time:.4f} seconds")
    print(f"Average time per iteration: {total_time / num_iterations:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
