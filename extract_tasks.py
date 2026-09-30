import sqlite3
import json
import time
import sys

TASK_KEYWORDS = ('assign', 'review', 'create', 'update', 'send', 'manage')

def extract_tasks(text):
    # Deterministic task extraction logic (mocking LLM for now)
    lines = text.split('.')
    tasks = []
    for line in lines:
        lower_line = line.lower()
        for word in TASK_KEYWORDS:
            if word in lower_line:
                tasks.append(line.strip())
                break
    return tasks

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(extract_tasks(sys.argv[1])))
