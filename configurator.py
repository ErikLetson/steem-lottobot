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
acct = "None"
node = "wss://steemd.steemit.com"
outlog = os.path.join('data', 'out.log')
winlog = os.path.join('data', 'winners.log')
errlog = os.path.join('data', 'error.log')
assac = "None"
keys = []

################################################################################
################################################################################

#function definitions

#function to write to config file
def write_to_config():

    with open(conf_path, 'w') as f:

        f.write(str(acct) + '\n')
        f.write(str(node) + '\n')
        f.write(str(outlog) + '\n')
        f.write(str(winlog) + '\n')
        f.write(str(errlog) + '\n')
        f.write(str(assac) + '\n')

        for k in keys:

            f.write(str(k) + '\n')

################################################################################
################################################################################

#Default settings

#Read default values from file if it exists (removing the newline char also)
try:
    
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

        assac = config.readline()
        assac = assac[0:len(assac) - 1]

        line = config.readline()
        keys = []

        while line != "" and line != '\n':
            
            keys.append(line[0:len(line) - 1])

            line = config.readline()

#if the config file does not exist, make it and all other logs
except FileNotFoundError:

    #first, set our default (useless) values
    acct = "None"
    node = "wss://steemd.steemit.com"
    outlog = os.path.join('data', 'out.log')
    winlog = os.path.join('data', 'winners.log')
    errlog = os.path.join('data', 'error.log')
    assac = "None"
    keys = []

    #next, make our config file
    write_to_config()

    #now, as an added precaution, make all of our log files
    #we want this behavior for the first time the configurator is run
    open(outlog, 'w').close()
    open(winlog, 'w').close()
    open(errlog, 'w').close()

    #finally, also create the kill file, setup file, & info files
    open(os.path.join('data', 'command'), 'w').close()
    open(os.path.join('data', 'setup'), 'w').close()
    open(os.path.join('data', 'llstart'), 'w').close()
    open(os.path.join('data', 'llend'), 'w').close()
    open(os.path.join('data', 'prize'), 'w').close()

#make a blacklist
try:

    open(os.path.join('data', 'blacklist'), 'r').close()

except FileNotFoundError:
    
    open(os.path.join('data', 'blacklist'), 'w').close()

################################################################################
################################################################################

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
        print("It can be used to set the account name, Steem node, and WIF keys that Lottobot uses, among other things.")
        print("In order to use Lottobot, you should set the account name and add Posting and Memo private WIF keys that match the account name to Lottobot's key list.")
        print("For most users, it is recommended that you use the default node.")
        print("")
        print("Following are some commands that you can issue to the configurator:")
        print("")
        print("  a..........Change account name")
        print("  b..........Add account names to the blacklist")
        print("  d..........Delete *all* WIF keys")
        print("  e..........Change path to error log")
        print("  h..........Display this help screen")
        print("  k..........Add (a) WIF key(s)")
        print("  l..........List current configuration")
        print("  o..........Change path to output log")
        print("  n..........Change the default Steem node")
        print("  q..........Quit the configurator")
        print("  r..........Reset configuration to default")
        print("  s..........Add an associated account to make automatic transfers to")
        print("  w..........Change path to winner log")
        print("")
        print("To issue a command to the configurator, input a letter corresponding to a command above and press [ENTER].")
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
        print("This will change the name of the account that Lottobot uses (currently: " + acct + ")")
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

    #add account names to the longlotto blacklist
    elif cmd == 'b':

        print("")
        print("==Edit Blacklist==")
        print("")
        print("Here you can add accounts to the weekly lottery blacklist")
        print("Any account names on the blacklist will NOT be added as entrants for the weekly lottery, even if they meet the required conditions.")
        print("To remove a name that is already on the blacklist, simply reenter it. You will be prompted to confirm its removal.")
        print("")
        print("NOTE: You should include the name of the account ONLY. DO NOT use the '@' prefix.")
        print("")
        
        ba = ""
        bl = []

        #read the blacklist into the list
        with open(os.path.join('data', 'blacklist'), 'r') as f:

            for line in f.readlines():

                if line[len(line) - 1] == '\n':

                    line = line[0:len(line) - 1]

                if line != "":

                    bl.append(line)

        while ba != "!":

            ba = input("Enter an account name (enter '!' to quit) >>>")

            print("")

            if ba[0] == '@':

                print("Enter the account name ONLY. No '@'")
                print("")

            elif ba == '!':

                a = input("Are you done editing the blacklist? (y/n) >>>")
                print("")

                if a.lower != 'y':

                    ba = ""
                    print("OK, resuming...")
                    print("")

            elif ba in bl:

                a = input("REALLY remove '" + ba + "' from the blacklist? (y/n) >>>")
                print("")

                if a.lower == 'y':

                    print("Removing...")
                    print("")

                    bl.remove(ba)

                    print("'" + ba + "' has been removed from the blacklist.")
                    print("")

                else:

                    print("OK")
                    print("")

            else:

                a = input("You entered '" + ba + "', is this correct? (y/n) >>>")
                print("")

                if a.lower == 'y':

                    print("Adding '" + ba + "' to blacklist...")
                    print("")

                    bl.append(ba)

                    print("'" + ba + "' has been blacklisted from the weekly lottery.")
                    print("To undo this, enter '" + ba + "' again at the next prompt.")
                    print("")

                else:

                    print("OK, '" + ba + "' has not been blacklisted.")
                    print("")
                
        print("Writing blacklist to file...")
        print("")

        with open(os.path.join('data', 'blacklist'), 'at') as f:

            for item in bl:

                f.write(item + "\n")
            
    #delete all wif keys
    elif cmd == 'd':

        print("")
        print("==Delete WIF Keys==")
        print("")
        print("This will delete *ALL* of the WIF keys currently stored in the configuration file at " + conf_path)
        print("")

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
        print("  Current associated  account...." + str(assac))
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
        print("  associated account...None")
        print("  keys.................None")
        print("")

        really = input("REALLY reset to these values? (y/n) >>>")

        if really.lower() == 'y':

            print("")
            print("Reseting...")

            acct = "None"
            node = "wss://steemd.steemit.com"
            outlog = os.path.join('data', 'out.log')
            winlog = os.path.join('data', 'winners.log')
            errlog = os.path.join('data', 'error.log')
            assac = "None"
            keys = []

            write_to_config()

            print("Configuration successfully reset to default.")
            print("")

        else:

            print("")
            print("OK, no changes will be made.")
            print("")

    #add an associated account
    elif cmd == 's':

        print("")
        print("==Add Associated Account==")
        print("")
        print("This will change the name of the account that Lottobot will make automatic transfers to (default: None, currently: " + assac + ")")
        print("Note that this value is optional. To set the name of the account that Lottobot will use to perform its normal functions, enter option 'a' into the configurator.")
        print("")
        
        confirm = ""
        
        while confirm.lower() != 'y':

            new_name = input("Please enter a Steem account name >>>")

            print("")

            confirm = input("You entered " + str(new_name) + ". Is this name correct? (y/n) >>>")

            print("")

        print("Writing associated account name " + str(new_name) + " to file...")

        assac = new_name

        write_to_config()

        print("")
        print("Write complete")
        print("Associated account name is set to " + str(new_name) + ".")
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
