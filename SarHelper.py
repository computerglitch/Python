#!/bin/env python
import yum
import rpm
import os
import sys
import subprocess
import string
import pprint
if len(sys.argv) == 1:
    print "\nUsage: SarHelper.py [logfile] [start_time] [end_time]"
    print "Example: SarHelper.py /var/log/sa/sa04 10:00:00 14:30:00\n"
else:
    #get the required arguments [logfile] [start_time] [end_time]
    logfile_path = sys.argv[1]
    start_time = sys.argv[2]
    end_time = sys.argv[3]
    #define the packages we want installed
    packagesrereq = ["sysstat", "atop"]
    #function to check if the packages are installed
    def check_pkg (pkglist):
        yb = yum.YumBase()
    	missing_packages = set()
    	for package in pkglist:
            res = yb.rpmdb.searchNevra(name=package) 
       	    if not res:
	        missing_packages.add(package)
                print "\n\n" + package, "not installed! Would you like to install it?"
                yn = raw_input("[Y] or [n]: ").lower()
                if yn == "y":
                    yb.install(name=package)
                    yb.resolveDeps()
                    yb.processTransaction()
                elif yn == "n":
                    print "All required packages %s are not installed! Exiting."% (pkglist)
		    sys.exit()
    #call the check_pkg function
    check_pkg(packagesrereq)
    #function to allow different columns from sar to be displayed
    def sar_interface(input):
        x = input
        if x == "cpuidle":
            z = "$9"
	    y = "-u"
        if x == "idledate":
	    z = "$1, $2"
	    y = "-u"
	if x == "load":
            z = "$5, $6, $7"
            y = "-q"
	if x == "loaddate":
	    z = "$1, $2"
            y = "-q"
        cpuidle = "/usr/bin/sar -f %s -s %s -e %s %s | awk '{ print %s }' | grep -v 'idle' | grep -v 'Average' | grep -v 'Linux'"% (logfile_path, start_time, end_time, y, z)
        sar = subprocess.Popen(cpuidle,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = sar.communicate()[0]
        idle = string.split(output[1:-1], '\n')
        return idle
    #get the cpuload statistics as well as the load statistics and higlight areas of interest
    cpuidle = sar_interface("cpuidle")[1:-1]
    busycpu = min(cpuidle)
    date = sar_interface("idledate")[1:]
    load = sar_interface("load")[3:-1]
    busyload = max(load)
    loaddate = sar_interface("loaddate")[1:]
    for n,i in enumerate(cpuidle):
        if i==busycpu:
	    cpuidle[n]='\033[93m' + busycpu + '\033[0m'
    for n,i in enumerate(load):
        if i==busyload:
            load[n]='\033[93m' + busyload + '\033[0m'
    print "\nCPU Idle Percent         Load Averages"
    print "__________________       ___________________________"
    for a,b,c,d in zip(date, cpuidle, loaddate, load):
	print '%s  %s       %s  %s'% (a, b, c, d)
