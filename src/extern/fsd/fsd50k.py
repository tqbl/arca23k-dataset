from pathlib import Path

import pandas as pd

import extern.core.labels as labels
from extern.core.dataset import Dataset, DataSubset


class FSD50K(Dataset):
    def __init__(self, root_dir, gt_dir=None):
        super().__init__('FSD50K',
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=None,
                         )

        if gt_dir is not None:
            gt_dir = Path(gt_dir)
        else:
            gt_dir = self.root_dir / 'FSD50K.ground_truth'

        # Determine label set
        vocab_path = self.root_dir / 'FSD50K.ground_truth' / 'vocabulary.csv'
        vocab = pd.read_csv(vocab_path, index_col=0, header=None)
        self.label_set = sorted(vocab[1])

        # Create DataSubset for dev set
        tags_dev = read_tags(gt_dir / 'dev.csv')
        subset_dev = DataSubset('dev', self, tags_dev,
                                self.root_dir / 'FSD50K.dev_audio')
        # Split into training and validation sets
        self.add_subset(subset_dev.subset('train', tags_dev.split == 'train'))
        self.add_subset(subset_dev.subset('val', tags_dev.split == 'val'))

        # Create DataSubset for eval set
        tags_eval = read_tags(gt_dir / 'eval.csv')
        self.add_subset(DataSubset('eval', self, tags_eval,
                                   self.root_dir / 'FSD50K.eval_audio'))

        # Create aliases
        self['training'] = self['train']
        self['validation'] = self['val']
        self['test'] = self['eval']

    @staticmethod
    def target(subset, index=None):
        return labels.binarize(subset, 'labels', index)


def read_tags(path):
    df = pd.read_csv(path, index_col=0)
    # Add missing file extension to file names
    fnames = [f'{name}.wav' for name in df.index]
    df.index = pd.Index(fnames, name=df.index.name)
    df['labels'] = df['labels'].str.split(',')
    df['mids'] = df['mids'].str.split(',')
    return df
