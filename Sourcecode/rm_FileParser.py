__author__ = 'Theresa'
'''
Parsing of TestData and Visualization
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy
import re
from optparse import OptionParser
import MatrixOperators as matrixOps
import logging
logger = logging.getLogger('root')

# -----------------------------------------------------------------------------------
# Parse datasets from research (e.g. healthcare.rbac)
# -----------------------------------------------------------------------------------
def read(filename):
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = max(list(map(int, re.findall('u_U(.+?)[\n\r\s]+', data))))+1
    logger.info("userCount: "+str(userCount))

    # Count permissions
    permCount = max(list(map(int, re.findall('p_P(.+?)[\n\r\s]+', data))))+1
    logger.info("permCount: "+str(permCount))

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
    logger.info("DONE.\n")
    return UPmatrix

# -----------------------------------------------------------------------------------
# Parse datasets from research (e.g. domino.rbac)
# -----------------------------------------------------------------------------------
def read2(filename):
    logger.info("Read2")
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = max(list(map(int, re.findall('u_U(.+?)[\n\r\s]+', data))))#+1
    logger.info("userCount: "+str(userCount))

    # Count permissions
    permCount = max(list(map(int, re.findall('p_P(.+?)[\n\r\s]+', data))))#+1
    logger.info("permCount: "+str(permCount))

    # Create UP Matrix
    UPmatrix = [[0 for i in range(permCount)] for j in range(userCount)]
    for line in lines:
        if line.startswith("u_"):
            parts = line.split(" ")
            user = parts[0]
            userId = int(user[3:])-1
            for i in range(len(parts)-1):
                perm = parts[i+1]
                permId = int(perm[3:])-1
                #print(str(userId)+" , "+str(permId))
                UPmatrix[userId][permId] = 1
    logger.info("DONE.\n")
    return UPmatrix

# -----------------------------------------------------------------------------------
# Parse datasets from research (e.g. firewall-1.rbac)
# -----------------------------------------------------------------------------------
def read4(filename):
    logger.info("Read4")
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = max(list(map(int, re.findall('u_U(.+?)[\n\r\s]+', data))))#+1
    logger.info("userCount: "+str(userCount))

    # Count permissions
    permCount = max(list(map(int, re.findall('p_P(.+?)[\n\r\s]+', data))))+1
    logger.info("permCount: "+str(permCount))

    # Create UP Matrix
    UPmatrix = [[0 for i in range(permCount)] for j in range(userCount)]
    for line in lines:
        if line.startswith("u_"):
            parts = line.split(" ")
            user = parts[0]
            userId = int(user[3:])-1
            for i in range(len(parts)-1):
                perm = parts[i+1]
                permId = int(perm[3:])
                #print(str(userId)+" , "+str(permId))
                UPmatrix[userId][permId] = 1
    logger.info("DONE.\n")
    return UPmatrix

# -----------------------------------------------------------------------------------
# Parse datasets from datagenerator
# -----------------------------------------------------------------------------------
def read3(filename):
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = len(lines)-1
    logger.info("userCount: "+str(userCount))

    # Count permissions
    permCount = max(list(map(int, re.findall('Permission ([0-9]*)', data))))
    logger.info("permCount: "+str(permCount))

    attrCount = len(lines[0].split(','))-permCount-1
    logger.info("attrCount: "+str(attrCount))

    # Create UP Matrix
    matrix = [[0 for i in range(permCount+attrCount)] for j in range(userCount+1)]
    for line in lines[1:]:
        parts = line.split(",")
        userId = int(parts[0])
        for i in range(len(parts)-1):
            attr = parts[i+1]
            #logger.debug(str(userId)+" , "+str(attr))
            matrix[userId][i] = attr
    logger.info("DONE.\n")
    return matrix,userCount,attrCount,permCount

# -----------------------------------------------------------------------------------
# Parse userAttributes from datagenerator
# -----------------------------------------------------------------------------------
def readUserAttributes(filename):
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = len(lines)-2
    logger.info("userCount: "+str(userCount))

    # Count attributes
    attributesCount = max(list(map(int, re.findall('Attribute(.+?);', data))))
    logger.info("attributesCount: "+str(attributesCount))
    userAttributes = []
    for a in range(0,attributesCount):
        userAttributes.append(set())

    userAttributeValues = []
    for line in lines[2:]:
        parts = line.split(";")
        userId = int(parts[0])
        attributeValues = []
        for i in range(0,attributesCount):
            value = parts[i+1]
            attributeValues.append(value)
            userAttributes[i].add(value)
        userAttributeValues.append(attributeValues)

    userAttributeValues_normalized, userAttributes_normalized = normalizeAttributeValues(userAttributes,userAttributeValues)
    logger.info("DONE.\n")
    return userAttributeValues_normalized, userAttributes_normalized

def normalizeAttributeValues(userAttributes,userAttributeValues):
    userAttributeValues_normalized = userAttributeValues
    for user in userAttributeValues_normalized:
        for a,attr in enumerate(user):
            user[a]=list(userAttributes[a]).index(attr)

    userAttributes_normalized = [[] for a in range(0,len(userAttributes))]
    for a in range(0,len(userAttributes)):
        userAttributes_normalized[a] = list(range(0, len(userAttributes[a])))

    return userAttributeValues_normalized, userAttributes_normalized

# -----------------------------------------------------------------------------------
# Parse userAttributes from research (e.g. healthcare_20_cust.attr)
# -----------------------------------------------------------------------------------
def readUserAttributes2(filename,userCount):
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    data = data.split("=")[1]

    # Count attributes
    attributes = data.split(",")
    attributesCount = int(len(attributes)/userCount)
    logger.info("attributesCount: "+str(attributesCount))

    userAttributeValues = []
    for user in range(0,userCount):
        attributeValues = attributes[user*attributesCount:user*attributesCount+attributesCount]
        userAttributeValues.append(attributeValues)

    logger.info("DONE.\n")
    return userAttributeValues
# -----------------------------------------------------------------------------------
# Parse constraints
# -----------------------------------------------------------------------------------
def readConstraints(filename):
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count constraints
    constraintCount = len(lines)
    logger.info("constraintCount: "+str(constraintCount))

    constraints = []
    for line in lines:
        parts = [int(c) for c in line.split(";")]
        if len(parts) > 2:
            raise ValueError("Constraint '"+str(line)+"' is not valid")
        constraints.append(parts)

    return constraints

# -----------------------------------------------------------------------------------
# Parse User-Role Assignments
# -----------------------------------------------------------------------------------
def readURAssignments(filename):
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count constraints
    roleCnt = len(lines[2:])
    logger.info("role count: "+str(roleCnt))

    users = []
    for line in lines[2:]:
        parts = line.split(";")
        users += [int(user) for user in parts[1].split(",")]
    userCnt = max(users)
    logger.info("user count: "+str(userCnt))

    URMatrix = matrixOps.createEmptyMatrix(userCnt, roleCnt)
    for line in lines[2:]:
        parts = line.split(";")
        role = int(parts[0])-1
        userList = [int(user)-1 for user in parts[1].split(",")]
        for user in userList:
            URMatrix[user][role]=1

    return URMatrix

# -----------------------------------------------------------------------------------
# Parse URMatrix from file
# -----------------------------------------------------------------------------------
def readURMatrix(filename):
    logger.info("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCnt = len(lines[2:])
    print("user count: "+str(userCnt))

    roleCnt = len(lines[2:][0].split(";")[1:])-1
    print("role count: "+str(roleCnt))

    URMatrix = matrixOps.createEmptyMatrix(userCnt, roleCnt)
    for user,u in enumerate(lines[2:]):
        roles = u.split(";")[1:len(u.split(";"))-1]
        for role,r in enumerate(roles):
            URMatrix[user][role]=int(r)

    return URMatrix

# -----------------------------------------------------------------------------------
# Parse Role-Permission Assignments
# -----------------------------------------------------------------------------------
def readRPAssignments(filename):
    print("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count constraints
    roleCnt = len(lines[2:])
    print("role count: "+str(roleCnt))

    permissions = []
    for line in lines[2:]:
        parts = line.split(";")
        permissions += [int(permission) for permission in parts[1].split(",")]
    permissionCnt = max(permissions)+1
    print("permission count: "+str(permissionCnt))

    RPMatrix = matrixOps.createEmptyMatrix(roleCnt, permissionCnt)
    for line in lines[2:]:
        parts = line.split(";")
        role = int(parts[0])-1
        permissionList = [int(permission) for permission in parts[1].split(",")]
        for permission in permissionList:
            RPMatrix[role][permission]=1

    return RPMatrix

# -----------------------------------------------------------------------------------
# Parse RPMatrix from file
# -----------------------------------------------------------------------------------
def readRPMatrix(filename):
    print("Parsing file "+str(filename)+"... ")
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count constraints
    roleCnt = len(lines[2:])
    print("role count: "+str(roleCnt))

    permissionCnt = len(lines[1].split(";"))-2
    print("permission count: "+str(permissionCnt))

    RPMatrix = []
    for line in lines[2:]:
        parts = line.split(";")
        role = int(parts[0])-1
        permissionList = [int(permission) for permission in parts[1:-1]]
        RPMatrix.append(permissionList)
    return RPMatrix

def main():
    parser = OptionParser()
    parser.add_option("-i", dest="filename", default="..\\TestData\\healthcare.rbac",
         help="input file with UxP information", metavar="FILE")
    (options, args) = parser.parse_args()

    UPmatrix = numpy.matrix(read(options.filename))
    print(UPmatrix)