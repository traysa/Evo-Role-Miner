__author__ = 'Theresa'
'''
Parsing of TestData and Visualization
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy
import re
from optparse import OptionParser

# -----------------------------------------------------------------------------------
# Parse datasets from research (e.g. healthcare.rbc)
# -----------------------------------------------------------------------------------
def read(filename):
    print("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = max(list(map(int, re.findall('u_U(.+?)[\n\r\s]+', data))))+1
    print("userCount: "+str(userCount))

    # Count permissions
    permCount = max(list(map(int, re.findall('p_P(.+?)[\n\r\s]+', data))))+1
    print("permCount: "+str(permCount))

    # Create UP Matrix
    UPmatrix = [[0 for i in range(permCount)] for j in range(userCount)]
    for line in lines:
        if line.startswith("u_"):
            parts = line.split(" ")
            user = parts[0]
            userId = int(user[3:])
            for i in range(len(parts)-1):
                perm = parts[i+1]
                permId = int(perm[3:])
                #print(str(userId)+" , "+str(permId))
                UPmatrix[userId][permId] = 1
    print("DONE.\n")
    return UPmatrix

# -----------------------------------------------------------------------------------
# Parse datasets from datagenerator
# -----------------------------------------------------------------------------------
def read2(filename):
    print("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = len(lines)-1
    print("userCount: "+str(userCount))

    # Count permissions
    permCount = max(list(map(int, re.findall('Permission ([0-9]*)', data))))
    print("permCount: "+str(permCount))

    attrCount = len(lines[0].split(','))-permCount-1
    print("attrCount: "+str(attrCount))

    # Create UP Matrix
    matrix = [[0 for i in range(permCount+attrCount)] for j in range(userCount+1)]
    for line in lines[1:]:
        parts = line.split(",")
        userId = int(parts[0])
        for i in range(len(parts)-1):
            attr = parts[i+1]
            #print(str(userId)+" , "+str(attr))
            matrix[userId][i] = attr
    print("DONE.\n")
    return matrix,userCount,attrCount,permCount

def main():
    parser = OptionParser()
    parser.add_option("-i", dest="filename", default="..\\TestData\\healthcare.rbac",
         help="input file with UxP information", metavar="FILE")
    (options, args) = parser.parse_args()

    UPmatrix = numpy.matrix(read(options.filename))
    print(UPmatrix)