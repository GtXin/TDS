"""Reproduce the default gap-free overlay through MergedKlineSeries.plot()."""

from pathlib import Path
import runpy

# One renderer powers the class method and all current sample pictures.
runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "merged-kline-plot-options/generate.py"),
    run_name="__main__",
)
