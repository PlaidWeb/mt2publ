""" Functions for converting MT categories to Publ categories """

import logging
import email.message
import os.path

from . import save_file

LOGGER = logging.getLogger("mt2publ.category")


def process(category, config):
    """ Process a category to produce a metadata file """
    write = False

    message = email.message.Message()

    # Only write out the name if it differs from the Publ default
    if category.name and category.basename.title() != category.name:
        write = True
        message['Name'] = category.name

    # Add the description
    if category.description:
        write = True
        message.set_payload(category.description)

    if not write:
        LOGGER.info("Category '%s' has no vital metadata",
                    category.path or '(root)')
        return

    output_filename = os.path.join(*category.path.split('/'), f'_{category.basename}.cat')

    save_file(message, config.content_dir, output_filename, config)
