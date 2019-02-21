""" Entry processor """

import email.message
import logging
import re
import os
import html
import html.parser
import datetime

from . import save_file

LOGGER = logging.getLogger("mt2publ.entry")

# Map MT status codes to Publ equivalents
PUBLISH_STATUS = [None, 'DRAFT', 'PUBLISHED', 'HIDDEN', 'SCHEDULED', 'GONE']

# Map MT format type to (linebreaks,extension)
FORMATS = {
    None: (False, 'html'),
    '': (False, 'html'),
    '0': (False, 'html'),
    'richtext': (True, 'html'),
    'markdown': (False, 'md'),
}

# Map MT page types to archive types
ARCHIVE_MAP = {
    'entry': 'Individual',
    'page': 'Page',
}


def get_category(entry):
    """ Try to figure out what the actual category is of the entry, using the
    common ad-hoc logic of categories being used as ersatz tags. In Publ we want
    an entry to live at its most specific location. """

    # Find the primary category
    primary = None
    for placement in entry.categories:
        if placement.is_primary:
            primary = placement.category

    # Get the primary category's base path
    base_path = primary.path if primary else ''

    # Find the most specific category that matches the root path
    best_path = base_path
    for placement in entry.categories:
        sub_path = placement.category.path
        if sub_path.startswith(base_path) and len(sub_path) > len(best_path):
            best_path = sub_path

    return best_path


class HtmlCleanup(html.parser.HTMLParser):
    """ HTML sanitizer to remove MT's weird editor extensions """
    ignore_tags = {'form'}
    ignore_attrs = {'mt:asset-id', 'contenteditable'}

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = False
        self._fed = []

    def get_data(self):
        """ Get the filtered HTML """
        return ''.join(self._fed)

    def error(self, message):
        """ Deprecated, per https://bugs.python.org/issue31844 """
        return message

    def handle_starttag(self, tag, attrs):
        self._handle_tag(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._handle_tag(tag, attrs, True)

    def handle_data(self, data):
        self._fed.append(data)

    def handle_endtag(self, tag):
        if tag.lower() in HtmlCleanup.ignore_tags:
            return
        self._fed.append('</{}>'.format(tag))

    def _handle_tag(self, tag, attrs, selfclose):
        if tag.lower() in HtmlCleanup.ignore_tags:
            return

        out = '<' + tag
        for k, val in attrs:
            if k.lower() not in HtmlCleanup.ignore_attrs:
                out += ' ' + k
            if val:
                out += '="{}"'.format(html.escape(val))

        if selfclose:
            out += ' /'
        out += '>'
        self._fed.append(out)


def format_text(text, convert):
    """ Format the text the way MT would """

    # strip out MT's editor extensions
    cleaner = HtmlCleanup()
    cleaner.feed(text)
    text = cleaner.get_data()

    if not convert:
        return text

    # All other known formats do the li2br thing

    # strip out DOS line endings
    text = text.replace('\r', '')

    # split it into paragraph-sized chunks
    paras = re.split('\n\n+', text)

    # reformat the paragraphs using the same logic as MT
    # adapted from MT::Util::html_text_transform
    for para in paras:
        if not re.search('</?(?:h[1-6]|table|ol|dl|ul|menu|dir|p|pre|center|' +
                         'form|fieldset|select|blockquote|address|div|hr)', para, re.I):
            para = '<p>' + para.replace('\n', '<br/>\n') + '</p>'

    return '\n\n'.join(paras)


def demarkdown(text):
    """ Convert an HTML element back into Markdown """
    return re.sub('</?em>', '*', text)


def build_path_aliases(entry, category, templates, archive_type):
    """ Convert a template mapping to a path-alias """

    # see
    # https://movabletype.org/documentation/appendices/archive-file-path-specifiers.html
    ext = '.' + entry.blog.file_extension
    params = {
        'a': entry.author.basename,
        'b': entry.basename,
        'c': category.path if category else '',
        'C': category.basename if category else '',
        'd': entry.created.strftime('%d'),
        'D': entry.created.strftime('%a'),
        'e': '%06d' % entry.entry_id,
        'E': str(entry.entry_id),
        'f': entry.basename + ext,
        'F': entry.basename,
        'h': entry.created.strftime('%H'),
        'H': entry.created.strftime('%-H'),
        'i': 'index' + ext,
        'I': 'index',
        'j': entry.created.strftime('%j'),
        'm': entry.created.strftime('%m'),
        'M': entry.created.strftime('%b'),
        'n': entry.created.strftime('%M'),
        's': entry.created.strftime('%S'),
        'x': ext,
        'y': entry.created.strftime('%Y'),
        'Y': entry.created.strftime('%y'),
        '%': '%'
    }

    aliases = []
    for template in (t for t in templates if t.archive_type == archive_type):
        # This is inefficient but it's easy to reason around.
        out = template.file_template
        idx = 0
        while idx < len(out):
            idx = out.find('%', idx)
            if idx < 0:
                break

            if out[idx + 1] == '-':
                token = out[idx + 2]
                dash = True
                skip = 3
            else:
                token = out[idx + 1]
                dash = False
                skip = 2

            subst = params[token]
            if dash:
                subst = subst.replace('_', '-')

            out = out[0:idx] + subst + out[idx + skip:]
            idx = idx + 1

        out = '/' + out
        out = out.replace('//', '/')
        aliases.append(out)

    return aliases


def process(entry, config, alias_templates):
    """ Process an entry from the database, saving it with the provided configuration """
    # pylint:disable=too-many-branches

    LOGGER.debug("Entry %d", entry.entry_id)

    message = email.message.Message()

    message['Import-ID'] = str(entry.entry_id)

    if entry.title:
        message['Title'] = demarkdown(entry.title)

    if entry.created:
        message['Date'] = entry.created.isoformat()

    if entry.last_modified:
        message['Last-Modified'] = entry.last_modified.isoformat()

    if entry.atom_tag:
        message['Atom-Tag'] = entry.atom_tag

    if entry.author.author_id > 0:
        if entry.author.name:
            message['Author'] = entry.author.name
        if entry.author.url:
            message['Author-URL'] = entry.author.url
        if entry.author.email:
            message['Author-Email'] = entry.author.email

    nl2br, ext = FORMATS[entry.file_format]

    body = format_text(entry.text, nl2br)
    if entry.more:
        body += '\n\n.....\n\n' + \
            format_text(entry.more, nl2br)
    message.set_payload(body)

    # If the entry status isn't Published or Scheduled, or if it's Published from
    # the future, map the status accordingly; otherwise it will infer
    # SCHEDULED.
    if entry.status not in [2, 4] or (entry.status == 2
                                      and entry.created > datetime.datetime.now()):
        message['Status'] = PUBLISH_STATUS[entry.status]

    if entry.entry_type != 'entry':
        message['Entry-Type'] = entry.entry_type

    # Categories don't really cleanly map between MT and Publ, so let's just
    # preserve these as custom headers for now
    category = None
    for placement in entry.categories:
        if placement.is_primary:
            category = placement.category
            message['Import-MainCategory'] = placement.category.path
        else:
            message['Import-OtherCategory'] = placement.category.path

    for alias in build_path_aliases(entry, category, alias_templates,
                                    ARCHIVE_MAP[entry.entry_type]):
        message['Path-Alias'] = alias

    # For simplicity's sake we'll only use the file path for the category
    output_category = get_category(entry)
    output_filename = os.path.join(*output_category.split('/'),
                                   f'{entry.basename}-{entry.entry_id}.{ext}')

    save_file(message, config.content_dir, output_filename, config)
