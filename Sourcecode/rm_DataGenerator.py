__author__ = 'Theresa'

import random
import os
import datetime
import rm_Visualization as visual
import numpy


def drawFromBucket(permissionBucket, items):
    permissions = set()
    for i in range(items):
        permission = random.randint(0,len(permissionBucket)-1)
        #print("permission: "+str(permission))
        permissions.add(permissionBucket.pop(permission))
        #print("permissions: "+str(permissions))
        #print("tempPermissionBucket: "+str(permissionBucket))
    return permissionBucket, permissions

def generateRoles(roleCnt,permissionCnt,maxPermissionForRole, maxPermissionUsage):
    roles = [{} for r in range(roleCnt)]
    #print("roles: "+str(roles))
    permissionBucket = [p for p in range(permissionCnt) for c in range(maxPermissionUsage)]
    #print("permissionBucket: "+str(permissionBucket))
    for r in range(len(roles)):
        permissionForRoleCnt = random.randint(1,maxPermissionForRole)
        #print("permissionForRoleCnt: "+str(permissionForRoleCnt))
        tempPermissionBucket = [i for i in permissionBucket if not i in roles[r] or roles[r].remove(i)]
        #print("tempPermissionBucket: "+str(tempPermissionBucket))
        if (len(tempPermissionBucket) > 0):
            permissionBucket, permissions = drawFromBucket(tempPermissionBucket,permissionForRoleCnt)
            roles[r] = permissions
            #print("role: "+str(roles[r]))
        else:
            raise ValueError("An error occured")
    #print("roles: "+str(roles))
    return roles

def generateRoles2(roleCnt,permissionCnt,maxPermissionForRole, maxPermissionUsage):
    roles = [set() for r in range(roleCnt)]
    #print("roles: "+str(roles))
    permissionUsage = [0 for p in range(permissionCnt)]
    #print("permissionUsage: "+str(permissionUsage))
    permissionBucket = [p for p in range(permissionCnt) for c in range(maxPermissionUsage)]
    #print("permissionBucket: "+str(permissionBucket))
    emptySlotsinRole = [maxPermissionForRole for r in range(roleCnt)]
    while (0 in permissionUsage and  sum(emptySlotsinRole) != 0):
        openPermissions = [p for p in range(permissionCnt) if permissionUsage[p]<=maxPermissionUsage]
        #print("openPermissions: "+str(openPermissions))
        selectedPermission = random.sample(permissionBucket,1)[0]
        #print("permission: "+str(selectedPermission))
        openRoles = [r for r in range(roleCnt) if not emptySlotsinRole[r]==0]
        #print("openRoles: "+str(openRoles))
        selectedRole = random.sample(openRoles,1)[0]
        #print("selectedRole: "+str(selectedRole))
        roles[selectedRole].add(selectedPermission)
        permissionUsage[selectedPermission] += 1
        #print("permissionUsage: "+str(permissionUsage))
        emptySlotsinRole[selectedRole] -= 1
        #print("emptySlotsinRole: "+str(emptySlotsinRole))
    return roles

def generateRoles3(roleCnt,permissionCnt,maxPermissionForRole, maxPermissionUsage, RPdensity):
    roles = [set() for r in range(roleCnt)]
    #print("roles: "+str(roles))
    permissionUsage = [0 for p in range(permissionCnt)]
    #print("permissionUsage: "+str(permissionUsage))
    permissionBucket = [p for p in range(permissionCnt) for c in range(maxPermissionUsage)]
    #print("permissionBucket: "+str(permissionBucket))
    emptySlotsinRole = [maxPermissionForRole for r in range(roleCnt)]
    density = 0.0
    assignments = 0
    while (0 in permissionUsage and sum(emptySlotsinRole) != 0 and density < RPdensity):
        openPermissions = [p for p in range(permissionCnt) if permissionUsage[p]<=maxPermissionUsage]
        #print("openPermissions: "+str(openPermissions))
        selectedPermission = random.sample(permissionBucket,1)[0]
        #print("permission: "+str(selectedPermission))
        openRoles = [r for r in range(roleCnt) if not emptySlotsinRole[r]==0]
        #print("openRoles: "+str(openRoles))
        selectedRole = random.sample(openRoles,1)[0]
        #print("selectedRole: "+str(selectedRole))
        roles[selectedRole].add(selectedPermission)
        assignments += 1
        permissionUsage[selectedPermission] += 1
        #print("permissionUsage: "+str(permissionUsage))
        emptySlotsinRole[selectedRole] -= 1
        #print("emptySlotsinRole: "+str(emptySlotsinRole))
        density = assignments/(roleCnt * permissionCnt)
        print("density: "+str(density))
    return roles

