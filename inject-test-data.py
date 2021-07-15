#!/usr/bin/env python
#
# Inject test data into Elastic Search
#
# This injects millis and date.  It's possible that date in ElasticSearch is
# actually stored as millis anyway so this might be redundant
#
# TODO: Find out if it is redundant!
#

import json
import uuid
import sys

from http import client
from datetime import datetime, timedelta
from random import uniform
from math import floor


def addWiggleFactorToTimestamp(timestamp, gapInMinutes):
    print(f'Adding wiggle factor to "{timestamp}" with gap of "{gapInMinutes}"')
    wigglefactor = gapInMinutes * 0.25 * uniform(-1.0, 1.0)
    print(f'Wiggle factor is: {wigglefactor}')
    return timestamp + timedelta(minutes = wigglefactor)


def createBackupData(startDate, endDate, gapInMinutes):
    print(f'Creating test data between: {startDate}, {endDate} and {gapInMinutes} minutes between each')
    numberOfGaps = floor( (endDate - startDate).total_seconds() / (60 * gapInMinutes) )
    print(f'Number of {gapInMinutes} minute gaps is: {numberOfGaps}')
    headers = { "Content-Type": "application/json" }

    currentTimestamp = startDate
    timeIncrement = timedelta(minutes=gapInMinutes)    
        
    for item in range(1, numberOfGaps):
        print(f'Item: {item}')
        print(f'Adding timeIncrement: {timeIncrement}')
        currentTimestamp = currentTimestamp + timeIncrement
        timestamp = addWiggleFactorToTimestamp(currentTimestamp, gapInMinutes)
        timestampMillis = int(timestamp.timestamp()*1000)
        document = f'''
{{
  "occurence": "hourly",
  "replicas": [
    "us-west-2",
    "ap-southeast-1",
    "eu-west-1"
  ],
  "millis":"{timestampMillis}",
  "timestamp": "{timestamp.isoformat()}",
  "cloud": {{
    "availability_zone": "eu-north-1",
    "resident": "persistent"
  }}
}}'''
        print(f'Uploading document: {document}')
        httpConnection = client.HTTPConnection("localhost:9200")
        httpConnection.request("POST", "/backups/_doc", document, headers)
        print(f'Got HTTP response: {httpConnection.getresponse().status}')
        httpConnection.close()
    

# If this is the main script being run from CLI then do stuff
if __name__ == '__main__':
    startDate = datetime.fromisoformat(sys.argv[1])
    endDate = datetime.fromisoformat(sys.argv[2])
    gapInMinutes = int(sys.argv[3])
    
    createBackupData(startDate, endDate, gapInMinutes)


    
  
