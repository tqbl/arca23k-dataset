import argparse
import sys
from pathlib import Path


def curate(args):
    import pandas as pd
    from tqdm import tqdm

    with open(args.work_dir / 'labels.txt') as f:
        label_set = f.read().strip().split('\n')

    # Create and save ARCA23K-FSD annotations
    subset_dir = args.work_dir / 'subset'
    df_train = pd.read_csv(subset_dir / 'train.csv', index_col=0)
    df_val = pd.read_csv(subset_dir / 'val.csv', index_col=0)
    df_test = pd.read_csv(subset_dir / 'test.csv', index_col=0)
    df_train = df_train[df_train.label.isin(label_set)]
    df_val = df_val[df_val.label.isin(label_set)]
    df_test = df_test[df_test.label.isin(label_set)]
    fsd_dir = args.work_dir / 'final/ARCA23K-FSD.ground_truth'
    fsd_dir.mkdir(parents=True, exist_ok=True)
    df_train.to_csv(fsd_dir / 'train.csv')
    df_val.to_csv(fsd_dir / 'val.csv')
    df_test.to_csv(fsd_dir / 'test.csv')

    # Create DataFrame for ARCA23K annotations
    df = pd.read_csv(args.work_dir / 'download_list.csv', index_col=0)
    mids = pd.read_csv('metadata/fsd50k_mids.csv', index_col=0)
    df['mid'] = mids.loc[df.prediction].values
    df.columns = ['label', 'mid']
    df.index.name = 'fname'

    # Discard DataFrame entries that correspond to non-existing clips
    for clip_id in tqdm(df.index):
        path = args.work_dir / f'audio/{clip_id}.wav'
        n_bytes = path.stat().st_size
        if not path.exists() or n_bytes < 26460 or n_bytes > 2646500:
            df.drop([clip_id], inplace=True)

    # Constrain ARCA23K to be the same size as ARCA23K-FSD
    df_train = select_subset(df, df_train)

    # Save ARCA23K annotations
    arca23k_dir = args.work_dir / 'final/ARCA23K.ground_truth'
    df_train.to_csv(arca23k_dir / 'train.csv')
    df_val.to_csv(arca23k_dir / 'val.csv')
    df_test.to_csv(arca23k_dir / 'test.csv')


def select_subset(df, df_train):
    # Determine number of clips to download per class
    target_sizes = df_train.groupby(df_train.label).size()

    def _sample(x):
        n_samples = target_sizes[x.label][0]
        return x.sample(n_samples)

    return df.groupby(df.label).apply(_sample).droplevel(0)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', type=Path, default=Path('_output'),
                        help='path to workspace directory')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(curate(parse_args()))
