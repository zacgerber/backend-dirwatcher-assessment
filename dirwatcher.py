#!/usr/bin/env python
"""
A long-running program that watches a directory.

NOTE This implementation has a bug :)
If a partial magic string is appended to a watched file, saved, and then completed later on ..
it will not find the match because it uses raw file offsets instead of newline delimiters
to keep track of last position read.

"""
import sys
import os
import time
import logging
import signal
import argparse
import errno
from datetime import datetime as dt


# Create a local logger instance for this filename only
logger = logging.getLogger(__name__)

# A global flag shared by the main loop, and the signal handler
exit_flag = False


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.  Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets an event, and main() will exit it's loop when the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    logger.warn('Received OS process signal {}'.format(sig_num))

    # DO NOT use sys.exit() in here.  We want to give the while-loop a chance to close down
    # any open files, sockets, database connections, etc. so we don't leak resources.
    if sig_num == signal.SIGINT or sig_num == signal.SIGTERM:
        exit_flag = True


def search_for_magic(filename, pos, start_line, magic_string):
    """Searches fileobj for magic_string"""
    with open(filename) as f:
        f.seek(pos)
        line_num = start_line
        for line_num, line in enumerate(f, start_line + 1):
            # don't count as a full line if there is no newline at the end
            if not line.endswith('\n'):
                line_num -= 1
            if magic_string in line:
                logger.info('Magic text found: line {} of file {}'.format(line_num - 1, f.name))
        return f.tell(), line_num


def watch_directory(path, magic_string, ext, interval):
    """Inspects all text files within given path, for a magic string"""
    # This dictionary is a mapping of filenames.  Keys are absolute paths,
    # Values are the last byte offset from previous iteration (or 0)

    abs_path = os.path.abspath(path)
    files = {}

    while not exit_flag:
        time.sleep(interval)
        # add files to our dict that are not yet present
        for f in os.listdir(abs_path):
            if f not in files:
                logger.info('File added: ' + f)
                files[f] = (0, 1)
        # remove files that have disappeared
        # NOTE USE OF list(dict) to avoid 'dictionary changed size during iteration'
        for f in list(files):  
            if f not in os.listdir(abs_path):
                logger.info('File removed: ' + f)
                files.pop(f)
        
        for f, v in files.items():
            pos, line = v
            if f.endswith(ext):
                fp = os.path.join(abs_path, f)
                files[f] = search_for_magic(fp, pos, line, magic_string)


def create_parser():
    """Returns a cmd line argument parser"""
    parser = argparse.ArgumentParser(
        description='Watches a directory of text files for a magic string')
    parser.add_argument('-e', '--ext', type=str, default='.txt',
                        help='Text file extension to watch e.g. .txt, .log')
    parser.add_argument('-i', '--interval', type=float,
                        default=1.0, help='Number of seconds between polling')
    parser.add_argument('path', help='Directory path to watch')
    parser.add_argument('magic', help='String to watch for')
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # If no cmd line args present, they are just horsing around.
    if not args:
        parser.print_usage()
        sys.exit(1)

    # Take a time measurement of when we started watching
    app_start_time = dt.now()

    # For now, set up just to log to console
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s [%(threadName)-12s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)

    # A bold startup banner that is easy to see when quickly scrolling through a log file
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        '    Running {0}\n'
        '    Started on {1}\n'
        '-------------------------------------------------------------------\n'
        .format(__file__, app_start_time.isoformat())
    )

    # Install termination signal handlers.
    # Now we can hear when OS sends one of these signals to our python process
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Main loop, keep alive forever unless we receive a SIGTERM, SIGINT
    while not exit_flag:

        try:
            watch_directory(args.path, args.magic, args.ext, args.interval)

        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(
                    'Directory or file not found: {}'.format(os.path.abspath(args.path)))
            else:
                logger.error(e)
            time.sleep(5.0)
            continue

        except Exception as e:
            error_str = 'Unhandled Exception in MAIN\n{}\nRestarting ...'.format(
                str(e))
            logger.error(error_str, exc_info=True)
            time.sleep(5.0)
            continue

    # Alas, we are dying a graceful death
    uptime = dt.now() - app_start_time
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        '   Stopped {0}\n'
        '   Uptime was {1}\n'
        '-------------------------------------------------------------------\n'
        .format(__file__, str(uptime)))

    logging.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
