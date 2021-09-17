import argparse
import json
import sys
import time
from pathlib import Path

from extern.freesound import FreesoundClient, FreesoundException


def download(args):
    with open('client.json') as f:
        params = json.load(f)

    client = FreesoundClient()
    client.set_token(params['client_secret'])

    # Ensure output directory exists
    output_dir = args.work_dir / 'query'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine the first page to start downloading
    # Redownload the last downloaded page in case it has been updated
    initial_page = sum(1 for _ in output_dir.glob('page*.json')) or 1

    page = initial_page
    while True:
        response = text_search(client, page)
        output_path = output_dir / f'page{page:04d}.json'
        with open(output_path, 'w') as f:
            json.dump(response.json_dict, f, indent=2)

        print(f'Page {page} retrieved with {len(response.results)} results')

        if response.next is None:
            break

        page += 1

    if page > initial_page:
        print(f'Retrieved pages {initial_page}-{page}')


def text_search(client, page, query=''):
    fields = 'id,name,tags,description,type,channels,channels,' \
             'bitdepth,duration,samplerate,license,username'

    try:
        return client.text_search(
            query=query,
            fields=fields,
            filter='duration:[* TO 30]',
            sort='created_asc',
            page=str(page),
            page_size=150,
        )
    except FreesoundException as e:
        if e.code == 500:
            # Search server could not be reached
            # Wait 10 seconds before trying again
            time.sleep(10)

            return text_search(client, page, query)

        raise e


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', type=Path, default=Path('_output'),
                        help='path to workspace directory')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(download(parse_args()))
