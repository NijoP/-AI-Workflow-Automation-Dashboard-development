import pytest
from extract_tasks import extract_tasks

def test_extract_tasks_basic():
    text = "Please assign the ticket to John. Also, review the document."
    tasks = extract_tasks(text)
    assert tasks == ["Please assign the ticket to John", "Also, review the document"]

def test_extract_tasks_no_tasks():
    text = "This is a regular sentence. It has no keywords."
    tasks = extract_tasks(text)
    assert tasks == []

def test_extract_tasks_case_insensitivity():
    text = "ASSIGN this. ReViEw that. CReaTe a PR. UpDaTe the docs. SeNd the email. MaNaGe the team."
    tasks = extract_tasks(text)
    assert tasks == [
        "ASSIGN this",
        "ReViEw that",
        "CReaTe a PR",
        "UpDaTe the docs",
        "SeNd the email",
        "MaNaGe the team"
    ]

def test_extract_tasks_whitespace_stripping():
    text = "  Please update the server.   \n\n  Send a message to admin.  "
    tasks = extract_tasks(text)
    assert tasks == ["Please update the server", "Send a message to admin"]

def test_extract_tasks_multiple_keywords():
    text = "Please assign and review the document."
    tasks = extract_tasks(text)
    assert tasks == ["Please assign and review the document"]

def test_extract_tasks_empty_string():
    text = ""
    tasks = extract_tasks(text)
    assert tasks == []

def test_extract_tasks_only_keywords():
    text = "assign. review. create. update. send. manage."
    tasks = extract_tasks(text)
    assert tasks == ["assign", "review", "create", "update", "send", "manage"]

def test_extract_tasks_keywords_as_substrings():
    # The current implementation checks `word in line.lower()`.
    # 'assign' is a word, but 'assignment' contains 'assign'.
    # If the implementation does a simple string inclusion, it will match.
    text = "Here is the assignment. Sendings are paused."
    tasks = extract_tasks(text)
    assert tasks == ["Here is the assignment", "Sendings are paused"]
