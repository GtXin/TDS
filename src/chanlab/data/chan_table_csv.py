"""File adapters for the ChanTable CSV and its provenance context."""

from pathlib import Path

from chanlab.algo.chan_table import ChanTable


def read_chan_table(path: Path, context_path: Path | None = None) -> ChanTable:
    """Load the raw master table and optional provenance context."""
    return ChanTable.read_csv(path, context_path)


def write_chan_table(
    table: ChanTable, path: Path, context_path: Path | None = None
) -> None:
    """Write the raw master table and optional provenance context."""
    table.write_csv(path, context_path)
