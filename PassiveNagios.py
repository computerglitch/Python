#!/bin/env python
#########################################################
# This is a script to check the services on a localhost #       
# and report the results to the nagios host passively.  #       
#                                                       #
# Use cron to run this script at a defined period. I    #
# typically schedule the checks every 5 minutes.        #       
#                                                       #       
# Cron example:                                         #       
# */5 * * * *  root  /opt/passive_checks.py             #       
#                                                       #       
# This script relies on nagios-plugins-all, nsca client #       
# and mpt-status being installed and configured.        #       
#                                                       #       
# Current checks performed:                             #       
# - Ping                                                #       
# - CPU                                                 #       
# - LOAD                                                #       
# - LSI Raid Status                                     #       
# - [/] Partition Space                                 #       
#                                                       #       
# Written by: Robbie Reese                              #
# Changes:                                              # 
# v0.1      - 04/05/2013   - Inital Release             #
# v0.2      - 12/10/2013   - Added LSI RAID Function    #
#########################################################
import subprocess
import string
import socket
#Define our: local nagios plugin path(must have trailing "/") - nagios server ip - nsca binary location - hostname
plugins = "/usr/lib64/nagios/plugins/"
nagios_server = "172.26.12.17"
nsca = "/usr/sbin/send_nsca"
myhostname = (socket.gethostname())
#Define your service checks here
service_checks = {
    "check_00" : {
        "service" : "HA LVM [/backup]",
        "run_cmd" : "check_disk -w 10% -c 5% -p /backup"
    },
    "check_01" : {
        "service" : "LOAD",
        "run_cmd" : "check_load -w 19.0,20.0,21.0 -c 22.0,23.0,24.0"
    },
    "check_02" : {
        "service" : "PING",
        "run_cmd" : "check_ping -H localhost -w 3000.0,80% -c 5000.0,100% -p 5"
    },
    "check_03" : {
        "service" : "HA LVM [/fetalarchive]",
        "run_cmd" : "check_disk -w 10% -c 5% -p /fetalarchive"
    },
    "check_04" : {
        "service" : "CLUSTER SVC",
        "run_cmd" : "check_clustat"
    },
    "check_05" : {
        "service" : "PARTITION [/]",
        "run_cmd" : "check_disk -w 10% -c 5% -p /"
    },
    "check_06" : {
        "service" : "CPU",
        "run_cmd" : "check_cpu_perf 20 10"
    }
}
#Function to check if the host is up or not. This check is needed by nagios to show overall host status.
#Example: std_hostup_check("mysql0.localdomain")
def std_hostup_check(hostname):
    hostup = "check_ping -H localhost -w 3000.0,80% -c 5000.0,100% -p 5"
    cmd = subprocess.Popen(plugins + hostup,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = cmd.communicate()[0]
    return_code = cmd.returncode
    string = '"' + hostname + "\\t" + str(return_code) + "\\t" + output + '"'
    send_cmd = "echo -e %s | %s %s" %(string, nsca, nagios_server)
    ps = subprocess.Popen(send_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    return output
#Function to check the health of a RAID 1 on a LSI HBA. 
#This function requires that mpt-status be installed (http://sisyphus.ru/en/srpm/Branch4/mpt-status/get)
def lsi_raid_check():
    getid = "/usr/sbin/mpt-status -p | grep 'id' | awk '{ print $3 }' | tr -d id=,"
    ps = subprocess.Popen(getid,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    id = ps.communicate()[0]
    service_name = "LSI RAID"
    cmd = subprocess.Popen("/usr/sbin/mpt-status -s -i %s" %(id),shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    raw = cmd.communicate()[0]
    if raw.count("ONLINE") == 2:
        stat = [ "0", "OK: " ]
    elif raw.count("ONLINE") == 1:
        stat = [ "1", "WARNING: " ]
    else:
        stat = [ "2", "CRITICAL: " ]
    string = '"' + myhostname + "\\t" + service_name + "\\t" + stat[0] + "\\t" + stat[1] + raw + '"'
    send_cmd = "echo -e %s | %s %s" %(string, nsca, nagios_server)
    ps = subprocess.Popen(send_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    return output
#Function to process nagios passive checks and create the nsca string
#hostname = the local hostname, service_name = match the service description on the nagios server, check_cmd = the check command
#Example: passive_check(webhost0.localdomain, "ROOT PART", "check_disk -w 10% -c 5% -p /")
def passive_check(hostname, service_name, check_cmd):
    cmd = subprocess.Popen(plugins + check_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    process_out = cmd.communicate()[0]
    return_code = cmd.returncode
    return '"' + hostname + "\\t" + service_name + "\\t" + str(return_code) + "\\t" + process_out + '"'
#Function to send the defined service checks to the nsca server
#This function relies on the passive_check function to get the string to send.
def send_checks():
    for check in service_checks.values():
        string = passive_check(myhostname, check['service'], check['run_cmd'])
        cmd = "echo -e %s | %s %s" %(string, nsca, nagios_server)
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
    return output
std_hostup_check(myhostname)
send_checks()
lsi_raid_check()
