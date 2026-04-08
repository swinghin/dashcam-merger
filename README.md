# Dashcam Merger

A command-line tool that uses ffmpeg to concatenate a given list of video files.

## Usage

Open your terminal of choice, type in `python3 merge.py `, then drag your list of files into the terminal window. Or type in the file names one by one if you really hate yourself.

To specify the output directory, add `-o ` and drag in your desired folder, or create a file named `defaults.json` liek this example:

```json
{
  "output_dir": "/Volumes/Download",
}
```

## Example usage

Concatenate two video files `191901_00.TS` `192001_01.TS` and save to current working directory (or `output_dir` specified in `defaults.json`)

```bash
python3 merge.py 191901_00.TS 192001_01.TS
```

Concatenate two video files `191901_00.TS` `192001_01.TS` and save to specified directory `/Volumes/Download` (also overrides `output_dir` in `defaults.json`)

```bash
python3 merge.py 191901_00.TS 192001_01.TS -o /Volumes/Download
```

## Why does this exist

My dashcam records in 1 minute interval video files. I want to merge them into one single file for easy playback.
I used to have to manually create a list of video files that I need merging then type out an ffmpeg command in terminal to concatenate all the files... a waste of time and body energy if have mulitple journeys at a time to concatenate!
I decided to write this python script so I can drag a list of files into my terminal command and it auto outputs a merged video file.

## License

[AGPL 3.0](https://choosealicense.com/licenses/agpl-3.0/ 'AGPL 3.0 License')
