
import os
import sys
import argparse
import datetime
import logging.handlers
import logging
import time
import signal
import errno

__Author__ = """Zachary Gerber, Michael DeMory, (video)Piero Madar,
Mavrick Watts, Nikal Morgan, Chris Warren"""

logger = logging.getLogger(__name__)

files = {}
exit_flag = False


def magic_word_getter(path, start_row, magic_word):
    line_start = 0
    with open(path) as f:
        for line_start, line in enumerate(f):
            if line_start >= start_row:
                if magic_word in line:
                    logger.info(
                        f'Match found for {magic_word}'
                        f'found on line {line_start+1} in {path}'
                        )
    return line_start + 1


def dir_watcher(args):
    file_collection = os.listdir(args.directory)
    detect_added_and_removed_files(file_collection, args.extension)
    for f in files:
        files[f] = magic_word_getter(
            os.path.join(args.directory, f),
            files[f],
            args.magic_word
        )


def detect_added_and_removed_files(file_collection, ext):
    global files
    for f in file_collection:
        if f.endswith(ext) and f not in files:
            files[f] = 0
            logger.info(f'{f} added to watchlist.')
    for f in list(files):
        if f not in file_collection:
            logger.info(f'{f} removed from watchlist.')
            del files[f]
    return file_collection


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
    logger.warning('Received ' + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True


def create_parser():
    """create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--interval',
                        help='Sets the interval in seconds to check the '
                             'directory for magic words',
                        type=float,
                        default=1.0)
    parser.add_argument('-x', '--extension',
                        help='Sets the type of file to watch for',
                        type=str,
                        default='.txt')
    parser.add_argument('directory', help='directory to monitor')
    parser.add_argument('magic_word', help='The magic word/words to watch for')
    return parser


def main(args):
    """Main function is declared as standalone, for testability"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    polling_interval = parsed_args.interval
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s \
               %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d &%H:%M:%S',
        level=logging.DEBUG
    )
    # fh = logging.FileHandler(filename='my_watch_log.log')
    # logger.addHandler(fh)

    start_time = datetime.datetime.now()
    logger.info(
        '\n'
        '----------------------------------------------------\n'
        f'   Running {__file__}\n'
        f'   PID is {os.getpid()}\n'
        f'   Started on {start_time.isoformat()}\n'
        '-----------------------------------------------------\n'
    )
    logger.info(
        f'Watching directory:{parsed_args.directory},'
        f'File Extension:{parsed_args.extension},'
        f'Polling Interval:{parsed_args.interval},'
        f', Magic Text:{parsed_args.magic_word}'
        )

    # time.sleep(5.0)

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            dir_watcher(parsed_args)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f"{parsed_args.directory} directory not found")
                time.sleep(2)
            else:
                logger.error(e)
        except Exception as e:
            logger.error(f"UNHANDLED EXCEPTION: {e}")
        time.sleep(polling_interval)

    time_on = datetime.datetime.now() - start_time
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
