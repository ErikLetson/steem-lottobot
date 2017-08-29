#! /usr/bin/python

###
#
# Lottobot Runtime Commander by Erik Letson
# |
# |--Simple program used for issuing commands to Lottobot
# |----while it is running.
#
###

import os, time

#variables
compath = os.path.join('data', 'command')
cmd = ""
write_token = ""

################################################################################
################################################################################

#function definitions

#function to write to config file
def write_to_file():

    with open(compath, 'w') as f:

        f.write(write_token)

################################################################################
################################################################################

#prompt the user
print("")
print("==Welcome==")
print("")
print("Welcome to the Lottobot runtime commander.")
print("")

cmd = input("Please enter a command (enter 'h' for help) >>>")

while True:

    cmd = cmd.lower()

    #display help
    if cmd == 'h':
        
        print("")
        print("==Help==")
        print("")
        print("This program is the Lottobot runtime commander.")
        print("")
        print("The commander passes commands to a running instance of Lottobot.")
        print("It is used primarily to kill a running instance of Lottobot cleanly. However, it has a few other functions as well.")
        print("")
        print("Following are some of the commands that you can issue to the commander:")
        print("")
        print("  h..........Display this help screen")
        print("  k..........Kill ALL running instances of Lottobot immediately")
        print("  n..........Kill ALL running instances of Lottobot at the end of the current lottery")
        print("  q..........Quit the commander")
        print("  t..........Trim (empty) ALL log files")
        print("")
        print("To issue a command to the commander, input a letter corresponding to a command above and press [ENTER].")
        print("")
