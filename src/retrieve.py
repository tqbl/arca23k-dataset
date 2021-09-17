import argparse
import sys
from pathlib import Path


def main(args):
    import nltk
    import pandas as pd
    from nltk.stem import WordNetLemmatizer

    from extern.core.dataset import DataSubset
    from extern.fsd import AudioSetOntology, Arca23K_FSD

    import retrieval
    import utils
    from retrieval import ShortestLemmatizer

    # Load metadata for FSD50K subset
    dataset_dir = args.work_dir / 'fsd50k'
    dataset = Arca23K_FSD('', dataset_dir, args.work_dir / 'subset')
    subset = DataSubset.concat([dataset['training'],
                                dataset['validation'],
                                dataset['test']])

    # Download NLTK resources
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

    # Build vocabulary of relevant terms based on label set
    lemmatizer = ShortestLemmatizer(WordNetLemmatizer())
    ontology = AudioSetOntology('metadata/ontology.json')
    vocab = retrieval.Vocabulary(dataset.label_set, ontology, lemmatizer)

    # Load Freesound metadata
    entries = utils.load_freesound_metadata(args.work_dir / 'query')
    index = pd.Index([int(index[:-4]) for index in subset.tags.index])
    mask = entries.index.isin(index)
    if args.evaluate:
        # Filter out entries that do not belong to FSD50K subset
        entries = entries[mask]
    else:
        # Filter out entries belonging to FSD50K
        dev_path = dataset_dir / 'FSD50K.ground_truth/dev.csv'
        index = pd.read_csv(dev_path, index_col=0).index
        mask = ~(mask | entries.index.isin(index))
        entries = entries[mask]

    # Run retrieval algorithm
    results = retrieval.retrieve(entries, vocab, lemmatizer)

    if args.evaluate:
        pd.options.display.max_rows = 100
        print(evaluate(results, subset))
    else:
        # Discard classes that lack a sufficient number of matches
        sizes = results.groupby('prediction').size()
        sizes2 = dataset['training'].tags.groupby('label').size()
        ratios = sizes / (sizes2 + 3)  # margin=3 for headroom
        labels = ratios.index[ratios >= 1]
        results = results[results.prediction.isin(labels)]

        # Write matches to CSV file
        results.to_csv(args.work_dir / 'freesound_matches.csv')
        with open(args.work_dir / 'labels.txt', 'w') as f:
            f.write('\n'.join(sorted(labels)))


def evaluate(results, subset):
    import pandas as pd

    # Combine ground truth and predictions into a single DataFrame
    results.index = results.index.astype(str) + '.wav'
    results = subset.tags.join(results)
    results = results[pd.notna(results.prediction)]

    accuracy = (results.label == results.prediction).mean()
    class_accuracy = results.groupby('label').apply(
        lambda x: (x.label == x.prediction).mean())
    df = pd.DataFrame(class_accuracy, columns=['Accuracy'])
    df.loc['Macro Average'] = class_accuracy.mean()
    df.loc['Micro Average'] = accuracy

    return df


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', type=Path, default=Path('_output'),
                        help='path to workspace directory')
    parser.add_argument('--evaluate', type=bool,
                        help='whether to run in evaluation mode')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main(parse_args()))
