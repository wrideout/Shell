#!/usr/bin/python
#
# shell.py
#
# Just a small shell program I've written in order to become a little more 
# familiar with Python.  There are several parts to this shell:
#   -Printing a prompt
#   -Parsing a command and arguments
#   -Parsing the PATH variable into a series of directories to search
#   -Searching the directories in the PATH for the parsed command
#   -Command execution/displaying output
#
#   William Rideout
#   Dustin Schoenbrun
#   
# Changelog:
#   8/15/11 - Completed basic functionality, alias functionality, and history
#               logging.
#   8/16/11 - Added history searching, support for the `cd` command, and support
#               for the '/' and '~' directories.  Added support for redirection,
#               and background processes.

import subprocess
from subprocess import call
import os
import sys

global m_History
global m_Aliases

################################################################################
# Displays the shell prompt.  This prompt includes the name of the current user,
# the hostname of the current computer, and the current working directory.
# The user input is also read and returned.
def prompt():
################################################################################
    # start by getting the current user name
    username = os.getlogin()

    # now get the hostname
    hostname = os.uname()[1]

    # and finally the cwd
    cwd = os.getcwd().split('/')[-1]
    if not cwd:
        cwd = '/'

    return raw_input('\n' + username + '@' + hostname + ':' + cwd + '> ')

################################################################################
# Searches the .shell_history file for the passed string.  If a matching line is
# found, then the line is printed
def searchHistory(word):
################################################################################
    m_History = open(HOME + '.shell_history','r')

    for line in m_History:
        if word in line:
            print line
    
    m_History.close()

################################################################################
# Parses the read line into a list for processing, and returns said list.
def readLine(line):
################################################################################
    if line == 'exit':
        global EXIT
        EXIT = True
        return
    
    elif '???' in line:
        searchHistory(line.split()[1])
        return
    
    elif 'cd' in line:
        if '~' in line.split()[1]:
            os.chdir(HOME)
        else:
            os.chdir(line.split()[1])
        return
    
    else:
        return line.split()

################################################################################
# Searches the directories in the PATH for the parsed command.  If the command
# is found, then the full path to the executable is placed into the first index
# of the args list, and True is returned.  Otherwise, the list is left alone and
# False is returned.
def searchPath():
################################################################################
    for dir in PATH:
        # combine the command and this PATH entry
        file = dir + '/' + ARGS[0]
        
        if os.path.exists(file):
            ARGS[0] = file
            return True
    
    return False

################################################################################
# Searches the .shell_aliases file for aliases.  If one is matched to the
# current command, then this command is expanded and placed into the ARGS
# variable, and True is returned.  Otherwise, ARGS is cleared, and False is
# returned.
def searchAliases():
################################################################################
    global ARGS
    m_Aliases = open(HOME + '.shell_aliases', 'r')
    
    for line in m_Aliases:
        # skip lines that start with #... those are comments
        if not '#' in line:
            alias = line.split('=')

            if ARGS[0] in alias[0]:
                # parse the alias line...
                ARGS = alias[1].split()
                m_Aliases.close()
                return True
    
    m_Aliases.close()
    return False

################################################################################
# Redirects output to the specified stream.
def redirect(args):
################################################################################
    #rIn = open(sys.stdin)
    rOut = 0
    #rErr = sys.stderr
    
    if '>' in args:
        rIn = open(args[args.index('>') + 1], 'w')
        args.remove(args[args.index('>') + 1])
        args.remove('>')

    if '2>' in args:
        rErr = open(args[args.index('2>') + 1], 'w')
        args.remove(args[args.index('2>') + 1])
        args.remove('2>')

    if '<' in args:
        rIn = open(args[args.index('<') + 1], 'w')
        args.remove(args[args.index('<') + 1])
        args.remove('<')

    call(args, stdout = rOut)
    #stdin = rIn, stdout = rOut, stderr = rErr)

################################################################################
# Executes the command stored in ARGS.  Normally, this is a simple call to the
# call() function.  However, we need to check for any redirection, and act
# accordingly.
def execute():
################################################################################
    # redirected output
    if '>' in ARGS or '<' in ARGS or '2>' in ARGS:
        redirect(ARGS)

    # backgrounded execution
    if '&' in ARGS:
        try:
            pid = os.fork()
    
        except OSError, e:
            print 'failed to fork correctly... aborting shell'
            sys.exit(1)
        
        if pid == 0:
            print 'forking process to background...'
            ARGS.remove(ARGS[-1])
            os.execv(ARGS[0], ARGS)

    # normal execution
    else:
        call(ARGS)

################################################################################
# The main program
################################################################################
EXIT = False
HOME = '/home/' + os.getlogin() + '/'
PATH = os.environ['PATH'].split(os.pathsep)

while not EXIT:
    line = prompt()
    ARGS = readLine(line)
   
    if not EXIT and ARGS:
        STATUS = searchAliases() or searchPath()

        if not STATUS:
            print 'Command `%s` not found' % ARGS[0]
        
        else:
            # add the command to the .shell_history file
            m_History = open(HOME + '.shell_history', 'a')
            
            for string in ARGS:
                m_History.write(string + ' ')

            m_History.write('\n')
            m_History.close()
           
            execute()

# BEWARE: the history file is cleared at program termination
open(HOME + '.shell_history','w').close()
