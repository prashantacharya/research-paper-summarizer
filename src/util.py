import json
from pathlib import Path
from nanoid import generate

def get_id():
    nanoid = generate(size=10)
    return nanoid


def get_file_name_from_id(id):
    return id.replace("_", " ") + ".pdf"


def load_existing_log(log_file):
    """Load existing summaries from the log file if it exists."""
    if Path(log_file).is_file():
        with open(log_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Existing log file is corrupted. Starting fresh.")
                return []
    return []


def is_already_summarized(file_name, log_data):
    """Check if a file has already been summarized by looking it up in the log data."""
    return any(entry["file"] == file_name for entry in log_data)


def save_log(log_data, log_file):
    """Save the log data to the log file."""
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=4)
