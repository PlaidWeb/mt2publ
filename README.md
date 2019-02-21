# mt2publ

A tool to (partially) convert a Movable Type website for use with Publ.

## Basic usage

Currently only SQLite databases are supported (although adding direct support for MySQL and Postgres isn't too hard). If you have a MySQL database dump you can convert it to SQLite via [mysql2sqlite](https://github.com/dumblob/mysql2sqlite), and for Postgres you can follow [these instructions](https://manuelvanrijn.nl/blog/2012/01/18/convert-postgresql-to-sqlite/).

```
pip install mt2publ
mt2publ -b BLOG_ID -c /path/to/site/content database.db
```

If you don't specify `-b` then it will dump all entries and category metadata from the MT database, which is probably not what you want if you have multiple blogs configured on the dashboard. You can find the specific blog ID by looking at its URL from the dashboard.

## Current status

It has been tested successfully to extract entries and categories from a single Movable Type 4.21 website.

## Features

### What's supported

* Markdown, Rich Text, and HTML entries (both with and without "convert linebreaks" set), with both intro and extended text
* Publication status:
    * "Draft" and "Scheduled" supported directly
    * "Review" becomes "HIDDEN"
    * "Spam" becomes "GONE"
    * "Published" tries to do the right thing with Publ's scheduling model
* Category metadata
* Blog metadata (stored on the root category)
* Multiple categories with some limitations:
    * It tries to infer the actual category based on the entry's primary category and what other subcategories an entry is in
    * All category placements are set in metadata headers, allowing manual cleanup (and fancy template logic if you so choose)
* Sets path aliases of "entry" and "page" assets based on the original template mappings
* Preserves the original entry ID as `Import-ID`
* `Entry-Type` for entry vs. page

### What won't be supported

* Asset relocation
* Markdown conversion
* Native multiple categories (unless those become [supported by Publ](https://github.com/PlaidWeb/Publ/issues/163))
* Things which are absolutely too complicated to get right, such as:
    * Full automated template conversion

### What's feasible

* Limited template conversion as a starting point
* Limited category path alias support
* Native support for MySQL, Oracle, and Postgres databases
* Tags
* Output backends for other blogging systems (Jekyll, Pelican, etc.)
