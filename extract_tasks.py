import sqlite3
import json
import time
import sys

def extract_tasks(text):
    # Deterministic task extraction logic (mocking LLM for now)
    lines = text.split('.')
    tasks = [line.strip() for line in lines if any(word in line.lower() for word in ['assign', 'review', 'create', 'update', 'send', 'manage'])]
    return tasks

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(extract_tasks(sys.argv[1])))
