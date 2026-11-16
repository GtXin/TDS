#!/usr/bin/env python3
"""Check staged blobs, or outgoing history relative to origin/main."""
import subprocess
import sys


def git(*args):
    return subprocess.check_output(['git', *args])


if '--history' in sys.argv:
    objects = git('rev-list', '--objects', 'origin/main..HEAD')
else:
    entries = git('ls-files', '--stage', '-z').split(b'\0')
    objects = b'\n'.join(e.split(b' ', 2)[1] + b' ' + e.split(b'\t', 1)[1]
                         for e in entries if e)
result = subprocess.run(
    ['git', 'cat-file', '--batch-check=%(objecttype) %(objectname) %(objectsize) %(rest)'],
    input=objects, stdout=subprocess.PIPE, check=True)
errors = 0
for line in result.stdout.splitlines():
    parts = line.split(b' ', 3)
    if parts[0] != b'blob':
        continue
    size = int(parts[2])
    if size > 50 * 1024**2:
        blocked = size >= 100 * 1024**2
        errors += blocked
        print(f"{'ERROR' if blocked else 'WARNING'} {size / 1024**2:.1f} MiB: "
              + parts[3].decode(errors='replace'))
print(f'Size check: {errors} blocking blobs')
sys.exit(bool(errors))
