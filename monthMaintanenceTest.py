import os
import random
from datetime import datetime, timedelta, date
import calendar
import ast
import requests
import json
import time
import yaml


def calculateDaysInMonth():
    """
    Get the number of days in the current month.
    """
    global year, month
    today = date.today()
    month = today.month
    year = today.year
    numberOfDaysInMonth = calendar.monthrange(year, month)[1]
    return numberOfDaysInMonth

def convertInventoryFileToRandomlist(inventoryFilePath):
    """
    Convert the content of an inventory file into a list of strings.
    Args:
        inventoryFilePath (str): Path to the inventory file.
    Returns:
        list: A list of strings parsed from the inventory file content.
    """
    with open(inventoryFilePath, 'r') as file:
        fileContent = file.read().strip()

    fileContent = fileContent.replace('\n', '').replace(' ', '').split(',')
    # random.shuffle(fileContent)
    return fileContent

def insertNodesToDict(numberOfDaysInMonth, randomNodeList):
    nodesDict = {dayNumber: [] for dayNumber in range(1, numberOfDaysInMonth + 1)}
    randomNodeListLen = len(randomNodeList)
    batchSize = int(randomNodeListLen / numberOfDaysInMonth)
    restOfBatchSize = randomNodeListLen % numberOfDaysInMonth
    batchSizeDifference = 0
    nodeListIter = iter(randomNodeList)

    for key in nodesDict.keys():
        batchSizeDifference = 1 if key <= restOfBatchSize else 0
        nodeBatch = [next(nodeListIter) for node in range(batchSize + batchSizeDifference)]
        batchSizeDifference = 0
        nodesDict[key] += nodeBatch

    return nodesDict

def convertBeginTimeToUnixTimestemp(jobBeginTime):
    """
    Convert a job start time from a string to a Unix timestamp.

    Args:
        jobBeginTime (str): The job start time in the format "%d.%m.%Y-%H:%M:%S".

    Returns:
        int: The Unix timestamp corresponding to the provided job start time.
    """
    date_format = "%d.%m.%Y-%H:%M:%S"
    dt = (datetime.strptime(jobBeginTime, date_format)) - timedelta(hours=3)
    unix_timestamp = int(time.mktime(dt.timetuple()))
    return unix_timestamp

def sendJobSubmissionRequest(requiredNode, jobBeginTime):
    """
    Submit a batch job to a Slurm REST API.

    Args:
        requiredNode (str): node that the slurm job will be run on.
        jobBeginTime (str): The job start time in the format "%d.%m.%Y-%H:%M:%S".

    Raises:
        ValueError: If the SLURM_REST_API_TOKEN environment variable is not set.
    """
    url = f"http://{os.environ['slurmIP']}:{os.environ['slurmPort']}/slurm/{os.environ['slurmCorrentVersion']}/job/submit"

    headers = {
        'X-SLURM-USER-NAME': os.environ['slurmUser'],
        'X-SLURM-USER-TOKEN': os.environ['SLURM_REST_API_TOKEN'],
        'Content-Type': 'application/json'
    }
    payload = {
        'job': {
            'script': f"#!/bin/bash\n {os.environ['nodeWorkingDir']}/slurmBatchJob.sh",
            'current_working_directory': os.environ['nodeWorkingDir'],
            'begin_time': convertBeginTimeToUnixTimestemp(jobBeginTime),
            'required_nodes': requiredNode,
            'environment': {
                'elasticPassword': f"{os.environ['elasticPassword']}",
                'elasticIP': f"{os.environ['elasticIP']}",
                'elasticPort': f"{os.environ['elasticPort']}",
                'elasticNewIndexName': f"{os.environ['elasticNewIndexName']}",
                'elasticUser': f"{os.environ['elasticUser']}"
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.ok:
        jobID = response.json().get('result', {}).get('job_id')
        print(f"Job submitted, JOBID: {jobID}, NODE: {requiredNode}, DATE: {jobBeginTime}")
    else:
        raise Exception(f"Error: {response.status_code}, NODE: {requiredNode} - {response.text}")

def submitBatchJobsToNodes(nodesDict):
    """
    Parse a dictionary of nodes and submit batch jobs for each entry.

    Args:
        nodesDict (dict): A dictionary where the keys are dates and the values are lists of node counts.
    """
    for day, nodesList in nodesDict.items():
        for requiredNode in nodesList:
            sendJobSubmissionRequest(requiredNode, f"{day}.{month}.{year}-05:00:00")

def main():
    inventoryFilePath = 'inventoryFile.txt'
    numberOfDaysInMonth = calculateDaysInMonth()
    randomNodeList = convertInventoryFileToRandomlist(inventoryFilePath)
    nodesDict = insertNodesToDict(numberOfDaysInMonth, randomNodeList)
    submitBatchJobsToNodes(nodesDict)

if __name__ == "__main__":
    main()