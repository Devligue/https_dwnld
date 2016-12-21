#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script allows to download file from user&password protected https url.

ORIGINAL FILE NAME:                                              https_dwnld.py

ARGUMENTS:
Short:    Long:               Description:                      Status:
-h        --help              show help for this script                optional
-u        --user              user name for url login                obligatory
-p        --password          password for url login                 obligatory
-f        --file_url          complete url to downloaded file        obligatory
-d        --save_directory    path to file save directory            obligatory
-o        --only_show         use to print instead of dwnld            optional
-s        --silent            use to hide progress bar                 optional

EXAMPLARY USAGE (from cmd line / terminal):
/----- disclaimer - put your own values in place of <some_argument_name> -----/

1. To download file to specified directory (short parameters):
>>> https_dwnld.py -u <user> -p <pass> -f <url_to_file> -d <file_save_dir>

2. To download file to specified directory (long parameters):
>>> https_dwnld.py --user <user> --password <pass> --file_url <url_to_file>
--save_directory <file_save_dir>

3. To print file text content /for text files only/ (short parameters):
>>> https_dwnld.py -u <user> -p <pass> -f <url_to_file> -d <file_save_dir> -o

4. To print file text content /for text files only/ (long parameters):
>>> https_dwnld.py --user <user> --password <pass> --file_url <url_to_file>
--save_directory <file_save_dir> --only_show

5. To do any of the above but w/o displaying progress bar in terminal add '-s'
or '--silent' just like:
>>> https_dwnld.py --user <user> --password <pass> --file_url <url_to_file>
--save_directory <file_save_dir> --only_show --silent

OUTPUT:
If everything worked fine script returns 'Completed' string to the console. If
option show_only was used script will return file text content string instead
of 'Completed' string. In case of any error an 'Error' string will be returned
with no additional information.
"""

__version__ = "1.0.4"
__author__ = "K. Dziadowiec (krzysztof.dziadowiec@gmail.com)"

import os
import sys
import getopt
import urllib2
try:
    import requests
    NATIVE = False
except ImportError:
    NATIVE = True

SLASH = "\\" if sys.platform == "win32" else "/"


def download_file(user, password, file_url, save_directory,
                  only_show=False, silent=False):
    """Call to download file or print its content to terminal.

    Required keyword arguments:
    user -- user name required for login
    password -- password required for login
    file_url -- complete url to file being downloaded
    save_directory -- path to dir that downloaded file will be saved to

    Optional keyword arguments:
    only_show -- set True to print content instead of downloading the file
    silent -- set True to hide downloading progress bar in terminal

    Returns string:
    Completed -- if file has been downloaded succesfully
    Error -- in case of any error
    <file text content> -- if only_show has been used
    """
    file_name = file_url.split("/")[-1]
    file_save_path = save_directory + SLASH + file_name

    if os.path.isfile(file_save_path):
        os.remove(file_save_path)

    try:
        file = requests.get(file_url, auth=(user, password), stream=True)

        if file.status_code is not requests.codes.ok:
            output = "Error"
        else:
            if not only_show:
                file_size = int(file.headers['content-length'])
                read_size = int(file_size) // 50

                with open(file_save_path, 'ab') as output:
                    if read_size == 0:
                        output.write(file.content)
                    else:
                        for i, chunk in enumerate(
                                file.iter_content(chunk_size=read_size)):
                            output.write(chunk)
                            if not silent:
                                print_progress(
                                    i, 50, prefix='Downloading Progress:',
                                    suffix='Complete', bar_length=50)
                    output = "Completed"
            else:
                output = file.content
    except requests.exceptions.ConnectionError:
        output = 'Error'

    sys.stdout.write(output)
    sys.stdout.flush()

    return output


def download_file_native(user, password, file_url, save_directory,
                         only_show=False, silent=False):
    """Call to download file or print its content to terminal.

    This function does exactly the same as download_file() but using nativ
    python packege urllib2 instead of requests.

    Required keyword arguments:
    user -- user name required for login
    password -- password required for login
    file_url -- complete url to file being downloaded
    save_directory -- path to dir that downloaded file will be saved to

    Optional keyword arguments:
    only_show -- set True to print content instead of downloading the file
    silent -- set True to hide downloading progress bar in terminal

    Returns string:
    Completed -- if file has been downloaded succesfully
    Error -- in case of any error
    <file text content> -- if only_show has been used
    """
    file_name = file_url.split("/")[-1]
    top_level_url = file_url[:-len(file_name)]
    file_save_path = save_directory + SLASH + file_name

    if os.path.isfile(file_save_path):
        os.remove(file_save_path)

    opener = create_opener(user, password, top_level_url)

    try:
        file, file_size = open_file(opener, file_url)

        if not only_show:
            read_size = int(file_size) // 50

            with open(file_save_path, 'ab') as output:
                if read_size == 0:
                    output.write(file.read(int(file_size)))
                else:
                    for i in range(51):
                        output.write(file.read(read_size))
                        if not silent:
                            print_progress(
                                i, 50, prefix='Downloading Progress:',
                                suffix='Complete', bar_length=50)
                output = 'Completed'
        else:
            output = file.read()
    except urllib2.HTTPError, e:
        output = 'Error'
    except urllib2.URLError, e:
        output = 'Error'

    sys.stdout.write(output)
    sys.stdout.flush()

    return output


def create_opener(user, password, top_level_url):

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, top_level_url, user, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)

    return opener


def open_file(opener, file_url):

    opener.open(file_url)
    urllib2.install_opener(opener)
    try:
        file = urllib2.urlopen(file_url)
    except:
        raise
    file_size = file.info().getheader('Content-Length').strip()

    return file, file_size


def print_progress(iteration, total, prefix='', suffix='',
                   decimals=1, bar_length=100):
    """Call in a loop to create terminal progress bar.

    Required keyword arguments:
    iteration -- current iteration
    total -- total iterations

    Optional keyword arguments:
    prefix -- prefix string (default '')
    suffix -- suffix string (default '')
    decimals -- positive number of decimals in percent complete (default 1)
    bar_length -- character length of bar (default 100)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = u'█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' %
                     (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == "__main__":

    only_show = False
    silent = False

    opts, args = getopt.getopt(
        sys.argv[1:],
        "hu:p:f:d:os",
        ["help", "user=", "password=", "file_url=", "save_directory=",
         "only_show", "silent"])

    if (len(opts) == 0 or
            (len(opts) == 1 and opts[0][0] not in ('-h', "--help")) or
            (len(opts) > 1 and len(opts) < 4) or
            len(opts) > 6):
        print "Incorrect usage. To get help try:\n\nhttps_dwnld.py --help"
        sys.exit()

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print __doc__
            sys.exit()
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-f", "--file_url"):
            file_url = arg
        elif opt in ("-d", "--save_directory"):
            save_directory = arg
        elif opt in ("-o", "--only_show"):
            only_show = True
        elif opt in ("-s", "--silent"):
            silent = True

    if not NATIVE:
        download_file(user=user, password=password,
                      file_url=file_url, save_directory=save_directory,
                      only_show=only_show, silent=silent)
    else:
        download_file_native(user=user, password=password,
                             file_url=file_url, save_directory=save_directory,
                             only_show=only_show, silent=silent)

    sys.exit(0)
