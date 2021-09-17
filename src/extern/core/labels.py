import numpy as np
import pandas as pd


def binarize(subset, tag_name, index=None, is_label=True):
    if index is None:
        fnames = subset.tags.index
        y = pd.concat([binarize(subset, tag_name, fname)
                       for fname in fnames],
                      axis=1, keys=fnames).T
        return y

    label_set = subset.dataset.label_set
    y = pd.Series(np.zeros(len(label_set)), index=label_set, name=index)
    label = subset.tags[tag_name].loc[index]
    if isinstance(label, list):
        labels = label
        for label in labels:
            y[label_set.index(label)] = 1
    elif is_label:
        y[label_set.index(label)] = 1
    else:
        y[label] = 1
    return y
