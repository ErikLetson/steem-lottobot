#! /usr/bin/python

###
#
# Lottobot Configurator by Erik Letson
# |
# |--Simple configuration tool for lottobot
# |----Sets accounts, nodes, and WIF keys to be used by lottobot
#
# The configurator is light on error checking.
# It's going to take your word for it.
#
###

import os

#variables
conf_path = os.path.join("data", "config")
cmd = ""

#Read default values from file (removing the newline char also)
with open(conf_path, 'r') as config:
    
    acct = config.readline()
    acct = acct[0:len(acct) - 1]
    
    node = config.readline()
    node = node[0:len(node) - 1]

    outlog = config.readline()
    outlog = outlog[0:len(outlog) - 1]

    winlog = config.readline()
    winlog = winlog[0:len(winlog) - 1]

    errlog = config.readline()
    errlog = errlog[0:len(errlog) - 1]

    line = config.readline()
    keys = []

    while line != "" and line != '\n':
        
        keys.append(line[0:len(line) - 1])

        line = config.readline()

#function to write to config file
def write_to_config():

    with open(conf_path, 'w') as f:

        f.write(str(acct) + '\n')
        f.write(str(node) + '\n')
        f.write(str(outlog) + '\n')
        f.write(str(winlog) + '\n')
        f.write(str(errlog) + '\n')

        for k in keys:

            f.write(str(k) + '\n')

#prompt the user
print("")
print("==Welcome==")
print("")
print("Welcome to the Lottobot configurator.")
print("")

cmd = input("Please enter a command (enter 'h' for help) >>>")
        
