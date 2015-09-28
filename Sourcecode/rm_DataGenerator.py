__author__ = 'Theresa'

import random
import os
import datetime

def generateUserInfo(userCnt, userTypeCnt, attributes):
    attributeCnt = len(attributes)
    userMatrix = [[(random.randint(1,attributes[i])) for i in range(attributeCnt)] for j in range(userTypeCnt)]
    while (len(userMatrix) < userCnt):
        userMatrix.append(userMatrix[random.randint(0,userTypeCnt-1)])
    return userMatrix

def applyRules(userInfo, rules):
    rulesCnt = len(rules)
    UPMatrix = [[0 for i in range(rulesCnt)] for j in range(userCnt)]
    for r,rule in enumerate(rules):
        for u,user in enumerate(userInfo):
            match = True
            for attr in range(len(rule)):
                if ((len(rule[attr]) != 0) and (user[attr] not in rule[attr])):
                    match = False
            if (match):
                UPMatrix[u][r] = 1
    return UPMatrix

def replaceRules(rules, ruleUsage, attributes):
    attributeCnt = len(attributes)
    for rule,i in enumerate(ruleUsage):
        if (i == 0):
            rules[rule] = [(random.sample(range(1,attributes[i]+1),random.randint(0,attributes[i]-1))) for i in range(attributeCnt)]
    return rules

def addNoise(UPmatrix, noise):
    for u,user in enumerate(UPMatrix):
        for p,permission in enumerate(user):
            r = random.random()
            if (r<=noise):
                UPMatrix[u][p] = int(not(bool(UPMatrix[u][p])))
    return UPMatrix

def printIntoFile(userInfo,UPMatrix, rules):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    directory = "..\\TestData\\Data_"+timestamp
    if not os.path.exists(directory):
        os.makedirs(directory)

    dataCSVfile = directory+"\\Data.csv"
    print("Write into CSV file "+str(dataCSVfile)+"...")
    if not os.path.exists(dataCSVfile):
        with open(dataCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("User;")
            for attr in range(0,len(userInfo[0])):
                 outfile.write("Attribute"+str(attr+1)+";")
            for p in range(0,len(UPMatrix[0])):
                 outfile.write("Permission"+str(p+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(dataCSVfile, "a") as outfile:
        for u,user in enumerate(userInfo):
            outfile.write(str(u+1)+";")
            for attr in range(0,len(userInfo[0])):
                 outfile.write(str(userInfo[u][attr])+";")
            for p in range(0,len(UPMatrix[0])):
                 outfile.write(str(UPMatrix[u][p])+";")
            outfile.write("\n")
        outfile.close()
    print("DONE.\n")

    resultCSVfile = directory+"\\Results.csv"
    print("Write into CSV file "+str(resultCSVfile)+"...")
    if not os.path.exists(resultCSVfile):
        with open(resultCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("Permission;")
            for attr in range(0,len(userInfo[0])):
                 outfile.write("Attribute"+str(attr+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(resultCSVfile, "a") as outfile:
        for r,rule in enumerate(rules):
            outfile.write(str(r+1)+";")
            for attr in range(0,len(rules[0])):
                tmp = ""
                for v in rules[r][attr]:
                    tmp += str(v)+","
                outfile.write(str(tmp[:-1])+";")
            outfile.write("\n")
        outfile.close()
    print("DONE.\n")

attributes = [3,3,2]
userCnt = 10
userTypeCnt = 5
permissionCnt = 20
noise = 0.05

userInfo = generateUserInfo(userCnt,userTypeCnt,attributes)
print("USERINFO: "+str(userInfo))

rules = [[0 for i in range(len(attributes))] for i in range(permissionCnt)]
ruleUsage = [0 for i in range(permissionCnt)]
while (0 in ruleUsage):
    rules = replaceRules(rules, ruleUsage, attributes)
    UPMatrix = applyRules(userInfo,rules)
    ruleUsage = [ sum(x) for x in zip(*UPMatrix)]
print("RULES: "+str(rules))
print("UPMATRIX: "+str(UPMatrix))
UPMatrix = addNoise(UPMatrix, noise)
print("UPMATRIX: "+str(UPMatrix))

printIntoFile(userInfo,UPMatrix, rules)