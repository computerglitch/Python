#!/bin/env python
#########################################################
# This program creates a random numbered folder and     #
# converts a specified file into a random uuid. This    #
# folder and file are then set to be removed after 2    #
# hours.                                                #
#                                                       #
# Written by: Robbie Reese                              #
# Changes:                                              #
# v0.1      - 07/17/2013   - Inital Release             #
#########################################################

import os, shutil, uuid, sys
from random import randint

#Enter your file and folder details here
##topdir is the directory the random directory will be created in
topdir = "/www/domain.com/client/"
##file is the file you want to randomize
file = "ProgramName.exe"
##cronfile is the name of the cronfile to create
cronfile = "/etc/cron.d/tmplink"

#Function to create a directory from a random set of numbers
def create_random_dir(p):
    i = str(randint(1,1000000000000000))
    os.mkdir("%s/%s"% (p, i), 0755)
    return i

#Function to rename the file given into a random uuid
def randomize_file(r):
    ext = 'exe'
    src = r
    rando = str(uuid.uuid4())
    dst = '%s.%s'% (rando, ext)
    convert = os.rename(src,dst)
    return dst

#Create the random directory and place the randomized file in the random directory
dirpath = topdir + create_random_dir(topdir)
shutil.copy(file, dirpath)
fullpath = "%s/%s"% (dirpath, file)
z = randomize_file(fullpath)
shutil.move(z, dirpath)

#Create a cronjob that deletes the random directory/random file and the cronjob itself after 2 hours
cjob = open(cronfile, "w")
cjob.write("00 */3 * * * root /bin/rm -rf %s && /bin/rm %s"% (dirpath, cronfile))
cjob.write("\n")
cjob.close()

#Print the file file location to the command line
print 'The file can be accessed here: %s/%s'% (dirpath, z)
