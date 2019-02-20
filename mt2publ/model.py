""" Maps the MT database schema to PonyORM """

import datetime

from pony import orm

db = orm.Database()  # pylint: disable=invalid-name


class Author(db.Entity):
    """ Blog authors """
    _table_ = 'mt_author'

    author_id = orm.PrimaryKey(int, column='author_id')
    basename = orm.Optional(str, column='author_basename')
    username = orm.Optional(str, column='author_name')
    name = orm.Optional(str, column='author_nickname')
    email = orm.Optional(str, column='author_email')
    url = orm.Optional(str, column='author_url')
    entries = orm.Set("Entry")


class Blog(db.Entity):
    """ Top-level blogs """
    _table_ = 'mt_blog'

    blog_id = orm.PrimaryKey(int, column='blog_id')

    name = orm.Optional(str, column='blog_name')
    description = orm.Optional(str, column='blog_description')

    entries = orm.Set('Entry')
    categories = orm.Set('Category')
    template_maps = orm.Set('TemplateMap')

    file_extension = orm.Optional(str, column='blog_file_extension')

    """ hack to make this act like a category for the exporter """
    path = ''
    basename = ''


class Entry(db.Entity):
    """ Entries """
    _table_ = 'mt_entry'

    entry_id = orm.PrimaryKey(int, column='entry_id')
    blog = orm.Optional(Blog, column='entry_blog_id')

    allow_comments = orm.Optional(bool, column='entry_allow_comments')
    author = orm.Optional(Author, column='entry_author_id')
    basename = orm.Optional(str, column='entry_basename')

    title = orm.Optional(str, column='entry_title')
    text = orm.Optional(str, column='entry_text')
    more = orm.Optional(str, column='entry_text_more')

    entry_type = orm.Optional(str, column='entry_class')

    created = orm.Optional(datetime.datetime, column='entry_created_on')
    last_modified = orm.Optional(datetime.datetime, column='entry_modified_on')

    status = orm.Required(int, column='entry_status')

    file_format = orm.Optional(str, column='entry_convert_breaks')

    categories = orm.Set('Placement')


class Category(db.Entity):
    """ Categories """
    _table_ = 'mt_category'

    category_id = orm.PrimaryKey(int, column='category_id')
    blog = orm.Optional(Blog, column='category_blog_id')

    basename = orm.Optional(str, column='category_basename')
    name = orm.Optional(str, column='category_label')
    description = orm.Optional(str, column='category_description')
    parent = orm.Optional('Category', column='category_parent')
    children = orm.Set('Category')

    entries = orm.Set('Placement')

    @property
    def path(self):
        """ Get the full path to this category """
        if self.parent and self.parent.category_id:
            return self.parent.path + '/' + self.basename
        return self.basename


class Placement(db.Entity):
    """ Entry placements """
    _table_ = 'mt_placement'

    placement_id = orm.PrimaryKey(int, column='placement_id')

    entry = orm.Required(Entry, column='placement_entry_id')
    category = orm.Required(Category, column='placement_category_id')
    is_primary = orm.Required(bool, column='placement_is_primary')


class TemplateMap(db.Entity):
    """ Template mappings """
    _table_ = 'mt_templatemap'

    templatemap_id = orm.PrimaryKey(int, column='templatemap_id')
    blog = orm.Optional(Blog, column='templatemap_blog_id')

    archive_type = orm.Optional(str, column='templatemap_archive_type')
    file_template = orm.Optional(str, column='templatemap_file_template')


def connect(**db_config):
    """ Connect to the database """
    db.bind(**db_config)
    db.generate_mapping(create_tables=False)
