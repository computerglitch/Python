#!/usr/bin/python
#########################################################
# This program bootstraps a system with specific        #
# settings. I did this simply as an experiment. Feel    #
# free to do what you want this program!. Although      #
# this program is meant to run on Redhat clones it      #
# could easily be modified for cross platform support.  #
#                                                       #
# Written by: Robbie Reese                              #
# Changes:                                              #
# v0.1      - 06/17/2013   - Inital Release             #
# v0.2      - 06/28/2013   - Added service checks       #
#########################################################

import fileinput
import sys
import subprocess
import string
import rpm
import yum
#System Settings
locale = "LANG=\"en_US.UTF-8\""
localeFile = "/etc/sysconfig/i18n"
swappiness = "10"
rpms = ["strace", "httpd", "mod_ssl", "atop", "nmap", "snmpcheck", "subversion", "sysstat", "xs", "mysql-server", "mysql"]
services = ["httpd", "mysqld"]
#Replace a specific line in a file with another line. Example: ReplaceAll("/file.1", "foo", "bar")
def ReplaceAll(file,searchExp,replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)
#Check the localeFile has the correct locale, if not present add it.
def LocaleSetting(locale):
    cmd = "grep 'LANG' %s" %(localeFile)
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    outnew = string.split(output)
    if not outnew:
        with open(localeFile, "a") as file:
            file.write(locale)
    elif outnew[0] != locale:
        ReplaceAll(localeFile, outnew[0], locale)
#Check the current swappiness and adjust accordingly.
def SwapSetting(swap):
    cmd = "cat /proc/sys/vm/swappiness"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    outnew = string.split(output)
    if outnew[0] != swap:
        cmd = "sysctl vm.swappiness=%s" %(swap)
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
    cmdgrep = "grep vm.swappiness /etc/sysctl.conf"
    ps = subprocess.Popen(cmdgrep,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    outnew = string.split(output)
    if not outnew:
        with open("/etc/sysctl.conf", "a") as file:
            file.write("vm.swappiness = %s\n" %(swap))
#Install packages specified - Note - The package name must be exact, for example use 'subversion' not 'svn'.
def CheckPackages(pkglist):
    yb = yum.YumBase()
    missing_packages = set()
    for pkgname in pkglist:
        if yb.rpmdb.searchNevra(name=pkgname):
            print "\033[92m" "%s is installed" "\033[0m" %(pkgname)
        else:
            print "\033[93m" "%s is not installed ... installing." "\033[0m" %(pkgname)
            missing_packages.add(pkgname)
            yb.install(name=pkgname)
            yb.resolveDeps()
            yb.processTransaction()
#Check that our services are running, and set to start at system boot.
def CheckServices(servicename):
    cmd = "ps -ef"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    for service in servicename:
        if service in output:
            print "\n" "\033[92m" "%s is running!" "\033[0m" %(service)
        else:
            print "\n" "\033[93m" "%s is not running! Starting service ..." "\033[0m" %(service)
            cmd = "service %s start && chkconfig %s on" %(service, service)
            ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
#Run our functions
CheckPackages(rpms)
SwapSetting(swappiness)    
LocaleSetting(locale)
CheckServices(services)
