"""Reproduce memo013's object-only CSV and plotting workflow."""

import hashlib
import json
from pathlib import Path

from chanlab.algo.kline import KlineTSeries


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    folder = root / "samples/chan_table"
    master = next(folder.glob("*chan_table*.csv"))
    metadata = next(folder.glob("*context*.csv"))
    series = KlineTSeries.read_csv(master, metadata)
    output = Path(__file__).resolve().parent / "roundtrip"
    output.mkdir(exist_ok=True)
    data_path, context_path = output / "raw.csv", output / "context.csv"
    series.write_csv(data_path, context_path)
    restored = KlineTSeries.read_csv(data_path, context_path)
    assert restored == series
    assert len(restored) == 10060
    assert restored.context == series.context
    figure = restored.plot(start=-40, volume=True)
    assert tuple(figure.data[0].x) == tuple(bar.timestamp for bar in series[-40:])
    assert tuple(figure.data[1].y) == tuple(bar.volume for bar in series[-40:])
    protected = json.loads((output.parent / "protected-hashes.json").read_text())
    assert all(
        hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
        for path, digest in protected.items()
    )
    report = {
        "rows": len(restored),
        "owned_context_keys": len(restored.context),
        "object_roundtrip_equal": restored == series,
        "plot_trace_values_match": True,
        "source_images_and_configuration_unchanged": True,
        "raw_export_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "context_export_sha256": hashlib.sha256(context_path.read_bytes()).hexdigest(),
    }
    (output.parent / "method-verification.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
