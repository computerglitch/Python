#!/usr/bin/python
import os
import re
import sys
import subprocess
import string

# Nagios dictionary of exit codes
status      = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}

#Function to create a list of all software arrays on the linux node
def getSoftwareArrays():
    getArrays = subprocess.Popen(['/bin/egrep', '^md*', '/proc/mdstat'], stdout=subprocess.PIPE).communicate()[0]
    RaidList = string.split(getArrays)
    md = []
    for element in RaidList:
        m = re.match("(md.*)", element)
        if m:
            mdDevices = element.split()
            md.extend(mdDevices)
    return md

#Function to get the current state of a software array
def getArrayState(array):
    RaidMap = []
    setRaidDevice = "/dev/" + array
    mdadmDetail = subprocess.Popen(['mdadm', '--detail', setRaidDevice], stdout=subprocess.PIPE).communicate()[0]
    m = re.search("(State.*)", mdadmDetail)
    if m:
        return m.group(1)

#Check the software aray state to see if it's degraded
for array in getSoftwareArrays():
    mdState = getArrayState(array).lstrip().rstrip()
    if mdState != "State : clean":
        if mdState != "State : active":
            print "{ RAID WARNING - " + array + " - " + mdState + " }",
            sys.exit(status['WARNING'])
for array in getSoftwareArrays():
    mdState = getArrayState(array).lstrip().rstrip()
    if mdState == "State : clean":
        print "{ RAID OK - " + array + " - " + mdState + " }",
sys.exit(status['OK'])

