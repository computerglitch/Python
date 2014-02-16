#!/usr/bin/python

# Display help with ./AddMailAccount.py -h

import sys
import subprocess
import os
import argparse
import fileinput
import shutil

#Domains allowed to be managed by this server.
allowed_domains = [ 'domain.com', 'domain.net', 'domain.com', 'domain.com', 'domain.com' ]
#Define path to files we will manage.
vmailboxfile = "postfix/vmailbox"
dovecotfile = "dovecot/passwd"
imapsynclist = "ImapSyncUserList"
#Arguments that can be passed to this program.
parser = argparse.ArgumentParser(description="Manage accounts on the local mail server")
parser.add_argument('-e', '--email', metavar="EMAIL", help="User email address, must be used with -p to set the user password")
parser.add_argument('-p', '--password', metavar="PASSWORD", help="User email password, must be used with the -e option")
parser.add_argument('-d', '--delete', metavar="DELETE", help="Delete user from the mailserver (keep the mailbox)")
#Store all of the arguments.
args = parser.parse_args()

#Function to add the email address to the vmailboxfile in the proper postfix format.
def PostfixMbox(emailaddress):
    if emailaddress in open(vmailboxfile).read():
        print "\nThe mailbox " + emailaddress + " exists already!"
        print "Check the file: " + vmailboxfile + "\n"
        sys.exit()
    elif domain not in allowed_domains:
        print "\nThe domain " + domain + " is not configured on this mailserver!"
        print "Add " + domain + " to the postfix configuration before adding this email.\n"
        sys.exit()
    else:
        with open(vmailboxfile, "a") as file:
            file.write(emailaddress + "\t\t" + domain + "/" + name + "/" "\n")
        cmd = "postmap %s" %(vmailboxfile)
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]

#Function to add the email address and password to dovecot in the proper dovecot format.
def DovecotPasswd(password):
    cmd = "doveadm pw -s ssha -p %s" %(password)
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    if email in open(dovecotfile).read():
        print "\nThe mailbox " + email + " exists already!\n"
        print "Check the file: " + dovecotfile + "\n"
        sys.exit()
    elif domain not in allowed_domains:
        print "\nThe domain " + domain + " is not configured on this mailserver!"
        print "Add " + domain + " to the postfix configuration before adding this email.\n"
        sys.exit()
    else:
        with open(dovecotfile, "a") as file:
            file.write(email + ":" + output)

#Function to remove the account from the mail server, does not remove the mailbox.
def RemoveAccount(emailaddress):
     with open(imapsynclist) as oldfile, open(imapsynclist + '.tmp', 'w') as newfile:
         for line in oldfile:
             if not any(email in line for email in emailaddress):
                 newfile.write(line)
     shutil.move(imapsynclist + '.tmp', imapsynclist)
     with open(vmailboxfile) as oldfile, open(vmailboxfile + '.tmp', 'w') as newfile:
         for line in oldfile:
             if not any(email in line for email in emailaddress):
                 newfile.write(line)
     shutil.move(vmailboxfile + '.tmp', vmailboxfile)
     with open(dovecotfile) as oldfile, open(dovecotfile + '.tmp', 'w') as newfile:
         for line in oldfile:
             if not any(email in line for email in emailaddress):
                 newfile.write(line)
     shutil.move(dovecotfile + '.tmp', dovecotfile)

#Add the email address and password passed to the program to the email server.
if args.email != None and args.password != None:
    sep = "@"
    email = args.email
    dovecotpasswd = args.password 
    name = args.email.split(sep, 1)[0]
    domain =  args.email.split(sep, 1)[1]
    checkadd = raw_input("Are you sure you want to add " + email + " to the mailserver? [y/N] ")
    if checkadd.lower() == "y":
        print "\nCreating new user " + email 
        PostfixMbox(email)
        DovecotPasswd(dovecotpasswd)
        checkimapsync = raw_input("Is this an IMAP account that needs syncing between servers? [y/N] ")
        if checkimapsync.lower() == "y":
            with open(imapsynclist, "a") as file:
                file.write(email + "\n")
        print "Successfully added: " + email + " to the email server.\n"
    elif checkadd.lower() == "n":
        print "\nNot adding " + email + "\n"
        sys.exit()
#Remove the email address passed to the program from the email server.
elif args.delete != None:
    email_delete = [ args.delete ]
    if str(email_delete[0]) in open(imapsynclist).read() or str(email_delete[0]) in open(vmailboxfile).read():
        checksure = raw_input("Are you sure you want to remove the " + str(email_delete[0]) + " mail account? [y/N] ")
        if checksure.lower() == "y":
            RemoveAccount(email_delete)
            print str(email_delete[0]) + " mail account removed\n"
        elif checksure.lower() == "n":
            print "\nNot removing account!\n"
            sys.exit()
