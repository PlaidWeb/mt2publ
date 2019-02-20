""" common functionality """

import logging
import os
import os.path
import tempfile
import shutil

LOGGER = logging.getLogger('mt2publ')


def save_file(message, path, force_overwrite):
    """ save the message data to the specified file as an atomic operation """

    try:
        os.makedirs(os.path.dirname(path))
    except FileExistsError:
        pass

    if os.path.isfile(path) and not force_overwrite:
        LOGGER.warning("Refusing to overwrite existing file %s", dest)
        return

    with tempfile.NamedTemporaryFile('w', delete=False) as file:
        tmpfile = file.name
        file.write(str(message))

    shutil.move(tmpfile, path)
