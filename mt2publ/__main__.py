""" mt2publ - a tool to convert a MT site to a Publ site """

import argparse
import logging

import urllib.parse
from pony import orm

from . import model, __version__
from . import entry


LOG_LEVELS = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

LOGGER = logging.getLogger("mt2publ.main")


def parse_args(*args):
    parser = argparse.ArgumentParser(
        description="Convert an MT database to a Publ content store")

    parser.add_argument('--version', action='version',
                        version="%(prog)s " + __version__.__version__)

    parser.add_argument("-v", "--verbosity", action="count",
                        help="increase output verbosity",
                        default=0)

    parser.add_argument('--content', '-c', type=str, dest='content_dir',
                        help='Output content directory')
    parser.add_argument('--templates', '-t', type=str, dest='template_dir',
                        help='Output template directory')
    parser.add_argument('--force', '-f', action='store_true', dest='force_overwrite',
                        help='Force overwriting of existing files')

    parser.add_argument('db', type=str, help='SQLite database file')

    return parser.parse_args(*args)


def main():
    """ main entry point """
    config = parse_args()

    logging.basicConfig(level=LOG_LEVELS[min(
        config.verbosity, len(LOG_LEVELS) - 1)])

    # TODO support mysql, postgres, etc.
    model.connect(provider='sqlite', filename=config.db)

    with orm.db_session():
        for e in model.Entry.select():
            entry.process(e, config)
