"""Use existing read-only cached plotting wheels without changing project deps."""

import os
from pathlib import Path
import runpy
import sys

folder = Path(__file__).resolve().parent
root = folder.parents[2]
os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/tds-memo019-mpl")
sys.dont_write_bytecode = True
sys.path.insert(0, str(root / "src"))
base = Path.home() / ".cache/uv/archive-v0"
packages = ["matplotlib", "PIL", "cycler", "contourpy", "kiwisolver",
            "fontTools", "pyparsing", "packaging", "dateutil"]
for package in packages:
    matches = [p for p in base.iterdir() if (p / package / "__init__.py").is_file()]
    if matches:
        sys.path.append(str(matches[0]))
for p in base.iterdir():
    if (p / "six.py").is_file():
        sys.path.append(str(p))
        break
target = sys.argv[1] if len(sys.argv) > 1 else "build_examples.py"
runpy.run_path(str(folder / target), run_name="__main__")