def generateUsers(userCnt,attributes,userTypeCnt):
    userTypes = [[[] for a in range(len(attributes))] for u in range(userTypeCnt)]
    #("users: "+str(users))
    for u in range(userTypeCnt):
        for a,attrValues in enumerate(attributes):
            userTypes[u][a] = attrValues[random.randint(0,len(attrValues)-1)]
    #print("users: "+str(users))
    users = userTypes
    while (len(users) < userCnt):
        users.append(random.sample(userTypes,1)[0])
    return users

def generateRules(rules,roleCnt,attributes,maxRuleConditionCnt,ruleUsage):
    #rules = [[] for r in range(roleCnt)]
    #print("rules: "+str(rules))
    for r,usage in enumerate(ruleUsage):
        if (usage == 0):
            selectedAttributes = random.sample(range(0,len(attributes)),random.randint(1,maxRuleConditionCnt))
            #print("selectedAttributes: "+str(selectedAttributes))
            attrSet = []
            for a in range(len(attributes)):
                attrValueSet = []
                if (a in selectedAttributes):
                    attrValues = attributes[a]
                    numberOfValues = random.randint(1,len(attrValues)-1)
                    attrValueSet = random.sample(attrValues,numberOfValues)
                attrSet.append(attrValueSet)
            #print("attrSet: "+str(attrSet))
            rules[r] = attrSet
    #print("rules: "+str(rules))
    return rules

def assignUsersToRoles(users, roles, rules):
    rolesCnt = len(roles)
    userCnt = len(users)
    URMatrix = [[0 for r in range(rolesCnt)] for u in range(userCnt)]
    for r,rule in enumerate(rules):
        #print("rule: "+str(rule))
        for u,user in enumerate(users):
            #print("user: "+str(user))
            match = True
            for attr in range(len(rule)):
                if ((len(rule[attr]) != 0) and (user[attr] not in rule[attr])):
                    match = False
            if (match):
                #print("match")
                URMatrix[u][r] = 1
    return URMatrix

def assignRolesToPermissions(roles, permissionCnt):
    rolesCnt = len(roles)
    RPMatrix = [[0 for p in range(permissionCnt)] for r in range(rolesCnt)]
    for r,role in enumerate(roles):
        for p in role:
            RPMatrix[r][p] = 1
    return RPMatrix

def addNoise(UPmatrix, noise):
    for u,user in enumerate(UPMatrix):
        for p,permission in enumerate(user):
            r = random.random()
            if (r<=noise):
                UPMatrix[u][p] = int(not(bool(UPMatrix[u][p])))
    return UPMatrix

