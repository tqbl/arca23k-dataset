from pathlib import Path

import pandas as pd

import extern.core.labels as labels
from extern.core.dataset import Dataset, DataSubset


class Arca23K_(Dataset):
    def __init__(self, name, root_dir, data_dirs,
                 train_gt_dir, test_gt_dir=None):
        super().__init__(name,
                         root_dir,
                         sample_rate=44100,
                         n_channels=1,
                         bit_depth=16,
                         clip_duration=None,
                         )

        if test_gt_dir is None:
            test_gt_dir = train_gt_dir
        train_gt_dir = Path(train_gt_dir)
        test_gt_dir = Path(test_gt_dir)

        tags_train = read_tags(train_gt_dir / 'train.csv')
        tags_val = read_tags(test_gt_dir / 'val.csv')
        tags_test = read_tags(test_gt_dir / 'test.csv')

        self.add_subset(DataSubset('training', self, tags_train,
                                   data_dirs['training']))
        self.add_subset(DataSubset('validation', self, tags_val,
                                   data_dirs['validation']))
        self.add_subset(DataSubset('test', self, tags_test,
                                   data_dirs['test']))

        self.label_set = sorted(tags_train.label.unique())

    @staticmethod
    def target(subset, index=None):
        return labels.binarize(subset, 'label', index)


class Arca23K(Arca23K_):
    def __init__(self, root_dir, fsd50k_dir, gt_dir=None):
        super().__init__('ARCA23K',
                         Path(root_dir),
                         {'training': Path(root_dir) / 'ARCA23K.audio',
                          'validation': Path(fsd50k_dir) / 'FSD50K.dev_audio',
                          'test': Path(fsd50k_dir) / 'FSD50K.eval_audio',
                          },
                         gt_dir or Path(root_dir) / 'ARCA23K.ground_truth',
                         gt_dir or Path(root_dir) / 'ARCA23K-FSD.ground_truth',
                         )


class Arca23K_FSD(Arca23K_):
    def __init__(self, root_dir, fsd50k_dir, gt_dir=None):
        super().__init__('ARCA23K-FSD',
                         Path(root_dir),
                         {'training': Path(fsd50k_dir) / 'FSD50K.dev_audio',
                          'validation': Path(fsd50k_dir) / 'FSD50K.dev_audio',
                          'test': Path(fsd50k_dir) / 'FSD50K.eval_audio',
                          },
                         gt_dir or Path(root_dir) / 'ARCA23K-FSD.ground_truth',
                         )


def read_tags(path):
    df = pd.read_csv(path, index_col=0, dtype={'label': 'category'})
    # Add missing file extension to file names
    fnames = [f'{name}.wav' for name in df.index]
    df.index = pd.Index(fnames, name=df.index.name)
    return df
