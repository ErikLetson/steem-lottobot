#! /usr/bin/python

###
#
# Lottobot Killit by Erik Letson
# |
# |--Simple method to kill a running instance of Lottobot cleanly
# |----Also sets up for rerunning
#
# Doesn't currently check to see if the kill actually took
#
###

import os, time

#variables
killpath = os.path.join('data', 'kill')

#write the command to the path

with open(killpath, 'w') as kf:

    kf.write("KILL")

#prompt
print("Killing lottobot...")
print("Please wait appx. 15 seconds...")

#delay (to make sure it takes)
time.sleep(15)

#rewrite
open(killpath, 'w').close()

#finish
print("Killing complete!")
print("Exiting...")
