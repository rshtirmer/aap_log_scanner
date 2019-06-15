import sys
import os
import requests
from datetime import datetime, timedelta
import argparse
import json

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--startdate', nargs='?', default=getTodayStr(), type=str, help="Provide a start date, for example: 2019-06-13. \nDefaults to today's date")
    parser.add_argument('--enddate', nargs='?', default=getTodayStr(), type=str, help="Provide an end date, for example: 2019-06-13. \nDefaults to today's date")
    parser.add_argument('--ap', nargs='?', type=str, help="Provide an access provider to filter by, for example: optimum")
    parser.add_argument('--saltcall', action='store_true', help="Set this flag to run a salt call on gathered store numbers.")
    parser.add_argument('--force', action='store_true', help="Set this flag to autoagree to all user prompts.")
    parser.add_argument('--e6', action='store_true', help="Set this flag to filter by E6 stores.")
    parser.add_argument('--e7', action='store_true', help="Set this flag to filter by E7 stores.")
    parser.add_argument('--getstore', nargs='?', type=str, help="Prove a StoreNumber to retrieve.")
    args = parser.parse_args()
    return args

files = ["t128_aap.1.log", "t128_aap.log"]
patterns = ["Attempting to add config for stores", "Attempting to remove route filter for these stores"]

def getPath(fileName):
    path = "/var/log/128technology/"
    fullPath = path + fileName
    return fullPath

def getTodayStr():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    return date

def sortByDate(log):
    ordered_data = sorted(log.items(), key = lambda x:datetime.strptime(x[1], '%Y-%m-%d'), reverse=False)
    return ordered_data

def apiCall(storeNumber):
    host = "https://aap.attucs.com/api.php?uname=128t&storeNumber="
    host = host + str(storeNumber)
    try:
        r = requests.get(url = host)
        data = r.json()
        return data
    except:
        "ERROR Making API Call"

def openFiles():
    logs = []
    for file in files:
        path = getPath(file)
        with open(path) as f:
            for line in f.readlines():
                logs.append(str(line))
    return logs

def filterByDate(fullLog, startDate, endDate):
    startDate = datetime.strptime(startDate, "%Y-%m-%d")
    endDate = datetime.strptime(endDate, "%Y-%m-%d")
    logs = []
    for line in fullLog:
        try:
            date = datetime.strptime(line[:10], "%Y-%m-%d")
            if startDate <= date <= endDate:
                logs.append(str(line))
        except:
            pass
    return logs

def getMatches(log, pattern):
    logs = []
    for line in log:
        if pattern in line:
            logs.append(line)
    return logs

def getStoreNumbers(line):
    vals = line[line.find("(")+1:line.find(")")]
    content = vals.split(",")

    storeNumbers = []

    for num in content:
        num = num.strip('\'"')
        try:
            int(num)
            storeNumber = str(num).replace(' ','')
            storeNumbers.append(storeNumber)
        except:
            pass
    return storeNumbers

def getAllStoreNumbersByDate(log):
    logs = {}
    for line in log:
        storeNumbers = getStoreNumbers(line)
        date = line[:10]
        for storeNumber in storeNumbers:
            if storeNumber not in logs.keys():
                logs[storeNumber] = date
            else:
                oldDate = logs[storeNumber]
                oldDate = datetime.strptime(oldDate, "%Y-%m-%d")
                currentDate = datetime.strptime(date, "%Y-%m-%d")
                if(currentDate > oldDate):
                    logs[storeNumber] = date
    return logs

def updateE6(e6, e7):
    log = e6
    for storeNumber in log.keys():
        if storeNumber in e7.keys():
            log.pop(storeNumber, None)
    return log

def proccessLog(log, ap):
    dataLog = []
    previousDate = None
    for pair in log:
        storeNumber = pair[0]
        date = pair[1]

        data = apiCall(storeNumber)
        procData = json.loads(data)

        if (ap is None or ap.lower() in procData['AccessProvider'].lower()):
            dataLog.append(procData)

            if(date != previousDate):
                print("{}: \n").format(date)
                previousDate = date

            #AAPCA0719P1
            routerName = "AAP" + str(procData['State']) + str(procData['StoreNumber']) + "P" + str(procData['Pod'])
            print(routerName)
            print("Store Number: {}\n\t Access Provider: {}\n\t Pod: {}\n\t State: {}\n\t LannerSN-A: {}\n\t LannerSN-B: {}\n").format(procData['StoreNumber'], procData['AccessProvider'], procData['Pod'], procData['State'], procData['LannerSN-A'], procData['LannerSN-B'])

    return dataLog

def saltCall(procLog, force):
    saltCMD = "salt-call t128_aap.run_raw_template udp-transform-dia "
    numsToCall = ""

    for data in procLog:
        numsToCall += str(int(data['StoreNumber'])) + " "

    saltCMD += numsToCall

    print("Preparing to run the following bash script\n{}").format(saltCMD)
    if force:
        os.system(saltCMD)
    elif (raw_input("Run above command? (y/n): ").lower().strip()[:1] == "y"):
        os.system(saltCMD)

def buildOutput(args, e6, e7):
    outputLog = []

    if(args.getstore is not None):
        try:
            data = apiCall(args.getstore)
            procData = json.loads(data)
            print("\nStore Number: {}\n\t Access Provider: {}\n\t Pod: {}\n\t State: {}\n\t LannerSN-A: {}\n\t LannerSN-B: {}\n").format(procData['StoreNumber'], procData['AccessProvider'], procData['Pod'], procData['State'], procData['LannerSN-A'], procData['LannerSN-B'])
        except Exception as e:
            print("\nFailed to get StoreNumber!\nError: \n\t{}\n").format(e)

    if(not args.e6):
        print("*"*20)
        print("{} Total E6 Stores").format(len(e6))
        print("*"*20 + "\n")
        outputLog += proccessLog(e6, args.ap)

    if(not args.e7):
        print("*"*20)
        print("{} Total E7 Stores").format(len(e7))
        print("*"*20 + "\n")
        outputLog += proccessLog(e7, args.ap)

    if(args.saltcall):
        saltCall(outputLog, args.force)

def main():
    args = parseArgs()

    fullLog = openFiles()
    filteredLog = filterByDate(fullLog, args.startdate, args.enddate)

    e6FilteredLog = getMatches(filteredLog, patterns[0])
    e7FilteredLog = getMatches(filteredLog, patterns[1])
    e7FullLog = getMatches(fullLog, patterns[1])

    e7FullSN = getAllStoreNumbersByDate(e7FullLog)
    e6FilteredSN = getAllStoreNumbersByDate(e6FilteredLog)
    e7FilteredSN = sortByDate(getAllStoreNumbersByDate(e7FilteredLog))

    e6FilteredSN = sortByDate(updateE6(e6FilteredSN, e7FullSN))

    buildOutput(args, e6FilteredSN, e7FilteredSN)

if __name__== "__main__":
  main()
