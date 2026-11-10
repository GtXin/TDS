"""Reproduce the gap-free two-panel picture through MergedKlineSeries.plot()."""

from pathlib import Path
import runpy

# The shared production-method sample runner also exports overlay/calendar examples.
runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "merged-kline-plot-options/generate.py"),
    run_name="__main__",
)
