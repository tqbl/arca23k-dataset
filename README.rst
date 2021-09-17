ARCA23K
=======

This is the software used to create the ARCA23K and ARCA23K-FSD
datasets. A description of these datasets can be found on the `Zenodo
page`__. Details of how the datasets were created can be found in our
DCASE2021 workshop paper (to appear soon).

Due to the mutable nature of the Freesound database (the source of the
audio data), this software is unlikely to reproduce ARCA23K and
ARCA23K-FSD exactly. However, in releasing this code, we hope that it
can be used as a reference.

The baseline system used to run experiments will be released soon.

__ https://zenodo.org/record/5117901


.. contents::


Requirements
------------

This software requires Python >=3.8. To install the dependencies, run::

    poetry install

or::

    pip install -r requirements.txt

You are also free to use another package manager (e.g. Conda).

`FFmpeg`__ is required too for converting the audio files.

__ https://www.ffmpeg.org


Configuration
-------------

Some of the scripts require access to the Freesound API. To use the API,
you need access credentials, which you can `apply`__ for. Once you have
a client ID and a client secret key, you need to add these credentials
to the `client.json`__ file. An access token is also needed to download
clips from Freesound. To obtain an access token, follow the instructions
given `here`__. Note that an access token is only valid for 24 hours.

__ https://freesound.org/apiv2/apply
__ client.json
__ https://freesound.org/docs/api/authentication.html#oauth-authentication


Usage
-----

Each Python script has the following usage::

    python SCRIPT [--work_dir DIR] [other-options...]

The ``--work_dir`` option is used to specify the directory in which the
output files are to be written. By default, it is set to ``_output/``.
As some scripts depend on the output files of other scripts, please
ensure that this option is set to the same value across scripts.

For details of the other arguments and options, use ``--help``.

This software provides six scripts:

1. ``src/create_fsd50k_subset.py``: Creates a tentative version of
   ARCA23K-FSD. It selects a single-label subset of FSD50K and saves the
   ground truth data of the subset.
2. ``src/query_freesound.py``: Uses the Freesound API to search the
   database for all clips that are up to 30 seconds in duration. The
   search results, which include various metadata, are saved to disk.
3. ``src/retrieve.py``: Based on the search results of the previous
   script, the results are narrowed down to clips that can be assigned a
   label, which is determined using an automated procedure.
4. ``src/download_clips.py``: Uses the Freesound API to download clips
   from Freesound. The clips that are downloaded depend on the results
   of the previous script.
5. ``src/convert_audio.py``: Converts the downloaded Freesound clips to
   16-bit mono WAV files sampled at 44.1 kHz.
6. ``src/curate_datasets.py``: Creates the final ground truth data for
   ARCA23K and ARCA23K-FSD.

Ensure that the scripts are run in the given order.


Attribution
-----------

`src/extern/freesound.py`__ is from `MTG/freesound-datasets`__.

`metadata/ontology.json`__ is from `audioset/ontology`__.

__ src/extern/freesound.py
__ https://github.com/MTG/freesound-datasets
__ metadata/ontology.json
__ https://github.com/audioset/ontology
