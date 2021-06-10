#!/usr/bin/env python
#
# Inject test data into Elastic Search
#

import json
import uuid
import sys

from http import client
from datetime import datetime, timedelta
from random import Random



def createBackupData(startDate, endDate, count):
    print(f'Creating test data between: {startDate}, {endDate} and {count} items')
    timespanInSeconds = (endDate - startDate).total_seconds()
    print(f'Timespan is: {timespanInSeconds}')
    randomGenerator = Random()
    headers = { "Content-Type": "application/json" }
    
    for item in range(1, count):
        print(f'Item: {item}')
        timedeltaSeconds = randomGenerator.random() * float(timespanInSeconds)
        timedeltaObject = timedelta(days=int(timedeltaSeconds / 86400), seconds=int(timedeltaSeconds % 86400))
        print(f'Adding timedelta: {timedeltaObject}')
        timestamp = startDate + timedeltaObject
        document = f'''
{{
  "occurence": "hourly",
  "replicas": [
    "us-west-2",
    "ap-southeast-1",
    "eu-west-1"
  ],
  "timestamp": "{timestamp}",
  "cloud": {{
    "availability_zone": "eu-north-1",
    "resident": "persistent"
  }}
}}'''
        print(f'Uploading document: {document}')
        httpConnection = client.HTTPConnection("localhost:9200")
        httpConnection.request("POST", "/backups/backup", document, headers)
        print(f'Got HTTP response: {httpConnection.getresponse().status}')
        httpConnection.close()
    

# If this is the main script being run from CLI then do stuff
if __name__ == '__main__':
    startDate = datetime.fromisoformat(sys.argv[1])
    endDate = datetime.fromisoformat(sys.argv[2])
    count = int(sys.argv[3])
    
    createBackupData(startDate, endDate, count)


    
  
