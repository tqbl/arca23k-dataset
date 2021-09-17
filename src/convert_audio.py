import argparse
import subprocess
import sys
from pathlib import Path


def convert(args):
    # Ensure output directory exists
    output_dir = args.work_dir / 'audio'
    output_dir.mkdir(parents=True, exist_ok=True)

    downloads_dir = args.work_dir / 'downloads'
    for path in downloads_dir.iterdir():
        output_path = output_dir / (path.stem + '.wav')
        if not output_path.exists():
            cmd = f'ffmpeg -i {path} -sample_fmt s16 -ar 44100 ' \
                  f'-ac 1 -acodec pcm_s16le {output_path}'
            subprocess.run(cmd.split())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', type=Path, default=Path('_output'),
                        help='path to workspace directory')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(convert(parse_args()))
