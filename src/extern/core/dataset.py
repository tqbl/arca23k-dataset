import functools
from pathlib import Path

import pandas as pd

from .mask import FrameMask


class Dataset:
    def __init__(self,
                 name,
                 root_dir,
                 sample_rate=None,
                 n_channels=1,
                 bit_depth=16,
                 clip_duration=None,
                 label_set=None,
                 ):
        self.root_dir = Path(root_dir)
        if not self.root_dir.is_dir():
            raise FileNotFoundError(f'No such directory: {root_dir}')

        self.name = name
        self.sample_rate = sample_rate
        self.n_channels = n_channels
        self.bit_depth = bit_depth
        self.clip_duration = clip_duration
        self.label_set = label_set
        self.subsets = dict()

    @staticmethod
    def target(subset, index=None):
        return None

    def add_subset(self, subset):
        self.subsets[subset.name] = subset

    def __getitem__(self, key):
        return self.subsets[key]

    def __setitem__(self, key, value):
        self.subsets[key] = value

    def __delitem__(self, key):
        del self.subsets[key]

    def __iter__(self):
        return iter(self.subsets)

    def __len__(self):
        return len(self.subsets)

    def __str__(self):
        return self.name


class DataSubset:
    def __init__(self, name, dataset, tags=None, audio_dir=None):
        if audio_dir is None:
            audio_dir = dataset.root_dir
        else:
            audio_dir = Path(audio_dir)
            if not audio_dir.is_dir():
                raise FileNotFoundError(f'No such directory: {audio_dir}')

        self.name = name
        self.dataset = dataset

        def _copy_tags(tags):
            if not isinstance(tags, pd.DataFrame):
                raise ValueError('`tags` must be a pandas DataFrame')
            return tags.copy()

        # Set the tags for this DataSubset instance
        # One or more private tags are stored in self._tags
        if tags is None:
            # Create an empty DataFrame if no tags are given
            index = pd.Index([path.name for path in audio_dir.iterdir()
                              if path.suffix == '.wav'])
            self.tags = pd.DataFrame(index=index)
            self._tags = pd.DataFrame(index=self.tags.index)
        elif isinstance(tags, tuple) and len(tags) == 2:
            self.tags = _copy_tags(tags[0])
            self._tags = _copy_tags(tags[1])
        else:
            self.tags = _copy_tags(tags)
            self._tags = pd.DataFrame(index=self.tags.index)

        if 'audio_dir' not in self._tags:
            # Record the audio directory as a private tag
            self._tags['audio_dir'] = audio_dir

    @staticmethod
    def concat(subsets, name=None):
        tags = pd.concat([subset.tags for subset in subsets])
        private_tags = pd.concat([subset._tags for subset in subsets])
        subset = DataSubset(name or subsets[0].name,
                            subsets[0].dataset,
                            (tags, private_tags))
        return subset

    @functools.cached_property
    def audio_paths(self):
        audio_dirs = self._tags.audio_dir.groupby(
            level=0, sort=False).first()
        fnames = self.tags.index.unique(level=0)
        return audio_dirs / fnames

    def subset(self, name, mask, complement=False):
        if callable(mask):
            mask = mask(self.tags)
        elif isinstance(mask, str):
            mask = FrameMask(mask).value(self.tags)
        elif isinstance(mask, FrameMask):
            mask = mask.value(self.tags)

        if complement:
            mask = ~mask

        return self._subset(name, lambda tags: tags[mask])

    def subset_loc(self, name, index):
        return self._subset(name, lambda tags: tags.loc[index])

    def subset_iloc(self, name, indexer):
        return self._subset(name, lambda tags: tags.iloc[indexer])

    def sample(self, name, n=None, frac=None):
        return self.subset_loc(name, self.tags.sample(n, frac).index)

    def _subset(self, name, callback):
        tags = (callback(self.tags), callback(self._tags))
        return DataSubset(name, self.dataset, tags)

    def __getitem__(self, key):
        return self.subset(self.name, key)

    def __len__(self):
        return len(self.tags)

    def __str__(self):
        return f'{self.dataset} {self.name}'
