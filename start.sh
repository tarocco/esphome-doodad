#!/bin/bash
set -e
source "./.venv/bin/activate"
PYTHON_BIN="$(which python)"
"$PYTHON_BIN" "./main.py"
