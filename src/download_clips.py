import argparse
import json
from pathlib import Path


def download(args):
    import pandas as pd
    from tqdm import tqdm

    from extern.freesound import FreesoundClient, FSRequest, URIS

    import utils

    with open('client.json') as f:
        params = json.load(f)

    client = FreesoundClient()
    client.set_token(params['access_token'], auth_type='oauth')

    # Determine which clips to download
    df = pd.read_csv(args.work_dir / 'freesound_matches.csv', index_col=0)
    with open(args.work_dir / 'labels.txt') as f:
        label_set = f.read().strip().split('\n')

    # Load query results (to determine file extensions)
    results = utils.load_freesound_metadata(args.work_dir / 'query')
    results = results[results.index.isin(df.index)]
    results = results.join(df)

    # Select a subset of the clips to download
    # This saves time, space, and bandwidth
    results = select_subset(results, label_set, args.work_dir)

    # Ensure output directory exists
    download_dir = args.work_dir / 'downloads'
    download_dir.mkdir(parents=True, exist_ok=True)

    # Start downloading the selected clips
    results[['prediction']].to_csv(args.work_dir / 'download_list.csv')
    for index, row in tqdm(results.iterrows(), total=len(results)):
        path = Path(download_dir / f'{index}.{row.type}')
        if not path.exists():
            uri = URIS.uri(URIS.DOWNLOAD, index)
            try:
                FSRequest.retrieve(uri, client, path)
            except Exception as e:
                print(f'Unable to download sound {index}\nReason: {str(e)}')
                if 'Unauthorized' in str(e):
                    break


def select_subset(df, label_set, work_dir):
    import pandas as pd

    # Determine minimum number of clips to download per class
    df_train = pd.read_csv(work_dir / 'subset/train.csv', index_col=0)
    df_train = df_train[df_train.label.isin(label_set)]
    target_sizes = df_train.groupby(df_train.label).size()

    def _sample(x):
        n_samples = target_sizes[x.prediction][0]
        return x.sample(min(len(x), n_samples + 10))

    return df.groupby('prediction').apply(_sample).droplevel(0)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', type=Path, default=Path('_output'),
                        help='path to workspace directory')
    return parser.parse_args()


if __name__ == '__main__':
    download(parse_args())
