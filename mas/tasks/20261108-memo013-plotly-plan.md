# Memo013 Plotly scope and appendix
## Task
- **ID:** 20261108-memo013-plotly-plan
- **Goal:** Restore memo009 plotting requirement in memo013 and add an essential Plotly appendix.
- **Inputs:** memos009/013, existing implementation, official Plotly candlestick/subplot/HTML documentation.
- **Allowed changes:** Backed-up memo013 scope/plan/status/interface note/appendix/references, this task, memory and event log. No source, package or dataset changes in this documentation request.
- **Acceptance checks:** Clear selected package and pending implementation status; concise interface/boundary/dependency/chart/export/check details; preserve existing implemented example; links, numbering and whitespace checks.
- **Assignment:** Root edits/verifies; independent read-only review.
- **Status:** done
## Result and handoff
- **Outcome:** Updated plotting requirement and added appendix; not claiming plotting is implemented.
- **Evidence:** docs/memo/memoWX_013_klineFamily.md; complete timestamped backup before edit.
- **Blockers:** none for documentation.
- **Next action:** Verify documentation, then implement the specified plotting extension as the next coding action.

## Protected source/configuration hashes
```json
{
  "src/chanlab/algo/chan_table.py": "9b148028614bca7064fe5ad0cdfc7ad574785b3c6ab751d5391f886521e457a3",
  "src/chanlab/algo/kline.py": "823f3a66cec5988c1b2f4f8e14f4a9e5d97bf6d1cc3d763c7ed2fa695d37a739",
  "src/chanlab/data/chan_table_csv.py": "a0d3fd2ef1b021716e5be11a6cf011c97dee7e31463fea9c0ef3c5bd37cd824f",
  "src/chanlab/data/kline_csv.py": "dc165bcbf20d2967ab2e13176166c80e43ba836db55062094ec4f455c9a37c77",
  "pyproject.toml": "49f49b05bca357e4f804c6b22754c93ebf14e71bc29adaf43a0c2f5dba035527",
  "uv.lock": "987df5b1222e27ab1e3d30e61dd6c3f0aa652fa1150419970ea586dc1632775f"
}
```

## Verification
- Independent read-only review passed consistency, essential detail and clear planned-versus-implemented status.
- Confirmed existing003.c example unchanged; both Python blocks parse. Planned plot example was not executed because the method is not implemented.
- Appendix/API/dependency/status checks, local links, references1–6, source/configuration hashes and git diff --check passed. No packages installed or code/data changed.
- Documentation request complete. Plotly implementation/testing remains the next coding action; prior165-test result is explicitly limited to existing raw/CSV functionality.

## Implementation follow-through
The documented plotting extension is now implemented and verified; current code/samples/cohesive003 update are recorded in mas/tasks/20261108-memo013-plotly-implementation.md. Earlier pending statements describe the documentation-only stage.