def printDataIntoFiles(directory, users, roles, UPMatrix, rules):
    if not os.path.exists(directory):
        os.makedirs(directory)

    usersCSVfile = directory+"\\Users.csv"
    print("Write into CSV file "+str(usersCSVfile)+"...")
    if not os.path.exists(usersCSVfile):
        with open(usersCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("User;")
            for attr in range(0,len(users[0])):
                 outfile.write("Attribute"+str(attr+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(usersCSVfile, "a") as outfile:
        for u,user in enumerate(users):
            outfile.write(str(u+1)+";")
            for attr in range(0,len(users[0])):
                 outfile.write(str(users[u][attr])+";")
            outfile.write("\n")
        outfile.close()
    print("DONE.\n")

    upmatrixCSVfile = directory+"\\UPMatrix.csv"
    print("Write into CSV file "+str(upmatrixCSVfile)+"...")
    if not os.path.exists(upmatrixCSVfile):
        with open(upmatrixCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("User;")
            for p in range(0,UPMatrix.shape[1]):
                 outfile.write("Permission"+str(p+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(upmatrixCSVfile, "a") as outfile:
        for u,user in enumerate(users):
            outfile.write(str(u+1)+";")
            for p in range(0,UPMatrix.shape[1]):
                 outfile.write(str(UPMatrix[u,p])+";")
            outfile.write("\n")
        outfile.close()
    print("DONE.\n")

    rulesCSVfile = directory+"\\Rules.csv"
    print("Write into CSV file "+str(rulesCSVfile)+"...")
    if not os.path.exists(rulesCSVfile):
        with open(rulesCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("Role;")
            for attr in range(0,len(users[0])):
                 outfile.write("Attribute"+str(attr+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(rulesCSVfile, "a") as outfile:
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

    rolesCSVfile = directory+"\\Roles.csv"
    print("Write into CSV file "+str(rolesCSVfile)+"...")
    if not os.path.exists(rolesCSVfile):
        with open(rolesCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("Role;Permissions")
            outfile.write("\n")
            outfile.close()
    with open(rolesCSVfile, "a") as outfile:
        for r,role in enumerate(roles):
            outfile.write(str(r+1)+";")
            tmp = ""
            for p in role:
                tmp += str(p)+","
            tmp = tmp[:-1]
            outfile.write(tmp+";\n")
        outfile.close()
    print("DONE.\n")

    testdataFile = directory+"\\testdata.rbac"
    print("Write into RBAC file "+str(testdataFile)+"...")
    if not os.path.exists(testdataFile):
        with open(testdataFile, "a") as outfile:
            outfile.write("# Automatically generated data\n")
            outfile.write("# Users: "+str(UPMatrix.shape[0])+"\n")
            outfile.write("# Permissions: "+str(UPMatrix.shape[1])+"\n")
            outfile.write("# UserPermissionAssignments: "+str(UPMatrix.sum())+"\n")
            outfile.write("\n")
            for u,user in enumerate(UPMatrix):
                tmp = "u_U"+str(u)
                for p in range(0,UPMatrix.shape[1]):
                    if (UPMatrix[u,p]==1):
                        tmp += " p_P"+str(p)
                outfile.write(tmp+"\n")
            outfile.close()

attributes = [['Sales','Motor','Administration'],['Denmark','Germany','US'],['Internal','External']]
#attributes = [[['Sales',.4],['Motor',.4],['Administration',.2]],[['Denmark',.6],['Germany',.3],['US',.1]],[['Internal',.85],['External',.15]]]

userCnt = 46
userTypeCnt = 5
roleCnt = 18
permissionCnt = 46
noise = 0.05
maxPermissionForRole = 46
maxPermissionUsage = 3
maxRuleConditionCnt = 3
RPdensity = 0.2
UPdensity = 0.2

roles = generateRoles3(roleCnt,permissionCnt,maxPermissionForRole, maxPermissionUsage, RPdensity)
print("\nROLES:")
for r in roles:
    print(r)

users = generateUsers(userCnt,attributes,userTypeCnt)
print("\nUSERS:")
for u in users:
    print(u)

rules = [[] for r in range(roleCnt)]
ruleUsage = [0 for i in range(roleCnt)]
while (0 in ruleUsage):
    rules = generateRules(rules,roleCnt,attributes,maxRuleConditionCnt,ruleUsage)
    URMatrix = assignUsersToRoles(users,roles,rules)
    ruleUsage = [ sum(x) for x in zip(*URMatrix)]
print("\nRULES:")
for r in rules:
    print(r)

print("\nURMatrix: "+str(URMatrix))

RPMatrix = assignRolesToPermissions(roles,permissionCnt)
print("\nRPMatrix: "+str(RPMatrix))

UPMatrix = numpy.matrix(URMatrix,dtype=bool) * numpy.matrix(RPMatrix,dtype=bool)

print("\nUPMatrix:")
UPMatrix = numpy.matrix(UPMatrix,dtype=int)
print(UPMatrix)

#UPMatrix = addNoise(URMatrix, noise)
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
directory = "..\\TestData\\Data_"+timestamp
if not os.path.exists(directory):
    os.makedirs(directory)
printDataIntoFiles(directory,users, roles, UPMatrix, rules)
visual.showRoleModel(URMatrix, RPMatrix, UPMatrix, directory+"\\graphic", False, False, True, True)

#visual.showAllRoles(population,0,Original, directory+"\\mytest_best", False, False, True, True)