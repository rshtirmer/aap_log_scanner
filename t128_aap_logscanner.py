import sys
import requests
from datetime import datetime, timedelta
import argparse
import json
import os

day = timedelta(days=1)
def getTodayStr():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    return date

def getYesterdayStr():
    now = datetime.now() - day
    date = now.strftime("%Y-%m-%d")
    return date

def getDefaultPath():
    path = "/var/log/128technology/"
    fileName = "t128_aap.log"
    fullPath = path + fileName
    return fullPath

def remove_duplicates(l):
    return list(set(l))

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--startdate', nargs='?', default=getTodayStr(), type=str, help="Provide a start date, for example: 2019-06-13. \nDefaults to today's date")
    parser.add_argument('--enddate', nargs='?', default=getTodayStr(), type=str, help="Provide an end date, for example: 2019-06-13. \nDefaults to today's date")
    parser.add_argument('--file', nargs='?', default=getDefaultPath(), type=str, help="Provide a log file, for example: /var/log/128technology/t128_aap.log")
    parser.add_argument('--ap', nargs='?', type=str, help="Provide an access provider to filter by, for example: optimum")
    parser.add_argument('--event', nargs="?", type=str, help="Filter events by e6 or e7. If not set, no filtering by event is done.")
    parser.add_argument('--saltcall', action='store_true', help="Set this flag to run a salt call on gathered store numbers.")
    parser.add_argument('--force', action='store_true', help="Set this flag to autoagree to all user prompts.")
    args = parser.parse_args()
    return args

class logParser:
    def __init__(self, args):
        self.args = args

        self.startDate = datetime.strptime(self.args.startdate, "%Y-%m-%d")
        self.endDate = datetime.strptime(self.args.enddate, "%Y-%m-%d")

        self.patterns = ["Attempting to add config for stores", "Attempting to remove route filter for these stores"]

        self.logs = self.getAllMatches()
        self.filteredLogs = self.filterLogs()
        self.proccessedLogs = []

        if(self.args.event is None or self.args.event.lower() == "e6"):
            self.e6sn = self.getStoreNumbers(self.filteredLogs, self.patterns[0])
            self.e6sn = remove_duplicates(self.updateE6())
            print("**************************")
            print("{} Total Event 6 Stores").format(len(self.e6sn))
            print("**************************\n")
            self.proccessedLogs += self.proccessLog(self.e6sn)

        if(self.args.event is None or self.args.event.lower() == "e7"):
            self.e7sn = remove_duplicates(self.getStoreNumbers(self.filteredLogs, self.patterns[1]))
            print("**************************")
            print("{} Total Event 7 Stores").format(len(self.e7sn))
            print("**************************\n")
            self.proccessedLogs += self.proccessLog(self.e7sn)

        if(self.args.saltcall):
            numStore = []
            for data in self.proccessedLogs:
                numStore.append(int(data['StoreNumber']))
            self.satlCMD(numStore)

    def getAllMatches(self):
        contents = []

        with open("/var/log/128technology/t128_aap.1.log") as f:
            for line in f.readlines():
                for pattern in self.patterns:
                    if pattern in line:
                        contents.append(str(line))
        with open(self.args.file) as f:
            for line in f.readlines():
                for pattern in self.patterns:
                    if pattern in line:
                        contents.append(str(line))
        return contents

    def filterLogs(self):
        contents = []
        for line in self.logs:
            date = datetime.strptime(line[:10], "%Y-%m-%d")
            if self.startDate <= date <= self.endDate:
                contents.append(str(line))
        return contents

    def getStoreNumbers(self, log, pattern):
        contents = []
        for line in log:
            if pattern in line:
                vals = line[line.find("(")+1:line.find(")")]
                content = vals.split(",")

                for i in content:
                    try:
                        contents.append(int(i))
                    except: pass
        return contents

    def updateE6(self):
        contents = []
        e7FullStore = self.getStoreNumbers(self.logs, self.patterns[1])
        for i in self.e6sn:
            if i not in e7FullStore:
                contents.append(i)
        return contents

    def proccessLog(self, log):
        contents = []
        for num in log:
            data = self.apiCall(num)
            try:
                procData = json.loads(data)
                if self.args.ap is None:
                    print(data)
                    contents.append(procData)
                elif(self.args.ap.lower() in procData['AccessProvider'].lower()):
                    print(data)
                    contents.append(procData)
            except:
                print("ERROR on StoreNumber: " + str(num) + "\n")
        return contents

    def apiCall(self, storeNumber):
        host = "https://aap.attucs.com/api.php?uname=128t&storeNumber="
        host = host + str(storeNumber)
        try:
            r = requests.get(url = host)
            data = r.json()
            return data
        except:
            "ERROR Making API Call"

    def satlCMD(self, storeNumbers):
        saltCMD = "salt-call t128_aap.run_raw_template udp-transform-dia "
        numsToCall = ""
        for num in storeNumbers:
            numsToCall += str(num) + " "
        saltCMD += numsToCall
        print(saltCMD)
        if self.args.force:
            os.system(saltCMD)
        elif (raw_input("Run above command? (y/n): ").lower().strip()[:1] == "y"):
            os.system(saltCMD)

parseLogs = logParser(parseArgs())
