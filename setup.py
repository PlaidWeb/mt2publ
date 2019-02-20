"""Setup for Publ packaging"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from distutils.util import convert_path
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

main_ns = {}
ver_path = convert_path('mt2publ/__version__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name='mt2publ',

    version=main_ns['__version__'],

    description='A tool to convert a Movable Type site to a Publ site',

    long_description=long_description,

    long_description_content_type='text/markdown',

    url='https://github.com/PlaidWeb/Pushl',

    author='fluffy',
    author_email='fluffy@beesbuzz.biz',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',

        'License :: OSI Approved :: MIT License',

        'Natural Language :: English',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System',
    ],

    keywords='blog conversion movabletype mt publ',

    packages=['mt2publ'],

    install_requires=[
        'pony',
    ],

    extras_require={
        'dev': ['pylint', 'twine'],
    },

    project_urls={
        'Bug Reports': 'https://github.com/PlaidWeb/mt2publ/issues',
        'Funding': 'https://patreon.com/fluffy',
        'Source': 'https://github.com/PlaidWeb/mt2publ/',
        'Discord': 'https://discord.gg/xADP3ja'
    },

    entry_points={
        'console_scripts': [
            'mt2publ = mt2publ.__main__:main'
        ]
    },

    python_requires=">=3.4",
)
