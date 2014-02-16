#!/bin/env python
#########################################################
# Communicate via ssh to multiple nodes. I could just   #       
# use fabric but want to mess around with paramiko ;p   #       
#                                                       #       
#                                                       #       
# Written by: Robbie Reese                              #
#########################################################


import paramiko, sys

#Log paramiko to ssh.log and setup the paramiko client
paramiko.util.log_to_file('ssh.log')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.load_system_host_keys()

#Get the nodes to run the command on
if len(sys.argv) == 1:
    print "Usage: sshcom.py <nodes> <command to run in quotes>"
else:
    znodes = sys.argv[1]
    comrun = sys.argv[2]

#Function to create a list of node names (if the node does not require 00 01 02 etc, remove the zfill)
def nodes(nodename):
    xnodes = []
    for hostnum in range (00, 14):
        xnodes.append(nodename + "-" + str(hostnum).zfill(2))
    return xnodes

#Function to run the command given on a group of nodes
def runcom():
    for graphicnodes in nodes(znodes):
        client.connect(graphicnodes)
        stdin, stdout, stderr = client.exec_command(comrun)
        for command in stdout:
            print '... ' + command.strip('\n')
    return command

runcom()
client.close()
