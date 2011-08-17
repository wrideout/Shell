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

global m_Home
global m_History
global m_Aliases
global m_Exit
global m_Path
global m_Args

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
    history = open(m_History,'r')

    for line in history:
        if word in line:
            print line
    
    history.close()

################################################################################
# Parses the read line into a list for processing, and returns said list.
def readLine(line):
################################################################################
    global m_Exit

    if line == 'exit':
        m_Exit = True
        return
    
    elif '???' in line:
        searchHistory(line.split()[1])
        return
    
    elif 'cd' in line:
        if '~' in line.split()[1]:
            os.chdir(m_Home)
        else:
            os.chdir(line.split()[1])
        return
    
    else:
        return line.split()

################################################################################
# Searches the directories in the PATH for the parsed command.  If the command
# is found, then the full path to the executable is placed into the first index
# of the m_Args list, and True is returned.  Otherwise, the list is left alone 
# and False is returned.
def searchPath():
################################################################################
    global m_Args

    for dir in m_Path:
        # combine the command and this PATH entry
        file = dir + '/' + m_Args[0]
        
        if os.path.exists(file):
            m_Args[0] = file
            return True
    
    return False

################################################################################
# Searches the .shell_aliases file for aliases.  If one is matched to the
# current command, then this command is expanded and placed into the m_Args
# variable, and True is returned.  Otherwise, m_Args is cleared, and False is
# returned.
def searchAliases():
################################################################################
    aliases = open(m_Aliases, 'r')
    global m_Args

    for line in aliases:
        # skip lines that start with #... those are comments
        if not '#' in line:
            alias = line.split('=')

            if m_Args[0] in alias[0]:
                # parse the alias line...
                m_Args = alias[1].split()
                aliases.close()
                return True
    
    aliases.close()
    return False

################################################################################
# Redirects output to the specified stream.
def redirect(m_Args):
################################################################################
    # #rIn = open(sys.stdin)
    # rOut = 0
    # #rErr = sys.stderr
    # 
    # if '>' in m_Args:
    #     rIn = open(m_Args[m_Args.index('>') + 1], 'w')
    #     m_Args.remove(m_Args[m_Args.index('>') + 1])
    #     m_Args.remove('>')

    # if '2>' in m_Args:
    #     rErr = open(m_Args[m_Args.index('2>') + 1], 'w')
    #     m_Args.remove(m_Args[m_Args.index('2>') + 1])
    #     m_Args.remove('2>')

    # if '<' in m_Args:
    #     rIn = open(m_Args[m_Args.index('<') + 1], 'w')
    #     m_Args.remove(m_Args[m_Args.index('<') + 1])
    #     m_Args.remove('<')

    call(m_Args)

################################################################################
# Executes the command stored in m_Args.  Normally, this is a simple call to the
# call() function.  However, we need to check for any redirection, and act
# accordingly.
def execute():
################################################################################
    # redirected output
    if '>' in m_Args or '<' in m_Args or '2>' in m_Args:
        redirect(m_Args)

    # backgrounded execution
    if '&' in m_Args:
        try:
            pid = os.fork()
    
        except OSError, e:
            print 'failed to fork correctly... aborting shell'
            sys.exit(1)
        
        if pid == 0:
            print 'forking process to background...'
            m_Args.remove(m_Args[-1])
            os.execv(m_Args[0], m_Args)

    # normal execution
    else:
        call(m_Args)

################################################################################
# Counts the number of discreet entries (lines) in the command history and
# returns that number.
def getHistorySize():
################################################################################
    return len(open(m_History).readlines())

################################################################################
# Writes the current contents of m_Args to the command history.  If there are at
# least 1000 entries in the command history, then the new line is written to the
# bottom, and the uppermost line is deleted.
def writeToHistory():
################################################################################
    count = getHistorySize()
    
    print count
    
    if count >= 5:
        history = open(m_History, 'r')
        lines = history.readlines()
        history.close()

        history = open(m_History, 'w')
        history.write('\n'.join(lines[1:]))
        history.close()
    
    history = open(m_History, 'a')
    
    for string in m_Args:
        history.write(string + ' ')

    history.write('\n')
    history.close()


################################################################################
# The main program
################################################################################
m_Home = '/home/' + os.getlogin() + '/'
m_History = m_Home + '.shell_history'
m_Aliases = m_Home + '.shell_aliases'
m_Exit = False
m_Path = os.environ['PATH'].split(os.pathsep)

while not m_Exit:
    line = prompt()
    m_Args = readLine(line)

    if not m_Exit and m_Args:
        status = searchAliases() or searchPath()

        if not status:
            print 'Command `%s` not found' % m_Args[0]
        
        else:
            # add the command to the .shell_history file
            writeToHistory()

            execute()