while True:

    cmd = cmd.lower()

    #display help
    if cmd == 'h':
        
        print("")
        print("==Help==")
        print("")
        print("This program is the Lottobot configurator.")
        print("")
        print("The configurator is a simple command line program that allows you to customize Lottobot to your liking.")
        print("It can be used to set the account name, Steem node, and WIF keys that Lottobot uses.")
        print("In order to use Lottobot, you should set the account name and add Posting and Memo private WIF keys that match the account name to Lottobot's key list.")
        print("For most users, it is recommended that you use the default node.")
        print("")
        print("Following are some commands that you can issue to the configurator:")
        print("")
        print("  a..........Change account name")
        print("  d..........Delete *all* WIF keys")
        print("  e..........Change path to error log")
        print("  h..........Display this help screen")
        print("  k..........Add (a) WIF key(s)")
        print("  l..........List current configuration")
        print("  o..........Change path to output log")
        print("  n..........Change the default Steem node")
        print("  q..........Quit the configurator")
        print("  r..........Reset configuration to default")
        print("  w..........Change path to winner log")
        print("")
        print("The configurator is currently set to write to the configuration file located at " + conf_path)
        print("Assuming you didn't change it, this is the file that Lottobot will read its configuration data from.")
        print("You also can change Lottobot's configuration by directly editing the configuration file.")
        print("")

    #change account name
    elif cmd == 'a':

        print("")
        print("==Change Account Name==")
        print("")

        confirm = ""
        
        while confirm.lower() != 'y':

            new_name = input("Please enter a Steem account name >>>")

            print("")

            confirm = input("You entered " + str(new_name) + ". Is this name correct? (y/n) >>>")

            print("")

        print("Writing name " + str(new_name) + " to file...")

        acct = new_name

        write_to_config()

        print("")
        print("Write complete")
        print("Account name is set to " + str(new_name) + ".")
        print("")

    #delete all wif keys
    elif cmd == 'd':

        print("")
        print("==Delete WIF Keys==")
        print("")
        print("This will delete *ALL* of the WIF keys currently stored in the configuration file at " + conf_path)

        answer = input("Are you SURE? (y/n) >>>")

        if answer.lower() == 'y':

            print("Deleting keys...")

            keys = []

            write_to_config()

            print("All WIF keys deleted.")
            print("")

        else:

            print("OK, no keys will be deleted.")
            print("")

    #change error log path
    elif cmd == 'e':

        print("")
        print("==Error Log Path==")
        print("")

        ne = input("Enter the path to the error log (enter 'q' to quit) >>>")

        if ne.lower() == 'q':

            print("")
            print("OK, quitting...")
            print("")

        else:

            print("")
            print("Writing path to file...")

            errlog = ne

            write_to_config()

            print("")
            print("Write complete!")
            print("The error log will be recorded at: " + str(ne))
            print("")

    #add wif keys
    elif cmd == 'k':

        print("")
        print("==Add WIF Keys==")
        print("")
        print("Current keys:")

        if len(keys) > 0:
                
            for k in keys:

                print(k)

        else:

            print("None")

        print("")

        new_key = input("Enter WIF key (enter 'q' to quit) >>>")

        while new_key.lower() != "q":

            #some very mild error checking
            if new_key[0] == '5' and len(new_key) == 51:

                keys.append(new_key)

                print("")
                print("Added " + new_key + " to WIF key list.")
                print("")

            else:

                print("")
                print("Invalid WIF key.")
                print("All legal WIF keys are 51 characters long and begin with '5'.")
                print("Please try again.")
                print("")

            new_key = input("Enter WIF key (enter 'q' to quit) >>>")

        print("")
        print("Writing new keys to config file at " + conf_path + "...")

        write_to_config()

        print("Write complete!")
        print("Current keys:")

        if len(keys) > 0:
                
            for k in keys:

                print(k)

        else:

            print("None")
            
        print("")

    #list current configuration
    elif cmd == 'l':

        print("")
        print("==Current Configuration==")
        print("")

        print("Following is the current Lottobot configuration according to " + conf_path + ".")
        print("")

        print("  Current config file path......." + conf_path)
        print("")
        print("  Current account name..........." + str(acct))
        print("")
        print("  Current Steem node............." + str(node))
        print("")
        print("  Output log location............" + str(outlog))
        print("  Winner log location............" + str(winlog))
        print("  Error log location............." + str(errlog))
        print("")
        print("  Current keys:")
        print("  |")

        for k in keys:

            print("  |--" + str(k))

        print("")

    #change output log path
    elif cmd == 'o':

        print("")
        print("==Output Log Path==")
        print("")

        no = input("Enter the path to the output log (enter 'q' to quit) >>>")

        if no.lower() == 'q':

            print("")
            print("OK, quitting...")
            print("")

        else:

            print("")
            print("Writing path to file...")

            outlog = no

            write_to_config()

            print("")
            print("Write complete!")
            print("The output log will be recorded at: " + str(no))
            print("")

    #change node
    elif cmd == 'n':

        print("")
        print("==Change Node==")
        print("")
        print("Current node is set to: " + str(node))
        print("Default is wss://steemd.steemit.com (enter 'default' to use this node)")
        print("")

        new_node = input("Please enter the node address to use >>>")

        print("")
        print("Writing " + str(new_node) + " to file " + str(conf_path) + "...")
        
        if new_node.lower() == "default":

            node = "wss://steemd.steemit.com"

        else:

            node = new_node

        write_to_config()

        print("Write complete!")
        print("Node is set to: " + str(node))
        print("")

    #quit the configurator
    elif cmd == 'q':

        print("")
        print("==Quit==")
        print("")

        q = input("Are you sure you want to quit the configurator? (y/n) >>>")

        if q.lower() == 'y':
            
            print("")
            print("Exiting the configurator...")
            print("")
            
            break

        else:

            print("")

    #reset to defaults
    elif cmd == 'r':

        print("")
        print("==Reset to Default Configuration==")
        print("")

        print("Default configuration is as follows:")
        print("")
        print("  name.................None")
        print("  default node.........wss://steemd.steemit.com")
        print("  output log path......data/out.log")
        print("  winners log path.....data/winners.log")
        print("  error log path.......data/error.log")
        print("  keys.................None")
        print("")

        really = input("REALLY reset to these values? (y/n) >>>")

        if really.lower() == 'y':

            print("")
            print("Reseting...")

            acct = "None"
            node = "wss://steemd.steemit.com"
            outlog = "data/out.log"
            winlog = "data/winners.log"
            errlog = "data/error.log"
            keys = []

            write_to_config()

            print("Configuration successfully reset to default.")
            print("")

        else:

            print("")
            print("OK, no changes will be made.")
            print("")

    #change winner log path
    elif cmd == 'w':

        print("")
        print("==Winners Log Path==")
        print("")

        nw = input("Enter the path to the winners log (enter 'q' to quit) >>>")

        if nw.lower() == 'q':

            print("")
            print("OK, quitting...")
            print("")

        else:

            print("")
            print("Writing path to file...")

            winlog = nw

            write_to_config()

            print("")
            print("Write complete!")
            print("The winners log will be recorded at: " + str(nw))
            print("")

    #if the command is illegal
    else:

        print("Sorry, your command was not understood.")
        print("For a list of legal commands, press 'h'.")
        print("")

    cmd = input("Please enter a command >>>")
