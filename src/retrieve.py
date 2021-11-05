import argparse
import sys
from pathlib import Path


def main(args):
    import nltk
    import pandas as pd
    from jaffadata.datasets import AudioSetOntology
    from nltk.stem import WordNetLemmatizer

    import retrieval
    import utils
    from retrieval import ShortestLemmatizer

    # Load metadata for FSD50K subset
    dataset_dir = args.work_dir / 'fsd50k'
    subset = read_metadata(args.work_dir / 'subset')

    # Download NLTK resources
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

    # Build vocabulary of relevant terms based on label set
    lemmatizer = ShortestLemmatizer(WordNetLemmatizer())
    ontology = AudioSetOntology('metadata/ontology.json')
    label_set = sorted(subset.label.unique())
    vocab = retrieval.Vocabulary(label_set, ontology, lemmatizer)

    # Load Freesound metadata
    entries = utils.load_freesound_metadata(args.work_dir / 'query')
    mask = entries.index.isin(subset.index)
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
        scores = evaluate(results, subset)
        scores.to_csv(args.work_dir / 'retrieval_scores.csv')
        print(scores)
    else:
        # Discard classes that lack a sufficient number of matches
        sizes = results.groupby('prediction').size()
        sizes2 = subset[subset.train].groupby('label').size()
        ratios = sizes / (sizes2 + 3)  # margin=3 for headroom
        labels = ratios.index[ratios >= 1]
        results = results[results.prediction.isin(labels)]

        # Write matches to CSV file
        results.to_csv(args.work_dir / 'freesound_matches.csv')
        with open(args.work_dir / 'labels.txt', 'w') as f:
            f.write('\n'.join(sorted(labels)))


def read_metadata(metadata_dir):
    import pandas as pd

    df_train = pd.read_csv(metadata_dir / 'train.csv', index_col=0)
    df_val = pd.read_csv(metadata_dir / 'val.csv', index_col=0)
    df_test = pd.read_csv(metadata_dir / 'test.csv', index_col=0)
    df = pd.concat([df_train, df_val, df_test])
    df['train'] = df.index.isin(df_train.index)
    return df


def evaluate(results, subset):
    import pandas as pd

    # Combine ground truth and predictions into a single DataFrame
    results = subset.join(results)
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
