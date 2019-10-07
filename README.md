<table style="width: 646px;">
<tbody>
<tr>
<td style="width: 124px;"><img src="https://images-na.ssl-images-amazon.com/images/I/51XV10AJC8L._SX333_BO1,204,203,200_.jpg" width="124" height="166" /></td>
<td style="width: 124px;"><img src="https://mysite.du.edu/~jcalvert/railway/anim1.gif" width="124" height="166" /></td>
<td style="width: 241.832px;"><img src="http://www.dmainsurance.com/wp-content/uploads/2017/06/logging.jpg" width="202" height="150" /></td>
<td style="width: 257.168px;">
<h2 style="text-align: center;">Dirwatcher</h2>
<p style="text-align: center;">Long Running Program with signal handling and logging</p>
</td>
</tr>
</tbody>
</table>

### Objectives
 - Create a long running program
 - Demonstrate OS signal handling (SIGTERM, SIGINT)
 - Demonstrate program logging
 - Use exception handling to keep the program running
 - Structure your code repository using best practices
 - Read a set of requirements and deliver on them, asking for clarification if anything is unclear.

### Goal
For this assessment you will create your own small long-running program named `dirwatcher.py`.  This will give you experience in structuring a long-running program. The `dirwatcher.py` program should accept some command line arguments that will instruct it to monitor a given directory for text files that are created within the monitored directory.  Your `dirwatcher.py` program will continually search within all files in the directory for a 'magic' string which is provided as a command line argument.  This can be implemented with a timed polling loop.  If the magic string is found in a file, your program should log a message indicating which file and line number the magic text was found.  Once a magic text occurrence has been logged, it should not be logged again unless it appears in the file as another subsequent line entry later on.  Don't worry about reporting multiple occurrences of the magic string in a single line.

Files in the monitored directory may be added or deleted or appended at any time by other processes.  Your program should log a message when new files appear or other previously watched files disappear.  _Assume that files will only be changed by appending to them._  That is, anything that has previously been written to the file will not change.  Only new content will be added to the end of the file.  You don't have to continually re-check sections of a file that you have already checked.

Your program should terminate itself by catching SIGTERM or SIGINT (be sure to log a termination message).  The OS will send a signal event to processes that it wants to terminate from the outside, but only if the program is listening.  Think about when a sys admin wants to shutdown the entire computer for maintenance with a `sudo shutdown` command.  If your process has open file handles, or is writing to disk, or is managing other resources, this is the OS way of telling your program that you need to cleanup. Finish any writes in progress, and release resources before shutting down.

NOTE that handling OS termination signals and polling the directory that is being watched are two separate functions of your program.  You won't be getting an OS signal when files are created or deleted.

### Success Criteria
 - Use all best-practices that have been taught so far: docstrings, PEP8, unit tests, clean and readable code and meaningful commit messages.
 - Have a demonstrable OS signal handler
 - Log messages for files with magic text
 - Handle and log different exceptions such as file-not-found, directory-not-exist as well as handle and report top-level unknown exceptions so that your program stays alive.
 - Include a startup and shutdown banner in your logs and report the total runtime (uptime) within your shutdown log banner.  Please see the hints below if you don't understand what a logging banner is.
 - READ THE RUBRIC.

### Hints
```python
import signal
exit_flag = False
def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    logger.warn('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
 if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warn('Received ' + signames[sig_num])
    exit_flag = True

def main():
    # Hook these two signals from the OS .. 
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends either of these to my process.

    while not exit_flag:
        try:
            # call my directory watching function..
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_interval)
    
    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start.
```

### More hints
Create a versatile command line argument parser that can handle these options

 - An argument that controls the polling interval, instead of hard coding the polling interval.
 - An argument that specifics the magic text to search for, instead of hard-coding in your program
 - An argument that filters what kind of file extension to search within, such as `.txt` or `.log`
 - Argument to specify the directory to watch.  This directory may not yet exist!

