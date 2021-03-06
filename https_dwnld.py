#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script allows to download file from password protected https urls.

USAGE:
    https_dwnld.py <user> <password> <url> [action] [flags]

    Positional Arguments:
        <user>      - HTTP Basic Auth user name
        <password>  - HTTP Basic Auth user password
        <url>       - URL of a file to be downloaded

    [action] is required and must be only one of the following:
        -o/--out <path>     : download file output directory path
        -s/--show           : print file content to console

    [flags] are optional and can be all of the following:
        -v/--version        : display version and exit
        -h/--help           : display help message and exit
        --debug             : increase logging verbosity
        -r/--raw            : hide download progress bar
"""

from __future__ import division, print_function

import os
import sys
import math
import logging
import ssl

__version__ = "2.2.2"
__author__ = "K. Dziadowiec (krzysztof.dziadowiec@gmail.com)"

logger = logging.getLogger(__name__)

# NOTE: PEP 476
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

try:
    NATIVE = False
    import requests
except ImportError as e:
    NATIVE = True
    if sys.version_info >= (3, 0):
        from urllib.error import HTTPError, URLError
        from urllib.request import (
            urlopen,
            HTTPPasswordMgrWithDefaultRealm,
            HTTPBasicAuthHandler,
            build_opener,
            install_opener,
        )
    else:
        from urllib2 import (
            urlopen,
            HTTPError,
            URLError,
            build_opener,
            install_opener,
            HTTPPasswordMgrWithDefaultRealm,
            HTTPBasicAuthHandler,
        )

try:
    import argparse
except ImportError:
    import optparse

# Fixes missing FileNotFoundError in Python 2
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def download_file(user, password, url, out_dir=None, show=False,
                  raw=False):
    """Download a file or print its content to terminal. Uses requests.

    The return values are:
        `Completed`     -- if downloading has been completed
        ``              -- show action has been completed
        `Error`         -- in case of any error
    """
    check_exclusive_positional_args(out_dir, show)

    try:
        file = requests.get(url, auth=(user, password), stream=True)

        if file.status_code is not requests.codes.ok:
            logger.error('URL Status Code: {}'.format(file.status_code))
            return 'Error'

        if show:
            print(try_decode(file.content), end='')
        elif out_dir:
            file_name = url.split("/")[-1]
            save_path = os.path.join(os.path.abspath(out_dir), file_name)
            logger.debug('downloading to: {}'.format(save_path))

            try:
                os.remove(save_path)
            except OSError:
                pass

            file_size = int(file.headers['content-length'])
            logger.debug('file size: {}'.format(file_size))
            chunk_size = 1024
            logger.debug('chunk size: {}'.format(chunk_size))
            chunk_count = int(math.ceil(file_size / chunk_size))
            logger.debug('chunk count: {}'.format(chunk_count))

            with open(save_path, 'ab') as output:
                chunks = file.iter_content(chunk_size=chunk_size)
                for i, chunk in enumerate(chunks):
                    output.write(chunk)
                    if raw:
                        continue
                    print_progress(
                        i + 1,
                        chunk_count,
                        bar_length=50,
                        prefix='Downloading Progress:',
                    )
            logger.debug(
                'downloaded size: {}'.format(os.path.getsize(save_path))
            )

    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        return 'Error'
    except FileNotFoundError as e:
        logger.error(e)
        return 'Error'
    else:
        return '' if show else 'Completed'


def download_file_native(user, password, url, out_dir=None, show=False,
                         raw=False):
    """Download a file or print its content to terminal. Uses urllib2/urllib.

    The return values are:
        `Completed`     -- if downloading has been completed
        ``              -- show action has been completed
        `Error`         -- in case of any error
    """
    check_exclusive_positional_args(out_dir, show)

    try:
        file = url_get(url, user, password)

        if show:
            print(try_decode(file.read()), end='')
        elif out_dir:
            file_name = url.split("/")[-1]
            save_path = os.path.join(os.path.abspath(out_dir), file_name)
            logger.debug('downloading to: {}'.format(save_path))

            try:
                os.remove(save_path)
            except OSError:
                pass

            file_size = get_content_length_native(file)
            logger.debug('file size: {}'.format(file_size))
            chunk_size = 1024
            logger.debug('chunk size: {}'.format(chunk_size))
            chunk_count = int(math.ceil(file_size / chunk_size))
            logger.debug('chunk count: {}'.format(chunk_count))

            with open(save_path, 'ab') as output:
                for i in range(chunk_count):
                    chunk = file.read(chunk_size)
                    output.write(chunk)
                    if raw:
                        continue
                    print_progress(
                        i + 1,
                        chunk_count,
                        bar_length=50,
                        prefix='Downloading Progress:',
                    )
            logger.debug(
                'downloaded size: {}'.format(os.path.getsize(save_path))
            )

    except HTTPError as e:
        logger.error(e)
        return 'Error'
    except URLError as e:
        logger.error(e)
        return 'Error'
    except FileNotFoundError as e:
        logger.error(e)
        return 'Error'
    else:
        return '' if show else 'Completed'


def check_exclusive_positional_args(arga, argb):
    if not bool(arga) ^ bool(argb):
        raise ValueError(
            'Only one of the exclusive positional args must be specified.'
        )


def get_content_length_native(file):
    if sys.version_info >= (3, 0):
        length = file.info()['content-length']
    else:
        length = file.info().getheader('Content-Length')

    if length is not None:
        return int(length)

    raise ValueError('Content-Length can not be of NoneType')


def url_get(url, user, password):
    top_level_url = url.rsplit('/', 1)

    password_mgr = HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, top_level_url, user, password)

    handler = HTTPBasicAuthHandler(password_mgr)

    opener = build_opener(handler)
    opener.open(url)
    install_opener(opener)

    return urlopen(url)


def print_progress(iteration, total, prefix='', suffix='', decimals=1,
                   bar_length=100):
    """Call in a loop to create terminal progress bar.

    Positional arguments:
        iteration -- current iteration
        total -- total iterations

    Optional arguments:
        prefix -- prefix string (default '')
        suffix -- suffix string (default '')
        decimals -- positive number of decimals in percent complete (default 1)
        bar_length -- character length of bar (default 100)
    """
    BAR_FILL = u'█' if sys.version_info >= (3, 0) else '█'
    percents = '{0:.{d}f}'.format(100 * (iteration / float(total)),
                                  d=decimals)
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '|{:-<{w}}|'.format(BAR_FILL * filled_length, w=bar_length)
    progress_bar = '\r{prefix} {bar} {percents}% {suffix}'.format(
        prefix=prefix, bar=bar, percents=percents, suffix=suffix)

    sys.stdout.write(progress_bar)

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def try_decode(byte_string):
    try:
        return byte_string.decode('utf-8')
    except UnicodeDecodeError:
        return byte_string


def parse_args(argv):
    try:
        return _parse_args_argparse(argv)
    except:
        return _parse_args_optparse(argv)


def _parse_args_optparse(argv):
    class PAOptionParser(optparse.OptionParser, object):
        def __init__(self, *args, **kw):
            self.posargs = []
            super(PAOptionParser, self).__init__(*args, **kw)

        def add_posarg(self, *args, **kw):
            pa_help = kw.get("help", "")
            kw["help"] = optparse.SUPPRESS_HELP
            o = self.add_option("--%s" % args[0], *args[1:], **kw)
            self.posargs.append((args[0], pa_help))

        def get_usage(self, *args, **kwargs):
            self.usage = "%%prog %s [options]\n\nPositional Arguments:\n %s" % \
                (' '.join(["<%s>" % arg[0] for arg in self.posargs]),
                 '\n '.join(["%s:\t\t%s" % (arg) for arg in self.posargs]))
            return super(PAOptionParser, self).get_usage(*args, **kwargs)

        def parse_args(self, *args, **kwargs):
            args = sys.argv[1:]
            args0 = []
            for p, v in zip(self.posargs, args):
                args0.append("--%s" % p[0])
                args0.append(v)
            args = args0 + args
            options, args = super(
                PAOptionParser, self).parse_args(args, **kwargs)
            if len(args) < len(self.posargs):
                msg = 'Missing value(s) for "%s"\n' % ", ".join(
                    [arg[0] for arg in self.posargs][len(args):])
                self.error(msg)
            return options, args

    parser = PAOptionParser(version=__version__)
    parser.add_option(
        '--debug',
        action='store_true',
        help='increase logging verbosity',
    )
    parser.add_posarg(
        'user',
        type=str,
        help='HTTP Basic Authentication user',
    )
    parser.add_posarg(
        'password',
        type=str,
        help='HTTP Basic Authentication password',
    )
    parser.add_posarg(
        'url',
        type=str,
        help='URL of a file to be downloaded',
    )
    parser.add_option(
        '-r',
        '--raw',
        dest='raw',
        action='store_true',
        help='hide progress bar',
    )

    def set_out(option, opt, value, parser):
        parser.values.out_dir = value
        parser.values.out_set_explicitly = True

    parser.add_option(
        '-o', '--out',
        type=str,
        dest='out_dir',
        help='downloading output directory',
        action='callback',
        callback=set_out,
    )
    parser.add_option(
        '-s', '--show',
        dest='show',
        action='store_true',
        help='show file content to console',
    )
    options, _ = parser.parse_args(argv[1:])
    parser.values.ensure_value('out_set_explicitly', False)
    if options.out_set_explicitly and options.show:
        parser.error('options -o and -s are mutually exclusive')
    if not (options.out_set_explicitly or options.show):
        parser.error('option -o or -s is required')

    return options


def _parse_args_argparse(argv):
    """Parse command-line args."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=__version__,
        help='display version and exit',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='increase logging verbosity',
    )
    parser.add_argument(
        'user',
        type=str,
        help='HTTP Basic Authentication user',
    )
    parser.add_argument(
        'password',
        type=str,
        help='HTTP Basic Authentication password',
    )
    parser.add_argument(
        'url',
        type=str,
        help='URL of a file to be downloaded',
    )
    parser.add_argument(
        '-r',
        '--raw',
        action='store_true',
        help='hide progress bar',
    )
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '-o', '--out',
        type=str,
        dest='out_dir',
        help='downloading output directory',
    )
    action_group.add_argument(
        '-s', '--show',
        action='store_true',
        help='show file content to console',
    )

    return parser.parse_args(argv[1:])


def initialize_logging(debug=False):
    """Initialize logging."""
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def run(argv):
    args = parse_args(argv)
    initialize_logging(args.debug)
    logger.debug(args)

    opts = dict(
        user=args.user,
        password=args.password,
        url=args.url,
    )

    if args.out_dir:
        opts.update(out_dir=args.out_dir)
    if args.show:
        opts.update(show=args.show)
    if args.raw:
        opts.update(raw=args.raw)
    logger.debug(opts)

    if not NATIVE:
        logger.debug('using `requests` library')
        retv = download_file(**opts)
    else:
        logger.debug('using native `urllib` library')
        retv = download_file_native(**opts)

    print(retv, end='')


if __name__ == "__main__":
    run(sys.argv)
