import json
import time
import sys
import subprocess
from db_utils import get_db_connection

def process_workflow(workflow_id):
    start_time = time.time()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT raw_text FROM workflows WHERE workflow_id = ?', (workflow_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"Workflow {workflow_id} not found.")
        return

    raw_text = result[0]
    
    # Generate summary (deterministic mock)
    summary = f"Processed input of {len(raw_text)} characters. Primary focus: " + raw_text[:50] + "..."
    
    # Call extract_tasks script
    process = subprocess.Popen(['python3', 'extract_tasks.py', raw_text], stdout=subprocess.PIPE)
    tasks_json, _ = process.communicate()
    tasks = json.loads(tasks_json.decode())
    
    priority_items = [t for t in tasks if 'urgent' in t.lower() or 'report' in t.lower()]
    
    processing_time_ms = (time.time() - start_time) * 1000
    
    cursor.execute('''
        UPDATE workflows 
        SET summary = ?, tasks = ?, priority_items = ?, processing_time_ms = ?, status = ?
        WHERE workflow_id = ?
    ''', (summary, json.dumps(tasks), json.dumps(priority_items), processing_time_ms, 'COMPLETED', workflow_id))
    
    conn.commit()
    conn.close()
    
    return {
        "workflow_id": workflow_id,
        "summary": summary,
        "tasks": tasks,
        "priority_items": priority_items,
        "processing_time_ms": processing_time_ms
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        res = process_workflow(sys.argv[1])
        print(json.dumps(res, indent=2))
