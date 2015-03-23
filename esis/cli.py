# -*- coding: utf-8 -*-
"""Elastic Search Index & Search."""

import argparse
import logging
import os

from esis.db import (
    DBReader,
    Database,
    TableReader,
)
from esis.fs import TreeExplorer

logger = logging.getLogger(__name__)

def main():
    """Entry point for the esis.py script."""
    args = parse_arguments()
    configure_logging(args.log_level)
    args.func(args)

def index(args):
    """Index database information into elasticsearch."""
    logger.debug('Indexing %r...', args.directory)
    tree_explorer = TreeExplorer(args.directory)
    for path in tree_explorer.paths():
        db_reader = DBReader(path)
        for table in db_reader.tables():
            table_reader = TableReader(db_reader.connection, table)
            logger.debug(table_reader)


def search(args):
    """Send query to elasticsearch."""
    logger.debug('Searching %r...', args.query)

def valid_directory(path):
    """Directory validation."""
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            '{!r} is not a valid directory'.format(path))

    if not os.access(path, os.R_OK | os.X_OK):
        raise argparse.ArgumentTypeError(
            'not enough permissions to explore {!r}'.format(path))

    return path

def configure_logging(log_level):
    """Configure logging based on command line argument.

    :param log_level: Log level passed form the command line
    :type log_level: int

    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Log to sys.stderr using log level
    # passed through command line
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    log_handler.setFormatter(formatter)
    log_handler.setLevel(log_level)
    root_logger.addHandler(log_handler)


def parse_arguments():
    """Parse command line arguments.

    :returns: Parsed arguments
    :rtype: argparse.Namespace

    """
    parser = argparse.ArgumentParser(description=__doc__)
    log_levels = ['debug', 'info', 'warning', 'error', 'critical']
    parser.add_argument(
        '-l', '--log-level',
        dest='log_level',
        choices=log_levels,
        default='warning',
        help=('Log level. One of {0} or {1} '
              '(%(default)s by default)'
              .format(', '.join(log_levels[:-1]), log_levels[-1])))

    subparsers = parser.add_subparsers(help='Subcommands')

    index_parser = subparsers.add_parser('index', help='Index SQLite database files')
    index_parser.add_argument('directory', type=valid_directory, help='Base directory')
    index_parser.set_defaults(func=index)

    search_parser = subparsers.add_parser('search', help='Search indexed data')
    search_parser.add_argument('query', help='Search query')
    search_parser.set_defaults(func=search)

    args = parser.parse_args()
    args.log_level = getattr(logging, args.log_level.upper())
    return args

if __name__ == '__main__':
    main()
