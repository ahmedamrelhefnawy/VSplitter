# FFMPEG Video Splitter

A Python-based tool to automatically split video files into multiple clips using FFMPEG, configured through a JSON file.

## Prerequisites

- Python 3.12.7 or higher
- FFmpeg installed on your system

### Installing FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install python-ffmpeg pyyaml
```

Or if you're using uv or pip with pyproject.toml:
```bash
pip install -e .
```

## Usage

1. Create a `split_config.json` file in the project directory (see configuration below)
2. Run the script:

```bash
python main.py
```

The tool will process all source files defined in the configuration and create the video clips in the specified output directory.

## Configuration File Structure

Create a `split_config.json` file with the following structure:

```json
{
  "output_dir": "path/to/output/directory",
  "source_files": [
    {
      "path": "/path/to/source/video.mp4",
      "clip_ranges": [
        ["Clip Name 1", ["start_time", "end_time"]],
        ["Clip Name 2", ["start_time", "end_time"]],
        ["Clip Name 3", ["start_time"]]
      ]
    }
  ]
}
```

### Configuration Parameters

- **`output_dir`**: Directory where the split video files will be saved. Use `"."` for the current directory.
- **`source_files`**: Array of source video files to process
  - **`path`**: Full path to the source video file
  - **`clip_ranges`**: Array of clips to extract from the video
    - Each clip is defined as: `["Clip Name", ["timestamps"]]`

### Time Stamp Format

Time stamps should be in the format: `H:MM:SS` or `HH:MM:SS`

Examples: `"0:19:22"`, `"1:05:30"`, `"00:00:15"`

## Time Stamp Rules

### Default Behavior
By default, you specify both the **start** and **end** time for each clip:
```json
["Clip Name", ["0:10:00", "0:20:00"]]
```

### Single Time Stamp Shortcuts
If only **one** time stamp is provided, the behavior depends on the clip's position:

#### 1. **First Clip** (single timestamp)
- **Start**: Beginning of the video (`00:00:00`)
- **End**: The provided timestamp

```json
["Introduction", ["0:05:30"]]
```
This extracts from the start of the video to 5 minutes 30 seconds.

#### 2. **Last Clip** (single timestamp)
- **Start**: The provided timestamp
- **End**: End of the video

```json
["Conclusion", ["1:45:00"]]
```
This extracts from 1 hour 45 minutes to the end of the video.

#### 3. **In-Between Clips** (single timestamp)
- **Start**: End time of the previous clip
- **End**: The provided timestamp

```json
["Chapter 1", ["0:10:00"]],
["Chapter 2", ["0:25:00"]],
["Chapter 3", ["0:40:00"]]
```
- Chapter 1: `00:00:00` to `0:10:00`
- Chapter 2: `0:10:00` to `0:25:00`
- Chapter 3: `0:25:00` to `0:40:00`

## Example Configuration

```json
{
  "output_dir": "./output",
  "source_files": [
    {
      "path": "/media/videos/lecture.mp4",
      "clip_ranges": [
        ["01 - Introduction", ["0:05:30"]],
        ["02 - Main Topic", ["0:15:45", "0:45:20"]],
        ["03 - Advanced Concepts", ["1:10:30"]],
        ["04 - Q&A Session", ["1:30:00"]]
      ]
    },
    {
      "path": "/media/videos/workshop.mp4",
      "clip_ranges": [
        ["Part 1", ["0:00:00", "0:30:00"]],
        ["Part 2", ["0:30:00", "1:00:00"]],
        ["Part 3", ["1:00:00"]]
      ]
    }
  ]
}
```

This configuration will:
- Create an `output` directory in the current folder
- Process two video files
- Extract 4 clips from `lecture.mp4` and 3 clips from `workshop.mp4`
- Name each output file according to the clip name (e.g., `01 - Introduction.mp4`)

## Features

- **Fast processing**: Uses codec copy to avoid re-encoding (instant splitting)
- **Async execution**: Processes videos asynchronously for better performance
- **Flexible time stamps**: Support for single or dual timestamp notation
- **Multiple source files**: Process multiple videos in one configuration
- **Automatic time calculation**: Intelligently fills in missing timestamps based on clip position

## Notes

- The tool uses FFmpeg's copy codec, which means no re-encoding occurs. This makes the splitting process very fast.
- Output files are named exactly as specified in the configuration with the same file extension of the source video file.
- If the output file already exists, it will be overwritten (`-y` flag)