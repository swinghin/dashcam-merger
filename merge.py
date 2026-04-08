#!/usr/bin/env python3
"""
dashcam.py

A command-line tool that uses ffmpeg to concatenate a given list of video files.

Supported options
-----------------
--output-dir DIR: If supplied, copy every valid input file into this directory
                  (creates the dir if it does not exist).
"""

import argparse
import os
import shutil
import subprocess
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

    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="DIR",
        help="Copy every valid file into DIR.",
    )

    return parser.parse_args()


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #


def ffmpeg_concat(concat_list: str, filename: str):
    # ffmpeg -f concat -safe 0 -i 2019_0821_121834_550.txt -c copy 2019_0821_121834_550.MOV

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise RuntimeError("ffmpeg not found in PATH")

    ffmpeg_cmd = [
        ffmpeg_path,
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_list,
        "-c",
        "copy",
        filename,
        "-y",
    ]

    result = subprocess.run(
        ffmpeg_cmd,
        capture_output=True,  # capture stdout & stderr
        text=True,  # return strings instead of bytes
    )

    # Raise an exception if ffmpeg failed (non‑zero exit code)
    result.check_returncode()

    return result


# --------------------------------------------------------------------------- #
# Main logic
# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()

    all_files_ok = True

    for path in args.files:
        abs_path = os.path.abspath(path)

        if not os.path.isfile(abs_path):
            print(f"[ERR]  File not found: {abs_path}", file=sys.stderr)
            all_files_ok = False
            continue

        print(f"[OK]   File exists: {abs_path}")

    if not all_files_ok:
        print("Some files are missing, aborted merge")

    # Default output dir is home folder if not provided as command line argument
    output_dir = os.path.expanduser("~") if not args.output_dir else args.output_dir

    # Build the ffmpeg concat file list
    ff_file_list = ["file '" + filepath + "'" for filepath in args.files]

    # Get the first video file name and extension
    first_file = os.path.basename(args.files[0])
    first_file_name = os.path.splitext(first_file)[0]

    # Build the ffmpeg concat file list txt file path
    ff_file_list_path = os.path.join(output_dir, first_file_name + ".txt")
    ff_file_output = os.path.join(output_dir, first_file)

    # Write the ffmpeg concat file list to disk
    with open(ff_file_list_path, "w", encoding="utf-8") as f:
        for line in ff_file_list:
            f.write(line + "\n")

    #
    try:
        proc = ffmpeg_concat(ff_file_list_path, ff_file_output)
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed (code {e.returncode})")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        sys.exit(e.returncode)

    os.remove(ff_file_list_path)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
