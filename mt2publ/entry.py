""" Entry processor """

import email.message
import logging
import re
import os

import slugify

LOGGER = logging.getLogger("mt2publ.entry")

# Map MT status codes to Publ equivalents
PUBLISH_STATUS = [None, 'DRAFT', 'PUBLISHED', 'HIDDEN', 'SCHEDULED', 'GONE']

# Map MT format type to (linebreaks,extension)
FORMATS = {
    None: (False, 'html'),
    False: (False, 'html'),
    True: (True, 'html'),
    'richtext': (True, 'html'),
    'markdown': (False, 'md'),
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


def format_text(text, convert):
    """ Format the text the way MT would """

    # TODO: convert <form mt:asset-id> stuff into the actual asset link

    if not convert:
        return text

    # All other known formats do the li2br thing

    # strip out DOS line endings
    text = text.replace('\r', '')

    # split it into paragraph-sized chunks
    paras = re.split('\n\n+', text)

    # reformat the paragraphs using the same logic as MT
    formatted = []
    for para in paras:
        if not re.search('</?(?:h1|h2|h3|h4|h5|h6|table|ol|dl|ul|menu|dir|p|pre|center|form|fieldset|select|blockquote|address|div|hr)', para):
            para = '<p>' + para.replace('\n', '<br/>\n') + '</p>'

    return '\n\n'.join(paras)


def demarkdown(text):
    """ Convert an HTML element back into Markdown """
    return re.sub('</?em>', '*', text)


def format_message(message):
    """ Convert an email.message into a text string, eliding MIME encoding stuff """
    output = ''
    for key, val in message.items():
        output += '{}: {}\n'.format(str(key), str(val))
    output += '\n'
    output += message.get_payload()

    return output


def process(entry, config):
    """ Process an entry from the database, saving it with the provided configuration """

    LOGGER.info("Entry %d", entry.entry_id)

    message = email.message.Message()

    message['Import-ID'] = str(entry.entry_id)

    if entry.title:
        message['Title'] = demarkdown(entry.title)

    if entry.created:
        message['Date'] = entry.created.isoformat()

    if entry.last_modified:
        message['Last-Modified'] = entry.last_modified.isoformat()

    nl2br, ext = FORMATS[entry.file_format]

    body = format_text(entry.text, nl2br)
    if entry.more:
        body += '\n.....\n' + \
            format_text(entry.more, nl2br)
    message.set_payload(body)

    if entry.status:
        message['Status'] = PUBLISH_STATUS[entry.status]

    if entry.entry_type != 'entry':
        message['Entry-Type'] = entry.entry_type

    # Categories don't really cleanly map between MT and Publ...
    for placement in entry.categories:
        if placement.is_primary:
            message['Import-Category'] = placement.category.path
        else:
            message['Import-OtherCategory'] = placement.category.path

    # For simplicity's sake we'll only use the file path for the category
    output_directory = os.path.join(*get_category(entry).split('/'))

    output_filename = 'import-{id}-{slug}.{ext}'.format(
        id=entry.entry_id,
        slug=entry.slug_text or slugify.slugify(entry.title),
        ext=ext)

    output_text = format_message(message)
    LOGGER.debug("Dry run file: %s/%s\n%s\n\n",
                 output_directory, output_filename, output_text)

    if config.content_dir:
        save_file(message, os.path.join(config.content_dir,
                                        output_directory), output_filename)
