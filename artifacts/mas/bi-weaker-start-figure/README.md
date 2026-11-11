# Initialization2.b illustration

`initialization-2b.png` is the current requested figure: before any qualified first pair, weaker same-kind B leaves the pending start A unchanged; stronger same-kind D replaces A. Both intervening opposite fractals fail old-stroke spacing. No endpoint C or cached Bi002 exists yet.

`weaker-start-2b.png` is the earlier geometric alternative-start illustration. Its valid later B→C does not by itself refute the local instruction to keep A as the current pending start. It answers a separate question about permanently eliminating alternative starts. The user corrected the discussion scope before delivery.

Both figures use synthetic continuous merged high/low ranges, not market OHLC. `draw.py` verifies the data and renders both PNGs through native AppKit; corresponding JSON records retain the exact ranges, checks and image hashes. Source and algorithm memos were not changed.

Reproduce from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python artifacts/mas/bi-weaker-start-figure/draw.py
```
