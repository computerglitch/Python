#!/bin/env python

import sys, os, subprocess, string

# exit codes for nagios status
status = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}

def pdu_check(host, check):
    if check == 'load':
	x = '.1.3.6.1.4.1.1718.3.2.2.1.7'
    elif check == 'temp':
	x = '.1.3.6.1.4.1.1718.3.2.5.1.6'
    elif check == 'humi':
	x = '.1.3.6.1.4.1.1718.3.2.5.1.10'
    else:
	print
    p = subprocess.Popen(['/usr/bin/snmpwalk', '-v2c', '-c', 'public', host, x], stdout=subprocess.PIPE)
    result = p.communicate()[0]
    sum = string.split(result)
    return sum

if len(sys.argv) == 1:
    print '\n', 'Usage: pdu_monitor.py <ip> <[load],[temp],[humi]>', '\n'
else:
    x = sys.argv[1]
    y = sys.argv[2]
    if y == 'load':
        print 'Load:', float(pdu_check(x, y)[3]) / 100, float(pdu_check(x, y)[7]) / 100, float(pdu_check(x,y)[11]) / 100
    elif y == 'temp':
        if '-1' in pdu_check(x, y):
	    print '\n', 'No temperature sensor detected!', '\n'
	else:
            print 'Temperature:', float(pdu_check(x, y)[3]) / 10, float(pdu_check(x, y)[7]) / 10
    elif y == 'humi':
        if '-1' in pdu_check(x, y):
	    print '\n', 'No humidity sensor detected!', '\n'
	else:
	    #print pdu_check(x, y)
            print 'Humidity:', int(pdu_check(x, y)[3]), int(pdu_check(x, y)[7])
	    print (int(pdu_check(x, y)[3]))
    else:
        print '\n', 'Usage: pdu_monitor.py <ip> <[load],[temp],[humi]>', '\n'
