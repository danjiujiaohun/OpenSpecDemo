import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "todo"


def run_todo(args, data_home):
    env = os.environ.copy()
    env["XDG_DATA_HOME"] = str(data_home)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        env=env,
        capture_output=True,
        text=True,
    )


def data_file(data_home):
    return Path(data_home) / "todo" / "todos.json"


def write_data(data_home, data):
    path = data_file(data_home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def read_data(data_home):
    return json.loads(data_file(data_home).read_text(encoding="utf-8"))
