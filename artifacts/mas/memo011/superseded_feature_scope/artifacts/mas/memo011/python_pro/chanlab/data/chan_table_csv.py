"""File adapters for the ChanTable CSV and its provenance context."""

from pathlib import Path

from chanlab.algo.chan_table import ChanTable


def read_chan_table(path: Path, context_path: Path | None = None) -> ChanTable:
    """Load the raw-axis view; feature records must be registered separately."""
    return ChanTable.read_csv(path, context_path)


def write_chan_table(
    table: ChanTable, path: Path, context_path: Path | None = None
) -> None:
    """Write a view and optional context without inferring feature records."""
    table.write_csv(path, context_path)
