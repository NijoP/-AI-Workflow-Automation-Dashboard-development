import uuid
from datetime import datetime
import sys
from db_utils import get_db_connection

def ingest(raw_text):
    workflow_id = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO workflows (workflow_id, raw_text, status, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (workflow_id, raw_text, 'PENDING', timestamp))
    
    conn.commit()
    conn.close()
    return workflow_id

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "Sample business process: Review quarterly reports and assign tasks to the marketing team."
    
    wid = ingest(text)
    print(f"Workflow {wid} ingested.")
