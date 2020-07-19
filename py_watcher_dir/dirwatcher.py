
import errno
import os
import sys
import argparse
from datetime import datetime as dt
import logging.handlers
import logging
import time
import signal

__Author__ = """Zachary Gerber, Michael DeMory, (video)Piero Madar,
Mavrick Watts, Nikal Morgan"""

logger = logging.getLogger(__name__)

files = {}
exit_flag = False


def watch_directory():
    pass


def scan_single_file():
    pass


def detect_added_files():
    pass


def detect_removed_files():
    pass


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here
    as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if
    the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    logger.warn('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def create_parser():
    """create an argument parser object"""
    parser = argparse.Argumentparser(
        description="Watches a directory of text files for a magic string"
    )
    parser.add_argument('-i', '--interval', type=float, default=1.0,
                        help='Sets the interval in seconds to check the '
                        'directory for magic words'
    parser.add_argument('-x', '--extension', type=str, default='.txt'
                        help='Sets the type of file to watch for'
    parser.add_argument('directory', help='directory to monitor')
    parser.add_argument('magic_word', help='The magic word/words to watch for')
    return parser


def main(args):
    """Main function is declared as standalone, for testability"""
    parser = create_parser()
    parser_args = parser.parse_args(args)
    polling_interval = parsed_args.interval
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s \
               %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d &%H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    start_time = dt.dt.now()
    logger.info(
        '\n'
        '----------------------------------------------------\n'
        f'   Running {__file__}\n'
        f'   Started on {start_time.isoformat()}\n'
        '-----------------------------------------------------\n'
    )

    time.sleep(5.0)
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            watch_directory(parsed_args)
            pass
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error("{} directory not found".format(
                    parsed_args.directory))
                time.sleep(2)
            else:
                logger.error(e)
        except Exception as e:
            logger.error("UNHANDLED EXCEPTION: {}".format(e))
        time.sleep(polling_interval)

    time_on = dt.dt.now() - start_time
    logger.info(
        '\n'
        '----------------------------------------------------\n'
        f'   Stopped {__file__}\n'
        f'   Time_on was {str(time_on)}\n'
        '-----------------------------------------------------\n'
    )
    logging.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:])