### DOs and DON'Ts
DON'T use a strategy where you are counting the number of files in the directory, and then reporting files added or deleted if the count increases or decreases.  Why Not?  What if your polling interval is long, and one file gets replaced by another with a different name?  The file count will still be the same, but you will miss tracking the new file.

DO use a strategy where you can model the contents of the directory within your program, using a dictionary.  The keys will be filenames, the values will be the last line number that was read during the previous polling iteration.  Keep track of the last line read.  When opening and reading the file, skip over all the lines that you have already examined.

DO synchronize your dictionary model with the actual directory contents.  A sync must do these things:

For every file in the directory, add it to your dictionary if it is not already in your dictionary (exclude files without proper extensions).  Report new files that are added to your dictionary.
For every entry in your dictionary, find out if it still exists in the directory.  If not, remove it from your dictionary and report it as deleted.
Once you have synchronized your dictionary, it's time to iterate through all of its files and look for magic text, starting from the line number where you left off last time.
DON'T structure your program as one big monolithic function.

DO break up your code into small functions such as `scan_single_file()` and `detect_added_files()` and `detect_removed_files()` and `watch_directory()`

DO Read the attached Rubric as your key to maximizing points. Many students will submit their projects without reading the rubric points.  Don't be that person.


### Testing the Program
There is test code included in this repo.  Now that you know how Test Driven Development works, you should be able to write code that will pass the entire test suite.  Remember, VSCode has a built-in framework for discovering and running tests.

Test your dirwatcher program using TWO terminal windows.  In the first window, start your Dirwatcher with various sets of command line arguments.  Open a second terminal window and navigate to the same directory where your Dirwatcher is running, and try these procedures:

Run Dirwatcher with non-existent directory -- Every polling interval, it should complain about the missing watch directory.
Create the watched directory with mkdir -- Dirwatcher should stop complaining.
Add an empty file with target extension to the watched directory -- Dirwatcher should report a new file added.
Append some magic text to first line of the empty file -- Dirwatcher should report that some magic text was found on line 1, only once.
Append a few other non-magic text lines to the file and then another line with two or more magic texts -- Dirwatcher should correctly report the line number just once (don't report previous line numbers)
Add a file with non-magic extension and some magic text -- Dirwatcher should not report anything
Delete the file containing the magic text -- Dirwatcher should report the file as removed, only once.
Remove entire watched directory -- Dirwatcher should revert to complaining about a missing watch directory, every polling interval.

### Testing the Signal Handler
To test the OS signal handler part of your Dirwatcher, send a SIGTERM to your program from a separate shell window.

While your Dirwatcher is running, open a new shell terminal.
Find the process id (PID) of your dirwatcher.  PID is the first column listed from the ps utility.
Send a SIGTERM to your Dirwatcher
Your signal handler within your python program should be called.  Your code should exit gracefully with a Goodbye message ...
Example: How to shutdown your program
```console
piero@Piero-MBP: ~ $ ps aux | grep dirwatcher.py
48885 ttys000    0:00.80 python dirwatcher.py
49388 ttys002    0:00.00 grep dirwatcher.py
piero@Piero-MBP: ~ $ kill -s SIGTERM 48885
```

Example:  How to log a shutdown from within your program 
```
2018-08-31 11:36:29.510 __main__     WARNING  [MainThread  ] Received SIGTERM
2018-08-31 11:36:29.834 __main__     INFO     [MainThread  ] 
-------------------------------------------------------------------
   Stopped dirwatcher.py
   Uptime was 0:33:39.316367
-------------------------------------------------------------------
```
### How robust is your exception handler?
Will your long running program fail if the directory under watch is suddenly deleted?  If your watcher is pointed at another program's logging directory (which may come or go under different circumstances), you may want to add an exception handler and do some longer-duration retries instead of bailing out.  Perhaps you could retry the directory every 5 seconds.  Once you have a valid directory, you could do the file polling every 1 second.  This would require an outer loop and an inner loop.  

### Credits
This assignment was inspired by the story of (The Cuckoo's Egg)[https://en.wikipedia.org/wiki/The_Cuckoo%27s_Egg]
