""" common functionality """

import logging
import os
import os.path
import tempfile
import shutil

LOGGER = logging.getLogger('mt2publ')


def save_file(message, dest, filename, config):
    """ save the message data to the specified file as an atomic operation """
    LOGGER.info("Output filename: %s", filename)
    if not dest:
        LOGGER.debug("No destination set")
        return

    path = os.path.join(dest, filename)

    try:
        os.makedirs(os.path.dirname(path))
    except FileExistsError:
        pass

    if os.path.isfile(path) and not config.force_overwrite:
        LOGGER.warning("Refusing to overwrite existing file %s", path)
        return

    with tempfile.NamedTemporaryFile('w', delete=False) as file:
        tmpfile = file.name
        # we can't just use file.write(str(entry)) because otherwise the
        # headers "helpfully" do MIME encoding normalization.
        # str(val) is necessary to get around email.header's encoding
        # shenanigans
        for key, val in message.items():
            print('{}: {}'.format(key, str(val)), file=file)
        print('', file=file)
        if message.get_payload():
            file.write(message.get_payload())

    shutil.move(tmpfile, path)
