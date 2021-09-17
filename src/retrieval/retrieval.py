import numpy as np
import pandas as pd
from tqdm import tqdm

from . import preprocessing


class Vocabulary:
    def __init__(self, label_set, ontology, lemmatizer):
        vocabulary = []
        label_terms = {}
        orig_labels = {}
        for label in label_set:
            label, orig_label = to_audioset_label(label), label

            # Extract search terms from label
            # e.g. 'Electric_guitar' -> ['Electric', 'guitar']
            terms = extract_label_terms(label, lemmatizer)

            vocabulary += terms
            label_terms[label] = terms
            orig_labels[label] = orig_label

            # Extract terms from child labels
            ids = ontology[label].child_ids
            for child_id in ids:
                child_label = ontology[child_id].name
                terms = extract_label_terms(child_label, lemmatizer)
                vocabulary += terms
                label_terms[child_label] = terms
                orig_labels[child_label] = orig_label

        self.vocabulary = sorted(set(vocabulary))
        self.label_vecs = self.vectorize(label_terms)
        self.orig_labels = list(orig_labels.values())

    def vectorize(self, terms):
        if isinstance(terms, dict):
            label_vecs = {label: self.vectorize(term_list)
                          for label, term_list in terms.items()}
            return np.stack(list(label_vecs.values()))

        return np.isin(self.vocabulary, terms).astype(float)

    def match(self, vec):
        sim = cosine_similarity(vec, self.label_vecs)
        index = np.argmax(sim)
        label = self.orig_labels[index]
        return sim, index, label

    def __len__(self):
        return len(self.vocabulary)


def retrieve(entries, vocab, lemmatizer, threshold=0.5):
    results = {}
    for clip_id, entry in tqdm(entries.iterrows(), total=len(entries)):
        # Preprocess tags to simplify retrieval
        tags = preprocessing.preprocess(entry.tags, lemmatizer)

        # Tokenize and preprocess clip description
        desc_tokens = preprocessing.tokenize(entry.description)
        desc_terms = preprocessing.preprocess(desc_tokens, lemmatizer)

        # Vectorize query and description
        vec = np.zeros(len(vocab))
        if len(tags) > 0:
            vec += vocab.vectorize(tags)
        if len(desc_terms) > 0:
            vec += vocab.vectorize(desc_terms)

        sim, index, label = vocab.match(vec)
        if sim[index] > threshold:
            results[clip_id] = (label, sim[index])

    # Create a DataFrame object for the results
    columns = ['prediction', 'score']
    results = pd.DataFrame.from_dict(results, orient='index', columns=columns)

    return results


def extract_label_terms(label, lemmatizer):
    tokens = preprocessing.tokenize(label)
    return preprocessing.preprocess(tokens, lemmatizer)


def cosine_similarity(vec, other_vecs):
    norm = np.linalg.norm(vec) * np.linalg.norm(other_vecs, axis=1)
    return np.inner(vec, other_vecs) / (norm + 1e-8)


def to_audioset_label(label):
    label = label.replace('_', ' ')
    if label == 'Dishes and pots and pans':
        return 'Dishes, pots, and pans'
    return label.replace(' and', ',')
