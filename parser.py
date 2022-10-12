"""
parse BLE API from a csv file.
"""

from ast import Num
import os
import csv

cwd = os.getcwd()
readPath = cwd + '\\' +'BLEAPI'


class APIParser():
    def __init__(self):
        fin = open(readPath + '\\' + 'api.csv', 'r', errors='ignore')
        reader = csv.reader(fin)
        self.APIdic =  {row[0]:(row[1],row[2],row[3]) for row in reader}
    

    def getAPI(self, idx):
        if type(idx) != str:
            idx = str(idx)
        api = self.APIdic[idx][0]
        tp = self.APIdic[idx][1]
        name = self.APIdic[idx][2]
        return api,tp,name

    def getAPInum(self):
        num = len(self.APIdic)
        return num


