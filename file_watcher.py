import os
import shutil
import time
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.resolve()
INBOX = VAULT_ROOT / "Inbox"
NEEDS_ACTION = VAULT_ROOT / "Needs_Action"

POLL_INTERVAL = 2  # seconds


def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def suggest_actions(suffix):
    suggestions = {
        ".md": "- [ ] Review content\n- [ ] Apply summarize-file skill if applicable",
        ".txt": "- [ ] Read and categorize\n- [ ] Summarize if needed",
        ".pdf": "- [ ] Extract text\n- [ ] Summarize key points",
        ".csv": "- [ ] Analyze data\n- [ ] Generate report",
        ".docx": "- [ ] Review document\n- [ ] Summarize key points",
        ".png": "- [ ] Review image\n- [ ] Add description",
        ".jpg": "- [ ] Review image\n- [ ] Add description",
    }
    return suggestions.get(suffix.lower(), "- [ ] Review file\n- [ ] Determine appropriate action")


def create_metadata(dest_path, original_name):
    meta_path = dest_path.with_suffix(dest_path.suffix + ".meta.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    suffix = Path(original_name).suffix

    content = f"""---
original_filename: {original_name}
moved_to_needs_action: {timestamp}
file_type: {suffix if suffix else "unknown"}
priority: normal
status: pending
---

# Task: {original_name}

**Source:** /Inbox
**Detected:** {timestamp}

## Suggested Actions

{suggest_actions(suffix)}
"""
    meta_path.write_text(content, encoding="utf-8")
    return meta_path.name


def process_file(filepath):
    original_name = filepath.name
    timestamp = get_timestamp()
    new_name = f"{timestamp}_{original_name}"
    dest = NEEDS_ACTION / new_name

    shutil.move(str(filepath), str(dest))
    meta_name = create_metadata(dest, original_name)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] New file detected: {original_name}")
    print(f"  -> Moved to: /Needs_Action/{new_name}")
    print(f"  -> Metadata: /Needs_Action/{meta_name}")
    print()


def watch():
    print("=" * 50)
    print("Atlas File Watcher")
    print(f"Watching: {INBOX}")
    print(f"Moving to: {NEEDS_ACTION}")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    print()

    INBOX.mkdir(exist_ok=True)
    NEEDS_ACTION.mkdir(exist_ok=True)

    while True:
        try:
            for item in INBOX.iterdir():
                if item.is_file():
                    try:
                        process_file(item)
                    except Exception as e:
                        print(f"[ERROR] Failed to process {item.name}: {e}")
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\nWatcher stopped.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    watch()
