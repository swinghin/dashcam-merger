#!/usr/bin/env python3
"""
process_files.py

A tiny utility that accepts a list of files on the command line and can
perform different actions based on optional flags.

Supported options
-----------------
--verbose       : Print a bit more detail for every file.
--dry-run       : Show what would happen, but don’t actually touch the file system.
--output-dir DIR: If supplied, copy every valid input file into this directory
                  (creates the dir if it does not exist).
--hash          : Instead of copying, compute and display a SHA‑256 hash.
"""

import argparse
import hashlib
import os
import shutil
import sys


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process a list of files given on the command line."
    )

    # Positional argument: one or more file names
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="+",
        help="Path to a file that should exist.",
    )

    # Optional flags
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print more information for each file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen, but do not modify the file system.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="DIR",
        help="Copy every valid file into DIR.",
    )
    parser.add_argument(
        "-H",
        "--hash",
        action="store_true",
        help="Compute and display a SHA‑256 hash for each file instead of copying.",
    )

    return parser.parse_args()


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def compute_hash(path: str) -> str:
    """Return the SHA‑256 hash of a file as a hex string."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def copy_file(src: str, dst_dir: str) -> None:
    """Copy a file to the destination directory (keeping its base name)."""
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, os.path.basename(src))
    shutil.copy2(src, dst)


# --------------------------------------------------------------------------- #
# Main logic
# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()

    all_ok = True

    for path in args.files:
        abs_path = os.path.abspath(path)

        if not os.path.isfile(abs_path):
            print(f"[ERR]  File not found: {abs_path}", file=sys.stderr)
            all_ok = False
            continue

        if args.verbose:
            print(f"[OK]   Processing: {abs_path}")

        # ---- hash mode ----------------------------------------------------
        if args.hash:
            h = compute_hash(abs_path)
            print(f"SHA‑256: {h}   ({abs_path})")
            continue

        # ---- default mode (just confirm existence) ----------------------
        if not args.dry_run:
            print(f"[OK]   File exists: {abs_path}")

    if all_ok:

        output_dir = os.path.expanduser("~") if not args.output_dir else args.output_dir

        ff_file_list = ["file '" + filepath + "'" for filepath in args.files]

        first_file_name = os.path.splitext(os.path.basename(args.files[0]))[0]

        ff_file_list_path = os.path.join(output_dir, first_file_name + ".txt")
        
        print(ff_file_list_path)

        # with open(f"{output_dir}/{first_file_name}.txt", "w", encoding="utf-8") as f:
        #     for line in ff_file_list:
        #         f.write(line + "\n")

        # # ---- copy mode ----------------------------------------------------
        # if args.output_dir:
        #     if args.dry_run:
        #         print(f"[DRY]  Would output {abs_path} to {args.output_dir}")
        #     else:
        #         try:
        #             copy_file(abs_path, args.output_dir)
        #             print(f"[COPY] {abs_path} -> {args.output_dir}")
        #         except Exception as e:
        #             print(f"[ERR]  Could not copy {abs_path}: {e}", file=sys.stderr)
        #             all_ok = False

    # Exit code: 0 if all files were OK, otherwise non‑zero
    sys.exit(0 if all_ok else 1)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
