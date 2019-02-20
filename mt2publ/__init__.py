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
        # we can't just use file.write(str(entry)) because otherwise the
        # headers "helpfully" do MIME encoding normalization.
        # str(val) is necessary to get around email.header's encoding
        # shenanigans
        for key, val in entry.items():
            print('{}: {}'.format(key, str(val)), file=file)
        print('', file=file)
        file.write(entry.get_payload())

    shutil.move(tmpfile, path)
