""" Maps the MT database schema to PonyORM """

import datetime

from pony import orm

db = orm.Database()  # pylint: disable=invalid-name


class Author(db.Entity):
    _table_ = 'mt_author'

    author_id = orm.PrimaryKey(int, column='author_id')
    basename = orm.Optional(str, column='author_basename')
    username = orm.Optional(str, column='author_name')
    name = orm.Optional(str, column='author_nickname')
    email = orm.Optional(str, column='author_email')
    url = orm.Optional(str, column='author_url')
    entries = orm.Set("Entry")


class Entry(db.Entity):
    _table_ = 'mt_entry'

    entry_id = orm.PrimaryKey(int, column='entry_id')
    blog_id = orm.Optional(int, column='entry_blog_id')

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
    _table_ = 'mt_category'

    category_id = orm.PrimaryKey(int, column='category_id')
    blog_id = orm.Optional(int, column='category_blog_id')

    basename = orm.Optional(str, column='category_basename')
    name = orm.Optional(str, column='category_label')
    description = orm.Optional(str, column='category_description')
    parent = orm.Optional('Category', column='category_parent')
    children = orm.Set('Category')

    entries = orm.Set('Placement')

    @property
    def path(self):
        if self.parent and self.parent.category_id:
            return self.parent.path + '/' + self.basename
        return self.basename


class Placement(db.Entity):
    _table_ = 'mt_placement'

    placement_id = orm.PrimaryKey(int, column='placement_id')

    entry = orm.Required(Entry, column='placement_entry_id')
    category = orm.Required(Category, column='placement_category_id')
    is_primary = orm.Required(bool, column='placement_is_primary')


class TemplateMap(db.Entity):
    _table_ = 'mt_templatemap'

    templatemap_id = orm.PrimaryKey(int, column='templatemap_id')
    blog_id = orm.Optional(int, column='templatemap_blog_id')

    archive_type = orm.Optional(str, column='templatemap_archive_type')
    file_template = orm.Optional(str, column='templatemap_file_template')


def connect(**db_config):
    db.bind(**db_config)
    db.generate_mapping(create_tables=False)
