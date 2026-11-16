# GitHub file size policy and recovery

## 000 — Background
GitHub rejected synchronization because two generated results in local commit `54a2f1a` exceed its 100 MiB file limit. Ignoring an already committed file does not repair history.[1]

## 001 — Storage decision
Keep the original JSON files locally and ignore their exact paths. Track lossless `results.json.gz` copies in `artifacts/mas/memo030-full/` and `artifacts/mas/memo030-four/`. Byte sizes and original SHA-256 hashes are in `artifacts/mas/github-size-fix/manifest.json`. Raw datasets and algorithms are unchanged.

On a fresh clone, restore inputs before using the existing run/plot/verify scripts:

```sh
gzip -dk artifacts/mas/memo030-full/results.json.gz
gzip -dk artifacts/mas/memo030-four/results.json.gz
```

After regenerating either JSON, refresh its compressed copy with `gzip -n -c path/to/results.json > path/to/results.json.gz` and refresh the manifest hashes. Never stage the ignored original.

## 002 — Prevention and history repair
Run `python3 scripts/check_git_sizes.py` before committing and add `--history` before pushing. The check warns above 50 MiB and rejects blobs at or above 100 MiB. Install the commit guard in each clone using `git config core.hooksPath .githooks`.

The oversized files occur only in the latest unpublished commit. Preserve that commit in a recovery bundle outside the repository, then amend it with the compressed replacements and policy changes. Verify outgoing history contains no oversized blobs; use a normal push. Shared history must not be rewritten without approval.

## References
[1] [GitHub: About large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
