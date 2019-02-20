""" mt2publ - a tool to convert a MT site to a Publ site """

import argparse
import logging

from pony import orm

from . import model, __version__
from . import category, entry


LOG_LEVELS = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

LOGGER = logging.getLogger("mt2publ.main")


def parse_args(*args):
    """ parse arguments """
    parser = argparse.ArgumentParser(
        description="Convert an MT database to a Publ content store")

    parser.add_argument('--version', action='version',
                        version="%(prog)s " + __version__.__version__)

    parser.add_argument("-v", "--verbosity", action="count",
                        help="increase output verbosity",
                        default=0)

    parser.add_argument("--blog-id", "-b", type=int, dest="blog_id",
                        help="Restrict entries to a specific blog", default=None)

    parser.add_argument('--content', '-c', type=str, dest='content_dir',
                        help='Output content directory', default=None)
    parser.add_argument('--force', '-f', action='store_true', dest='force_overwrite',
                        help='Force overwriting of existing files')

    parser.add_argument('db', type=str, help='SQLite database file')

    return parser.parse_args(*args)


def main(**args):
    """ main entry point """
    config = parse_args(**args)

    logging.basicConfig(level=LOG_LEVELS[min(
        config.verbosity, len(LOG_LEVELS) - 1)])

    model.connect(provider='sqlite', filename=config.db)

    with orm.db_session():
        if config.blog_id:
            blog = model.Blog.get(blog_id=config.blog_id)
        else:
            blog = None

        # Get the path alias mappings
        alias_templates = blog.template_maps if blog else model.TemplateMap.select()
        alias_templates = orm.select(
            e for e in alias_templates if e.file_template != '' and e.file_template is not None)

        LOGGER.debug('Alias templates: %s', list(alias_templates))

        entries = blog.entries if blog else model.Entry.select()
        for item in entries:
            entry.process(item, config, alias_templates)

        categories = blog.categories if blog else model.Category.select()
        for item in categories:
            category.process(item, config)
        if blog:
            category.process(blog, config)

if __name__ == '__main__':
    main()
