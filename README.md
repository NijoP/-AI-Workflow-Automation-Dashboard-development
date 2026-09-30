# AI Workflow Automation Engine

Deterministic AI workflow automation dashboard demonstrating business process automation.

## Features
- **Atomic Processing:** Modular scripts for ingestion, processing, and extraction.
- **Deterministic Logging:** SQLite-backed workflow tracking.
- **Modern Dashboard:** Reactive UI with Tailwind CSS and Vue.js.
- **Health Monitoring:** Built-in health check system.

## Project Structure
- `ingest_workflow.py`: Accepts raw text and stores it.
- `process_text.py`: Generates summaries and calls extraction tools.
- `extract_tasks.py`: Rule-based deterministic task extraction.
- `server.py`: Lightweight Python server providing a JSON API and serving the dashboard.
- `health_check.py`: System integrity verification.
- `index.html`: Dashboard UI.

## How to Run
1. Initialize the database:
   ```bash
   python3 init_db.py
   ```
2. Start the server:
   ```bash
   python3 server.py
   ```
3. Open `http://localhost:8000` in your browser.

## Data Schema
### Input
```json
{
  "workflow_id": "string",
  "raw_text": "string",
  "timestamp": "iso8601"
}
```
### Output
```json
{
  "summary": "string",
  "tasks": ["array"],
  "priority_items": ["array"],
  "processing_time_ms": "number"
}
```
