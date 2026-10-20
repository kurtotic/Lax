#!/usr/bin/env python3
"""Retired placeholder generator. The catalog is built from the sheet export."""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "import_sheet.py"), run_name="__main__")
