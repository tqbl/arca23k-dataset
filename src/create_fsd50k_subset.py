import argparse
import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


def main(args):
    from jaffadata.datasets import AudioSetOntology, FSD50K

    dataset_dir = args.work_dir / 'fsd50k'
    if not dataset_dir.is_dir():
        download_fsd50k_data(dataset_dir)
    dataset = FSD50K(dataset_dir)
    ontology = AudioSetOntology('metadata/ontology.json')

    # Filter out audio clips that contain multiple sounds
    train_set = to_single_label(dataset['training'], ontology)
    val_set = to_single_label(dataset['validation'], ontology)
    test_set = to_single_label(dataset['test'], ontology)

    # Filter out classes that have less than n instances
    # mids correspond to the AudioSet classes
    train_mids = filter_classes_by_size(train_set, n=50)
    val_mids = filter_classes_by_size(val_set, n=10)
    test_mids = filter_classes_by_size(test_set, n=20)
    mids = set(train_mids) & set(val_mids) & set(test_mids)

    # Filter out ancestor classes
    mids = filter_classes_by_ancestry(mids, ontology)

    # Create new subsets based on the new class set
    train_set = filter_subset_by_class(train_set, mids)
    val_set = filter_subset_by_class(val_set, mids)
    test_set = filter_subset_by_class(test_set, mids)

    # Save annotations to disk
    output_dir = args.work_dir / 'subset'
    output_dir.mkdir(parents=True, exist_ok=True)
    save_annotations(train_set, output_dir / 'train.csv')
    save_annotations(val_set, output_dir / 'val.csv')
    save_annotations(test_set, output_dir / 'test.csv')


def download_fsd50k_data(dataset_dir):
    import requests

    # Download ground truth zip file
    url = 'https://zenodo.org/record/4060432/files/FSD50K.ground_truth.zip'
    response = requests.get(url)
    if not response.ok:
        raise RuntimeError(f'Unable to download from Zenodo: '
                           f'{response.status_code} {response.reason}')

    # Unzip contents
    dataset_dir.mkdir(parents=True)
    (dataset_dir / 'FSD50K.dev_audio').mkdir()
    (dataset_dir / 'FSD50K.eval_audio').mkdir()
    zfile = ZipFile(BytesIO(response.content), 'r')
    zfile.extractall(dataset_dir)
    zfile.close()


def to_single_label(subset, ontology):
    import numpy as np

    # Check if any labels are unrelated to the first label, which
    # would mean that the clip contains more than one type of sound.
    # It is assumed the first label encountered is a leaf node.
    def _are_unrelated(mids):
        return any(not ontology[mid].is_ancestor(ontology[mids[0]])
                   for mid in mids[1:])

    mask = np.fromiter(map(_are_unrelated, subset.tags.mids), dtype=bool)

    subset = subset[~mask]
    subset.tags.insert(0, 'label', subset.tags.labels.str[0])
    subset.tags.insert(1, 'mid', subset.tags.mids.str[0])
    del subset.tags['labels']
    del subset.tags['mids']
    return subset


def filter_classes_by_size(subset, n):
    mids = subset.tags.mid
    sizes = mids.groupby(mids, sort=False).size()
    return mids.unique()[sizes >= n]


def filter_classes_by_ancestry(mids, ontology):
    def _item(mid):
        return ontology[mid]

    new_mids = []
    for mid in mids:
        # Determine whether the class is an ancestor of any other class
        is_ancestor = any(_item(mid).is_ancestor(_item(other_mid))
                          for other_mid in mids)
        # Include the class if it is not an ancestor
        if not is_ancestor:
            new_mids.append(mid)

    return new_mids


def filter_subset_by_class(subset, mids):
    return subset[subset.tags.mid.isin(mids)]


def save_annotations(subset, output_path):
    import pandas as pd

    tags = subset.tags
    names = [fname[:-4] for fname in tags.index]
    tags.index = pd.Index(names, name=tags.index.name)
    tags = tags[['label', 'mid']]
    tags.to_csv(output_path)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', type=Path, default=Path('_output'),
                        help='path to workspace directory')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main(parse_args()))
