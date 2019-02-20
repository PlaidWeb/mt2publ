""" Entry processor """

import email


def process(entry, config):
    """ Process an entry from the database, saving it with the provided configuration """

    print("Entry {id}: {title}".format(entry.entry_id, entry.title))
    for placement in entry.categories:
        print("    Category: {path} {primary}".format(
            placement.category.path, placement.is_primary))
