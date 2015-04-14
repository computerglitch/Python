#!/usr/bin/python

#########################################################
# This program finds the sizes of S3 buckets in a       #
# amazon aws account.                                   #
#                                                       #
# You must first have the aws command line interface    #
# installed and configured for this program to work     #
# properly. For more information see:                   #
#                                                       #
# http://docs.aws.amazon.com/cli/latest/userguide/      #
# cli-chap-getting-started.html                         #
#                                                       #
# Written by: Robbie Reese                              #
# Changes:                                              #
# v0.1      - 04/03/2015   - Inital Release             #
# v0.2      - 04/04/2015   - Clean column output        #
# v0.3      - 04/13/2015   - Cleaner output, total cost #
#########################################################

from __future__ import division
import sys
import subprocess
import string
import re

#The buckets we need to get the usage for - replace MyBucket# with your bucket names
s3buckets = [ "MyBucket1", "MyBucket2", "MyBucket3" ]

#Temporary list to store our results
tmpResults = []
for bucket in s3buckets:
    cmd = "aws s3api list-objects --bucket %s --output json --query '[sum(Contents[].Size)]'" %(bucket)
    ps1 = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    #Append the results to the temporary list
    out = tmpResults.append(ps1.communicate()[0])

#Cleanup our temporary list removing specific characters and spaces
tmpResults = [char.replace('[', '').replace(']', '').replace(' ', '').replace('\n', '') for char in tmpResults]

#Function to convert S3 usage output from s3api, to GB
def s3_convert(bucket):
   gb = int(bucket)/1024/1024/1024
   #Display the bucket usage in GB and limit to two decimal places
   size = format(gb,'.2f') 
   return size

#Create a new list with the clean gb sizes for each bucket
bucketsize = []
for data in tmpResults:
    sizes = bucketsize.append(s3_convert(data))

#Combine the two lists into a dictionary 
tmpDictionary = dict(zip(s3buckets, bucketsize))

#Get the values of the dictionary items, use the map function to convert the values to floats
values = map(float, tmpDictionary.values())

#Get the total of all bucket sizes and multiply it by the current cost of S3 storage fees
cost = sum(values)*.03

#Output the information in a grid readable format
data = zip(s3buckets, bucketsize)
#Set the column width based on the longest word - set a padding of 6 spaces between
col_width = max(len(word) for row in data for word in row) + 6
print "\n\033[93m\033[4mBucket Name\033[0m                \033[93m\033[4mBucket Size (GB)\033[0m"
for row in data:
    print "".join(word.ljust(col_width) for word in row)
print "\n"
print "\033[92mTotal S3 Cost (per month): $\033[1m%s \n\033[0m" %(cost)
