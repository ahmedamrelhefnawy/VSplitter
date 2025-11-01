import os
import json
from typing import List, Tuple
import asyncio
from ffmpeg.asyncio import FFmpeg
from ffmpeg_setup import ensure_ffmpeg

def fix_intervals(clip_ranges: List[Tuple[str, List[str]]]):
    '''Fixes the missing time stamps in intervals'''
    for i, split in enumerate(clip_ranges):

        assert len(split) == 2, f"Expected a list of length of 2 [Name: str, Interval: list[str]] as a split, got {len(split)}: {split}"

        name, interval = split
        assert 0 < len(interval) < 3, f'Conflict in interval {interval}, file: {name}'

        if len(interval) == 1:
            if i == 0:  # First interval
                interval.insert(0, '00:00:00')
            elif i == len(clip_ranges)-1:  # Last interval
                pass # Handled Later
            else:  # Interval in-between
                _, prev_interval = clip_ranges[i-1]
                prev_end = prev_interval[-1]
                interval.insert(0, prev_end)

    return clip_ranges

async def build_clip(source_path: str, file_output_path: str, config: dict):
    await FFmpeg().option('y').input(source_path).output(file_output_path, config).execute()
    print(f"{file_output_path.split('/')[-1]} was built sucessfully.")
    
async def main():
    # Ensure FFmpeg is available
    print("Checking FFmpeg availability...")
    ffmpeg_path = ensure_ffmpeg()
    print(f"Using FFmpeg at: {ffmpeg_path}\n")
    
    tasks = []
    
    # Read Config
    with open('./split_config.json', 'r') as f:
        splits_config = json.load(f)

    output_dir = splits_config['output_dir']
    os.makedirs(output_dir, exist_ok=True)

    for source in splits_config['source_files']:
        # Extract needed information
        source_path = source['path']
        source_ext = source_path.split('.')[-1]
        clip_ranges = source['clip_ranges']

        # Fix missing time stamps
        clip_ranges = fix_intervals(clip_ranges)

        for i, split in enumerate(clip_ranges):
            name, interval = split
            assert 0 < len(interval) < 3, f'Incompatible interval length {len(interval)} -> {interval}, file: {name}'

            config = {"codec:v": "copy", "codec:a": "copy"}

            # Building the final output path
            file_name = name+'.'+source_ext
            file_output_path = os.path.join(output_dir, file_name)

            if i == len(clip_ranges)-1 and len(interval) == 1: # The last split & only one time-stamp given
                start = interval[0]
                end = ''
            else:
                start, end = interval

            config['ss'] = start
            if end:
                config['to'] = end

            tasks.append(build_clip(source_path, file_output_path, config))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
