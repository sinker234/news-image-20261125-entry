"""Entrypoint for the news-image-20261125 make.fun entry.

The grader runs this program twice with no network in a fresh
container; both runs must write the same bytes to /output/entry.png.
This program draws the broadsheet in code (see draw.py) instead of
copying a stored image, so the output is fully reproducible from the
repository alone.

Output directory resolution, in order:
  1. $MAKEFUN_OUTPUT_DIR (what the kit uses locally)
  2. /output (what the grader provides)
  3. the current working directory (fallback for a manual run)

After rendering it verifies the result before exiting: the file must
exist, be a whole 1024x1024 PNG, and be at most 1 MiB. It prints the
byte size and sha256 so a caller can confirm two runs agree.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import draw  # noqa: E402  (local module, shipped in this repository)

EXPECTED_SIZE = (1024, 1024)
MAX_BYTES = 1024 * 1024


def resolve_output_dir():
    """Pick where entry.png goes, preferring the kit/grader locations."""
    for candidate in (os.environ.get("MAKEFUN_OUTPUT_DIR"), "/output", "."):
        if not candidate:
            continue
        if os.path.isdir(candidate) and os.access(candidate, os.W_OK):
            return candidate
    # Last resort: create ./out next to the program.
    fallback = os.path.join(HERE, "out")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def verify_png(path):
    """Check the rendered file is a whole 1024x1024 PNG under 1 MiB."""
    from PIL import Image

    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise SystemExit("entry.png too big: %d bytes" % size)
    with Image.open(path) as img:
        if img.format != "PNG":
            raise SystemExit("entry.png is not a PNG: %s" % img.format)
        if img.size != EXPECTED_SIZE:
            raise SystemExit("entry.png is %s, want 1024x1024" % (img.size,))
        img.load()  # forces a full decode: catches truncated data
    return size


def main():
    out_dir = resolve_output_dir()
    out_path = os.path.join(out_dir, "entry.png")
    end_y = draw.render(out_path)
    nbytes = verify_png(out_path)
    with open(out_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print("entry.png: %d bytes, sha256=%s, layout ends y=%d, stories=%d"
          % (nbytes, digest, end_y, draw.story_count()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
