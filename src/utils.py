import json

import pandas as pd
from tqdm import tqdm


def load_freesound_metadata(metadata_dir):
    def _has_tags(entry):
        return len(entry['tags']) > 0

    entries = []
    for path in tqdm(sorted(metadata_dir.iterdir())):
        with open(path, 'r') as f:
            json_dict = json.load(f)

        entries += list(filter(_has_tags, json_dict['results']))

    # Wrap the entries in a DataFrame object
    entries = pd.DataFrame(entries).set_index('id')
    # Filter out entries that have a duration outside [0.3, 30]
    entries = entries[(entries.duration >= 0.3) & (entries.duration <= 30)]

    return entries
