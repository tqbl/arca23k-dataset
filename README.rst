ARCA23K
=======

This is the software used to create the ARCA23K and ARCA23K-FSD
datasets. A description of these datasets, along with download links, can be
found on the `Zenodo page`__. Details of how the datasets were created can be
found in our `DCASE2021 paper`__ [1]_.

Due to the mutable nature of the Freesound database (the source of the
audio data), this software is unlikely to reproduce ARCA23K and
ARCA23K-FSD exactly. Nevertheless, we hope this code can serve as a
useful reference.

The source code for the baseline system can be found `here`__.

__ https://zenodo.org/record/5117901
__ https://arxiv.org/abs/2109.09227
__ https://github.com/tqbl/arca23k-baseline


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
access credentials are required, which can be applied for `here`__. Once
a client ID and a client secret key are obtained, they need to be added
to the `client.json`__ file. An access token is also needed to download
clips from Freesound. To obtain an access token, follow the instructions
given `here`__. Note that an access token is only valid for 24 hours. To
use the API without request limitations, you may need to contact the
Freesound developers.

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
   mono 16-bit 44.1 kHz WAV files.
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


Citing
------

If you wish to cite this work, please cite the following paper:

.. [1] \T. Iqbal, Y. Cao, A. Bailey, M. D. Plumbley, and W. Wang,
       “ARCA23K: An audio dataset for investigating open-set label
       noise”, in Proceedings of the Detection and Classification of
       Acoustic Scenes and Events 2021 Workshop (DCASE2021), 2021,
       Barcelona, Spain, pp. 201–205.

BibTeX::

    @inproceedings{Iqbal2021,
        author = {Iqbal, T. and Cao, Y. and Bailey, A. and Plumbley, M. D. and Wang, W.},
        title = {{ARCA23K}: An audio dataset for investigating open-set label noise},
        booktitle = {Proceedings of the Detection and Classification of Acoustic Scenes and Events 2021 Workshop (DCASE2021)},
        pages = {201--205},
        year = {2021},
        address = {Barcelona, Spain},
    }
