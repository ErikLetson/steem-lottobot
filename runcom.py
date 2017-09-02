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

################################################################################
################################################################################

#function definitions

#function to write to config file
def write_to_file(write_token):

    with open(compath, 'w') as f:

        f.write(write_token)

    #delay for the take
    time.sleep(15)

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
        print("  c..........Cancel a pending command")
        print("  h..........Display this help screen")
        print("  k..........Kill ALL running instances of Lottobot immediately")
        print("  n..........Kill ALL running instances of Lottobot at the end of the current lottery")
        print("  q..........Quit the commander")
        print("  t..........Trim (empty) ALL log files")
        print("")
        print("Most commands that you issue to the commander will take effect only after a time delay. This is to ensure the command is read by Lottobot, since it only reads commands at a certain point in its 'pass' cycle.")
        print("To issue a command to the commander, input a letter corresponding to a command above and press [ENTER].")
        print("")

    #kill lottobot at the end of the next lottery
    elif cmd == 'c':

        print("")
        print("==Cancel Command==")
        print("")
        print("This will cancel a delayed action command.")

        answer = input("Are you SURE you want to do this? (y/n) >>>")

        if answer.lower() == 'y':

            #prompt
            print("")
            print("Issueing command...")
            print("Please wait appx. 15 seconds...")

            write_to_file("TXEN")

            print("")
            print("Command issued!")
            print("")

        else:

            print("OK, no command will be canceled.")
            print("")

    #kill lottobot immediately
    elif cmd == 'k':

        print("")
        print("==Kill Lottobot (Immediate)==")
        print("")
        print("This will kill ALL running instances of Lottobot immediately.")

        answer = input("Are you SURE you want to do this? (y/n) >>>")

        if answer.lower() == 'y':

            #prompt
            print("")
            print("Killing lottobot...")
            print("Please wait appx. 15 seconds...")

            write_to_file("KILL")

            print("")
            print("Killing complete!")
            print("")

        else:

            print("OK, Lottobot will continue running.")
            print("")

    #kill lottobot at the end of the next lottery
    elif cmd == 'n':

        print("")
        print("==Kill Lottobot (Next Lotto)==")
        print("")
        print("This will kill ALL running instances of Lottobot at the end of the current lottery.")

        answer = input("Are you SURE you want to do this? (y/n) >>>")

        if answer.lower() == 'y':

            #prompt
            print("")
            print("Issuing command...")
            print("Please wait appx. 15 seconds...")

            write_to_file("NEXT")

            print("")
            print("Command issued!")
            print("NOTE: This is a delayed command. You can cancel it by entering 'c' here in the commander.")
            print("")

        else:

            print("OK, no command will be issued.")
            print("")

    #Trim (empty) log files
    ##NOTE: Trimming will be improved to be more delicate (and have more modes)
    ## in a future version.
    elif cmd == 't':

        print("")
        print("==Trim Logs==")
        print("")
        print("This will empty the log files that Lottobot writes to.")

        answer = input("Are you SURE you want to do this? (y/n) >>>")

        if answer.lower() == 'y':

            #prompt
            print("")
            print("Emptying...")
            print("Please wait appx. 15 seconds...")

            write_to_file("TRIM")

            print("")
            print("Emptying complete!")
            print("")

        else:

            print("OK, no changes will be made.")
            print("")

    #quit the commander
    elif cmd == 'q':

        print("")
        print("==Quit==")
        print("")

        q = input("Are you sure you want to quit the commander? (y/n) >>>")

        if q.lower() == 'y':
            
            print("")
            print("Exiting the commander...")
            print("")
            
            break

        else:

            print("")

    #if the command is illegal
    else:

        print("Sorry, your command was not understood.")
        print("For a list of legal commands, press 'h'.")
        print("")

    cmd = input("Please enter a command >>>")
