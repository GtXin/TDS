# S4 / S5 appendix study evidence

Owned memos: docs/memo/memoWX_021_Chan_xianduan.md and memoWX_022_Chan_zhongshu.md. Only appendices/references changed; main000–005 sections match pre-edit template backups byte-for-byte.

- `corpus_hits.txt`: one rg search over all108 numbered lessons,1779 matching lines for 线段/特征序列/中枢/重叠/次级别走势. This is keyword inventory, not an assertion of reading all lessons or all figures.
- `build_studies.py`: selected continuous source-block construction, style-only span removal and exact figure copies, memo pre-edit backups. Source author/editor distinctions are stated in each appendix. Do not run again after manual appendix edits without review; it regenerates the two appendices.
- `evidence.json`:9 selected original blocks and SHA-256,10 copied original figure hashes, pre-edit memo backups and preserved-section hashes. All10 originals were viewed; copied PNG/JPG/GIF bytes are unchanged.067 refers to figures that are absent in the supplied corpus; this is expressly recorded.
- `draw_manual_examples.py`: numerical assertions and two charts based solely on constructed input endpoints and manually inspected code branches, never importing CC. Segment example:16 strokes -> candidate geometry[0,2],[3,7],[8,12], N0/N1/N2 status distinction; center example:fixed[13,16], extension members4/5, close evidence7. Charts use input stroke/leg price lines and source axes, no fabricated OHLC candles.
- `manual_arithmetic.json`: literal inputs and passed arithmetic assertions. These checks establish displayed arithmetic, not engine behavior, full equivalence or correctness.
- `check_studies.py` / `checks.json`: source-block wording/hash, byte-identical figure copies and000–005, relative links, sequential citations and actual corpus count checks passed.

CC evidence: selected actual local snapshot374268381a3e (full HEAD in memos/manifest). No upstream repository changes, CC imports or CC execution. B covers current code, not unverified parity with the older public website snapshot.

Chart generation used existing proj009 Python/matplotlib3.11.1; TDS .venv lacks matplotlib. Initial chart run failed at matplotlib hlines(c=...), after producing first segment PNG; fixed to colors=..., preserved intermediate segment PNG under docs/memo/backups/memoWX_021_Chan_xianduan__20261109_033418_248195, reran successfully. Font-cache warnings resolved by temporary cache environment paths, no dependencies installed. Both final charts were visually inspected: all labels/axes/content visible. Corrected one center phase citation to actual file EOF128 after a separate pre-edit memo backup.
