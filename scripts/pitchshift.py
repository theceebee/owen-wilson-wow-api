#!/usr/bin/python3

# Standard Python libs.
import argparse
import logging
import os
import sys
from tempfile import NamedTemporaryFile
from typing import Any, AnyStr

# Third-party dependencies.
import librosa
import requests
import sounddevice

# `librosa` has an OTT warning about what module it's using to load the file.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter('ignore')

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


def pitch_shift_audio(path: Any, steps: float=.0) -> None:
    """
    Plays a pitch-shifted audio file.

    :param path:    The path of the file to play.
    :param steps:   The number of steps (up or down) to shift the pitch
                    (default=0 i.e. unchanged).
    :return:
    """

    logger.info('Retriculating splines...')

    data, sr = librosa.load(path)
    pitch_shifted = librosa.effects.pitch_shift(data, sr=sr, n_steps=steps)

    logger.info('Playing pitch-shifted audio...')
    sounddevice.play(pitch_shifted, sr)
    sounddevice.wait()


def pitch_shift_audio_url(url: AnyStr, steps: float=.0) -> None:
    """
    Plays a pitch-shifted audio file, downloaded from a URL.

    :param url:     The URL of the file to play.
    :param steps:   The number of steps (up or down) to shift the pitch
                    (default=0 i.e. unchanged).

    """

    logger.info('Downloading URL...')

    response = requests.get(url, stream=True)
    assert response.status_code == 200, 'Invalid URL!'

    with NamedTemporaryFile(mode='w+b',
                            suffix=os.path.splitext(url)[-1],
                            delete=False) as fp:

        fp.write(response.content)

    logger.info('Download Complete!')

    pitch_shift_audio(fp.name, steps)

    # Attempt to clean up the temp file
    try:
        logger.info('Cleaning up downloaded file...')
        os.remove(fp.name)
        logger.info('Clean-up complete!')
    except OSError:
        logger.warning(f'Failed to remove downloaded file: [{fp.name}]',
                       exc_info=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('steps', type=float)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file')
    group.add_argument('-u', '--url')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    try:
        pitch_shift_audio(args.file, args.steps) \
            if args.file \
            else pitch_shift_audio_url(args.url, args.steps)

    except Exception:
        logger.error('Something went wrong!', exc_info=True)
        sys.exit(1)

    sys.exit(0)
