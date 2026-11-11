#!/bin/bash

# merge.sh
# This script merges a list of video files using ffmpeg's concat demuxer.
#
# Usage: ./merge.sh [options] file1 [file2 ...]
#
# Options:
# -o DIR  Specify the output directory (e.g., /path/to/output).
#
# Example: ./merge.sh -o /path/to/output file1.mp4 file2.mp4
# Example: ./merge.sh file1.mp4 file2.mp4

# --- Configuration ---
set -euo pipefail

# --- Variables ---
# Initial default values
OUTPUT_DIR="."
# Use Process ID ($$) to make the temporary file unique and concurrency-safe
FILE_LIST_FILE="temp_file_list_$$"
INPUT_FILES=()

# --- Functions ---

# Cleanup function to remove the temporary list file
cleanup() {
    echo "Cleaning up temporary files..."
    rm -f "$FILE_LIST_FILE"
}
# Ensure cleanup runs even if the script is interrupted
trap cleanup EXIT

# Function to display usage instructions
usage() {
    echo "Usage: $0 [options] file1 [file2 ...]"
    echo
    echo "Arguments:"
    echo "  file1 [file2 ...]: Paths to the video files to be concatenated."
    echo "Options:"
    echo "  -o DIR            Specify the output directory (e.g., /path/to/output)."
    echo "  -h | --help       Show this help message."
    exit 1
}

# Function to check for necessary tools
check_dependencies() {
    if ! command -v ffmpeg &> /dev/null; then
        echo "[ERROR] ffmpeg is not installed or not in the PATH." >&2
        exit 1
    fi
    echo "[INFO] Dependencies met: ffmpeg found."
}

# Function to load default configuration from defaults.cfg (Key=Value format)
load_defaults() {
    local defaults_path="settings.cfg"
    if [ -f "$defaults_path" ]; then
        echo "[INFO] Found settings.cfg, attempting to load output_dir..."
        # Use grep and awk to safely extract the value, ignoring comments and empty lines
        local output_dir_from_defaults
        output_dir_from_defaults=$(grep '^output_dir=' "$defaults_path" | head -n 1 | awk -F'=' '{print $2}' | xargs)

        if [ -z "$output_dir_from_defaults" ]; then
            echo "[INFO] settings.cfg does not contain a valid 'output_dir' key."
        else
            OUTPUT_DIR="$output_dir_from_defaults"
            echo "Setting default output directory to: $OUTPUT_DIR"
        fi
    else
        echo "[WARNING] settings.cfg not found. Using initial default output directory: $OUTPUT_DIR"
    fi
}

# --- Main Logic ---
main() {

    # 1. Load configuration from settings.cfg
    load_defaults

    # 2. Parse command line arguments (file check is done after defaults are loaded)
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output-dir)
                if [ -n "$2" ] && [ ! "$2" =~ ^- ]]; then
                    OUTPUT_DIR="$2"
                    shift 2
                else
                    echo "[ERROR] -o argument requires an argument." >&2
                    usage
                fi
                ;;
            -h|--help)
                usage
                ;;
            *)
                # Treat remaining arguments as input files
                INPUT_FILES+=("$1")
                shift
                ;;
        esac
    done

    # Check if any input files were provided
    if [ ${#INPUT_FILES[@]} -eq 0 ]; then
        echo "[ERROR] No input files provided. Use -h for usage." >&2
        exit 1
    fi

    check_dependencies

    echo "[INFO] Starting merge process..."

    # 3. Validate all input files and build the concat list
    for file_path in "${INPUT_FILES[@]}"; do
        if [ ! -f "$file_path" ]; then
            echo "[ERROR] Input file not found: $file_path" >&2
            exit 1
        fi
        # Use realpath for cross-platform safety, although ffmpeg is generally robust
        echo "file '$(realpath "$file_path")'" >> "$FILE_LIST_FILE"
    done

    # Determine output file path
    local base_name=$(basename "${INPUT_FILES[0]}")
    local file_name_no_ext="${base_name%.*}"
    local output_file="${OUTPUT_DIR}/${file_name_no_ext}.mp4"

    # 4. Ensure output directory exists
    if [ ! -d "$OUTPUT_DIR" ]; then
        echo "[INFO] Output directory does not exist. Creating $OUTPUT_DIR..."
        if ! mkdir -p "$OUTPUT_DIR"; then
            echo "[FATAL] Failed to create output directory: $OUTPUT_DIR" >&2
            exit 1
        fi
    fi

    echo "[INFO] Target output file is: $output_file"

    # 5. Execute ffmpeg
    echo "[INFO] Starting FFmpeg concatenation..."
    # The -safe 0 flag is needed to allow absolute paths used in the concat file.
    if ffmpeg -f concat -safe 0 -i "$FILE_LIST_FILE" -c copy "$output_file" -y; then
        echo ""
        echo "=========================================="
        echo "[SUCCESS] Video concatenation completed successfully!"
        echo "Output file available at: $output_file"
        echo "=========================================="
    else
        # FFmpeg failed (non-zero exit code)
        echo "[ERROR] FFmpeg failed during concatenation." >&2
        exit 1
    fi
}

# Execute the main function
main "$@"