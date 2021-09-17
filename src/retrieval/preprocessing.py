import nltk
from nltk.corpus import stopwords, wordnet


STOP_WORDS = stopwords.words('english')


class ShortestLemmatizer:
    def __init__(self, lemmatizer):
        self.lemmatizer = lemmatizer

    def lemmatize(self, token):
        words = [self.lemmatizer.lemmatize(token, pos)
                 for pos in [wordnet.ADJ, wordnet.NOUN,
                             wordnet.VERB, wordnet.ADV]]
        return min(words, key=len)


def tokenize(text):
    return nltk.tokenize.word_tokenize(text.replace('/', ' '))


def preprocess(tokens, lemmatizer=None):
    # Filter out tokens that are not words e.g. punctuation
    tokens = filter(is_word, tokens)

    # Convert tokens to lowercase while preserving abbreviations
    # e.g. 'kHz' would not be converted to lowercase
    tokens = map(smart_lowercase, tokens)

    # Normalize tokens using lemmatization if enabled
    if lemmatizer is not None:
        tokens = map(lemmatizer.lemmatize, tokens)

    # Remove stop words such as 'and', 'is', etc.
    tokens = [token for token in tokens if token not in STOP_WORDS]

    # Remove words that are duplicates
    tokens = list(dict.fromkeys(tokens))

    return tokens


def smart_lowercase(word):
    word_lower = word.lower()
    return word_lower if word_lower[1:] == word[1:] else word


def is_word(text):
    return str.isalpha(text.replace('-', ''))
