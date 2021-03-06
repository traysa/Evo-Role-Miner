__author__ = 'Theresa Brandt von Fackh'

import random
import os
import datetime
import rm_Visualization as visual
import numpy

# -----------------------------------------------------------------------------------
# Draw a certain number of items randomly from a bucket
# Returns the bucket and a set of items
# -----------------------------------------------------------------------------------
def drawFromBucket(bucket, itemCnt):
    items = set()
    for i in range(itemCnt):
        item = random.randint(0,len(bucket)-1)
        items.add(bucket.pop(item))
    return bucket, items

# -----------------------------------------------------------------------------------
# Generate Roles with:
# - Limit of permissions per role
# - Limit of permission usage
# - Unused permissions possible
# - Roles with no permissions possible --> error occurs
# -----------------------------------------------------------------------------------
def generateRoles(roleCnt, permissionCnt, maxPermissionForRole, maxPermissionUsage):
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
            raise ValueError("An error occured: Permission bucket is empty")
    #print("roles: "+str(roles))
    return roles

# -----------------------------------------------------------------------------------
# Generate Roles with:
# - Limit of permissions per role
# - Limit of permission usage
# - A permission is in at least one role
# - No roles with no permission TODO
# -----------------------------------------------------------------------------------
def generateRoles2(roleCnt, permissionCnt, maxPermissionForRole, maxPermissionUsage):
    if (permissionCnt*maxPermissionUsage) < roleCnt:
         raise ValueError("An error occured: Not all roles can get permissions")
    roles = [set() for r in range(roleCnt)]
    #print("roles: "+str(roles))
    permissionUsage = [0 for p in range(permissionCnt)]
    #print("permissionUsage: "+str(permissionUsage))
    permissionBucket = [p for p in range(permissionCnt) for c in range(maxPermissionUsage)]
    #print("permissionBucket: "+str(permissionBucket))
    emptySlotsinRole = [maxPermissionForRole for r in range(roleCnt)]
    while (0 in permissionUsage and sum(emptySlotsinRole) != 0): #TODO check
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

# -----------------------------------------------------------------------------------
# Generate Roles with:
# - Limit of permissions per role
# - Limit of permission usage
# - A permission is in at least one role
# - Limit of assignment density
# -----------------------------------------------------------------------------------
def generateRoles3(roleCnt, permissionCnt, maxPermissionForRole, maxPermissionUsage, RPdensity):
    if (permissionCnt*maxPermissionUsage) < roleCnt:
         raise ValueError("An error occured: Not all roles can get permissions")
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

# -----------------------------------------------------------------------------------
# Generate Roles with:
# - Limit of permissions per role
# - Limit of permission usage
# - A permission is in at least one role
# - Configuration of role densities
# -----------------------------------------------------------------------------------
def generateRoles4(roleCnt, permissionCnt, maxPermissionUsage, configPermissionsForRoles):
    roles = [set() for r in range(roleCnt)]
    #print("roles: "+str(roles))
    permissionUsage = [0 for p in range(permissionCnt)]
    #print("permissionUsage: "+str(permissionUsage))
    permissionBucket = [p for p in range(permissionCnt) for c in range(maxPermissionUsage)]
    #print("permissionBucket: "+str(permissionBucket))

    emptySlotsinRole = [0 for r in range(roleCnt)]
    rolePercentage = 0.0
    roleFraction = 0
    role = 0
    for config in configPermissionsForRoles:
        rolePercentage += config[0]
        roleFraction += int(round(config[0]*roleCnt))
        #print(roleFraction)
        if (roleFraction > roleCnt):
            print("WARNING: configPermissionsForRoles is not conform")
        minPermissions = config[1]
        maxPermissions = config[2]
        while ((role < roleCnt) and (role < roleFraction)):
            emptySlotsinRole[role] = random.randint(minPermissions,maxPermissions)
            role += 1
    if (roleFraction < roleCnt):
        print("WARNING: No configPermissionsForRoles for all roles")
        while ((roleFraction < roleCnt) and (role < roleCnt)):
            emptySlotsinRole[role] = random.randint(1,permissionCnt)
            role += 1

    print("Permission Count for each role: "+str(emptySlotsinRole))

    if (maxPermissionUsage*permissionCnt < sum(emptySlotsinRole)):
        raise ValueError("Not enough permission usage for all roles")

    assignments = 0
    while (0 in permissionUsage and sum(emptySlotsinRole) != 0):
        #print("permissionUsage: "+str(permissionUsage))
        openPermissions = [p for p in range(permissionCnt) if permissionUsage[p]<maxPermissionUsage]
        #print("openPermissions: "+str(openPermissions))
        selectedPermission = random.sample(openPermissions,1)[0]
        #permissionBucket[selectedPermission] -= 1
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
    if (0 in permissionUsage):
        print("WARNING: There are unused permissions")
        while (0 in permissionUsage):
            unusedPermissions = [p for p in range(permissionCnt) if permissionUsage[p]==0]
            for unusedPermission in unusedPermissions:
                selectedRole = random.randint(0,roleCnt-1)
                permissions = roles[selectedRole]
                selectedPermission = permissions.pop()
                permissionUsage[selectedPermission] -= 1
                permissions.add(unusedPermission)
                permissionUsage[unusedPermission] += 1

    roles.sort(key=lambda row: row)
    return roles

# -----------------------------------------------------------------------------------
# Remove duplicates from list
# -----------------------------------------------------------------------------------
def uniq(lst):
    last = object()
    for item in lst:
        if item == last:
            continue
        yield item
        last = item

# -----------------------------------------------------------------------------------
# Generate Users with attribute values
# -----------------------------------------------------------------------------------
def generateUsers(userCnt,attributes,userTypeCnt):
    userTypes = []
    while(len(userTypes) < userTypeCnt):
        userType = [[] for a in range(len(attributes))]
        for a,attrValues in enumerate(attributes):
            userType[a] = attrValues[random.randint(0,len(attrValues)-1)]
        userTypes.append(userType)
        userTypes = list(uniq(sorted(userTypes)))
    print("\nUSERTYPES:")
    for userType in userTypes:
        print(userType)
    users = userTypes
    while (len(users) < userCnt):
        userType = random.sample(userTypes,1)[0]
        users.append(userType)
    users.sort(key=lambda row: row)
    return users

# -----------------------------------------------------------------------------------
# Generate Rules for Roles
# -----------------------------------------------------------------------------------
def generateRules(rules_AND, roleCnt, attributes, maxRuleConditionCnt, ruleUsage, userUsage):
    #rules = [[] for r in range(roleCnt)]
    #print("rules: "+str(rules))
    if (0 not in ruleUsage):
        roleList = [random.randint(0,roleCnt-1)]
    else:
        roleList = [i for i, j in enumerate(ruleUsage) if j == 0]

    for role in roleList:
        rules_OR = []
        selectedAttributes = random.sample(range(0,len(attributes)),random.randint(1,maxRuleConditionCnt))
        #print("selectedAttributes: "+str(selectedAttributes))
        attrSet = []
        for a in range(len(attributes)):
            attrValueSet = []
            if (a in selectedAttributes):
                attrValues = attributes[a]
                #numberOfValues = random.randint(1,len(attrValues)-1)
                #attrValueSet = random.sample(attrValues,numberOfValues)
                attrValueSet = random.sample(attrValues,1)
            attrSet.append(attrValueSet)
        #print("attrSet: "+str(attrSet))
        if (attrSet not in rules_OR):
            rules_OR.append(attrSet)
        rules_AND[role] = rules_OR

    #print("rules: "+str(rules))
    return rules_AND

# -----------------------------------------------------------------------------------
# Generate advanced Rules for Roles
# -----------------------------------------------------------------------------------
def generateAdvancedRules(rules_AND, roleCnt, attributes, maxRuleConditionCnt, ruleUsage, userUsage):
    #rules = [[] for r in range(roleCnt)]
    #print("rules: "+str(rules))
    if (0 not in ruleUsage):
        roleList = [random.randint(0,roleCnt-1)]
    else:
        roleList = [i for i, j in enumerate(ruleUsage) if j == 0]

    for role in roleList:
        rules_OR = []
        rule_OR_Size = random.randint(1,2)
        while rule_OR_Size > 0:
            selectedAttributes = random.sample(range(0,len(attributes)),random.randint(1,maxRuleConditionCnt))
            #print("selectedAttributes: "+str(selectedAttributes))
            attrSet = []
            for a in range(len(attributes)):
                attrValueSet = []
                if (a in selectedAttributes):
                    attrValues = attributes[a]
                    #numberOfValues = random.randint(1,len(attrValues)-1)
                    #attrValueSet = random.sample(attrValues,numberOfValues)
                    attrValueSet = random.sample(attrValues,1)
                attrSet.append(attrValueSet)
            #print("attrSet: "+str(attrSet))
            if (attrSet not in rules_OR):
                rules_OR.append(attrSet)
            rule_OR_Size -= 1
        rules_AND[role] = rules_OR

    #print("rules: "+str(rules))
    return rules_AND

# -----------------------------------------------------------------------------------
# Assign Users to Roles according to Rules
# Return URMatrix
# -----------------------------------------------------------------------------------
def assignUsersToRoles(users, roles, rules_AND):
    rolesCnt = len(roles)
    userCnt = len(users)
    URMatrix = [[0 for r in range(rolesCnt)] for u in range(userCnt)]
    for r_AND,rule_AND in enumerate(rules_AND):
        for r_OR,rule_OR in enumerate(rule_AND):
            #print("rule: "+str(rule))
            for u,user in enumerate(users):
                #print("user: "+str(user))
                match = True
                for attr in range(len(rule_OR)):
                    if ((len(rule_OR[attr]) != 0) and (user[attr] not in rule_OR[attr])):
                        match = False
                if (match):
                    #print("match")
                    URMatrix[u][r_AND] = 1
    return URMatrix

# -----------------------------------------------------------------------------------
# Assign Users to Roles according to Rules with
# - Limit number of TODO
# Return URMatrix
# -----------------------------------------------------------------------------------
def assignUsersToRoles2(users, roles, rules, density):
    rolesCnt = len(roles)
    userCnt = len(users)
    URMatrix = [[0 for r in range(rolesCnt)] for u in range(userCnt)]

    for u,user in enumerate(users):
        #print("user: "+str(user))
        assignedRolesForUser = [0 for role in range(rolesCnt)]
        for r,rule in enumerate(rules):
        #print("rule: "+str(rule))
            match = True
            for attr in range(len(rule)):
                if ((len(rule[attr]) != 0) and (user[attr] not in rule[attr])):
                    match = False
            if (match):
                #print("match")
                assignedRolesForUser[r] = 1

        if (sum(assignedRolesForUser) >= density*len(assignedRolesForUser)): #TODO check
            # Delete all role assignments of user
            #print("sum(assignedRolesForUser): "+str(sum(assignedRolesForUser)))
            #print("density: "+str(density*len(assignedRolesForUser)))
            #print("dense")
            URMatrix[u] = [0 for role in range(rolesCnt)]
        else:
            URMatrix[u] = assignedRolesForUser
    return URMatrix

# -----------------------------------------------------------------------------------
# Assign Users to Roles according to Rules
# -----------------------------------------------------------------------------------
def createRPMatrix(roles, permissionCnt):
    rolesCnt = len(roles)
    RPMatrix = [[0 for p in range(permissionCnt)] for r in range(rolesCnt)]
    for r,role in enumerate(roles):
        for p in role:
            RPMatrix[r][p] = 1
    return RPMatrix

# -----------------------------------------------------------------------------------
# Add noise by bitflip in the UPMatrix
# -----------------------------------------------------------------------------------
def addNoise(UPmatrix, noise):
    UPMatrixWithNoise = numpy.copy(UPMatrix)
    for u,user in enumerate(UPMatrixWithNoise):
        for p,permission in enumerate(user):
            if (UPMatrixWithNoise[u,p]):
                r = random.random()
                if (r<=noise[0]):
                    UPMatrixWithNoise[u,p] = int(not(UPMatrixWithNoise[u,p]))
            else:
                r = random.random()
                if (r<=noise[1]):
                    UPMatrixWithNoise[u,p] = int(not(UPMatrixWithNoise[u,p]))
    return UPMatrixWithNoise

# -----------------------------------------------------------------------------------
# Print generated data into files
# -----------------------------------------------------------------------------------
def printDataIntoFiles(directory, users, roles, UPMatrix, URMatrix, RPMatrix, rules_AND, UPMatrixWithNoise, noise):
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
            for r in range(0,UPMatrix.shape[1]):
                 outfile.write(str(UPMatrix[u,r])+";")
            outfile.write("\n")
        outfile.close()
    print("DONE.\n")

    urmatrixCSVfile = directory+"\\URMatrix.csv"
    print("Write into CSV file "+str(urmatrixCSVfile)+"...")
    if not os.path.exists(urmatrixCSVfile):
        with open(urmatrixCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("User;")
            for r in range(0,URMatrix.shape[1]):
                 outfile.write("Role"+str(r+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(urmatrixCSVfile, "a") as outfile:
        for u,user in enumerate(users):
            outfile.write(str(u+1)+";")
            for r in range(0,URMatrix.shape[1]):
                 outfile.write(str(URMatrix[u,r])+";")
            outfile.write("\n")
        outfile.close()
    print("DONE.\n")

    rpmatrixCSVfile = directory+"\\RPMatrix.csv"
    print("Write into CSV file "+str(rpmatrixCSVfile)+"...")
    if not os.path.exists(rpmatrixCSVfile):
        with open(rpmatrixCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("Role;")
            for p in range(0,RPMatrix.shape[1]):
                 outfile.write("Permission"+str(p+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(rpmatrixCSVfile, "a") as outfile:
        for r,role in enumerate(roles):
            outfile.write(str(r+1)+";")
            for p in range(0,RPMatrix.shape[1]):
                 outfile.write(str(RPMatrix[r,p])+";")
            outfile.write("\n")
        outfile.close()
    print("DONE.\n")

    upmatrixWithNoiseCSVfile = directory+"\\UPMatrixWithNoise.csv"
    print("Write into CSV file "+str(upmatrixWithNoiseCSVfile)+"...")
    if not os.path.exists(upmatrixWithNoiseCSVfile):
        with open(upmatrixWithNoiseCSVfile, "a") as outfile:
            outfile.write("sep=;\n")
            outfile.write("User;")
            for p in range(0,UPMatrixWithNoise.shape[1]):
                 outfile.write("Permission"+str(p+1)+";")
            outfile.write("\n")
            outfile.close()
    with open(upmatrixWithNoiseCSVfile, "a") as outfile:
        for u,user in enumerate(users):
            outfile.write(str(u+1)+";")
            for p in range(0,UPMatrixWithNoise.shape[1]):
                 outfile.write(str(UPMatrixWithNoise[u,p])+";")
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
        for r_AND,rule_AND in enumerate(rules_AND):
            for r_OR,rule_OR in enumerate(rule_AND):
                outfile.write(str(r_AND+1)+";")
                for attr in range(0,len(rule_OR)):
                    tmp = ""
                    for value in rule_OR[attr]:
                        tmp += str(value)+","
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
            outfile.write("# Noise: False\n")
            outfile.write("\n")
            for u,user in enumerate(UPMatrix):
                tmp = "u_U"+str(u)
                for p in range(0,UPMatrix.shape[1]):
                    if (UPMatrix[u,p]==1):
                        tmp += " p_P"+str(p)
                outfile.write(tmp+"\n")
            outfile.close()
    print("DONE.\n")

    testdataNoiseFile = directory+"\\testdata_noise.rbac"
    print("Write into RBAC file "+str(testdataNoiseFile)+"...")
    if not os.path.exists(testdataNoiseFile):
        with open(testdataNoiseFile, "a") as outfile:
            outfile.write("# Automatically generated data\n")
            outfile.write("# Users: "+str(UPMatrixWithNoise.shape[0])+"\n")
            outfile.write("# Permissions: "+str(UPMatrixWithNoise.shape[1])+"\n")
            outfile.write("# UserPermissionAssignments: "+str(UPMatrixWithNoise.sum())+"\n")
            outfile.write("# Noise: True "+str(noise)+"\n")
            outfile.write("#        Less permissions than Original: "+str(noise[0])+"\n")
            outfile.write("#        More permissions than Original: "+str(noise[1])+"\n")
            outfile.write("\n")
            for u,user in enumerate(UPMatrixWithNoise):
                tmp = "u_U"+str(u)
                for p in range(0,UPMatrixWithNoise.shape[1]):
                    if (UPMatrixWithNoise[u,p]==1):
                        tmp += " p_P"+str(p)
                outfile.write(tmp+"\n")
            outfile.close()
    print("DONE.\n")

# -----------------------------------------------------------------------------------
# Configuration parameters for Data Generator
# -----------------------------------------------------------------------------------
attributes = [['Sales','Motor','HumanResources','Development','FacilityManagement','Marketing'],['Denmark','Germany','US'],['Internal','External']] #User attributes and attributevalues
userCnt = 100 #Total number of users
userTypeCnt = 25 #Number of different usertypes (usertype is described by the users attributes)
permissionCnt = 100 #Total number of permissions
roleCnt = 25 #Total number of roles
configPermissionsForRoles = [(0.2,11,15),(0.8,2,10)] #Density of roles: (percentage of all roles, minPermissionCnt, maxPermissionCnt)
#RPdensity = 0.8
#maxPermissionForRole = 46
maxPermissionUsage = 5 #How often a permission can occur in different roles
maxRuleConditionCnt = 3 #
noise = [0.02,0.04] #Artificial noise (bit-flip in UP-Matrix):[users with to few permissions, users with too many permissions]

#roles = generateRoles3(roleCnt,permissionCnt,maxPermissionForRole, maxPermissionUsage, RPdensity)
roles = generateRoles4(roleCnt,permissionCnt, maxPermissionUsage, configPermissionsForRoles)
print("\nROLES:")
for r in roles:
    print(r)

users = generateUsers(userCnt,attributes,userTypeCnt)
print("\nUSERS:")
for u in users:
    print(u)

rules_AND = [[] for r in range(roleCnt)]
ruleUsage = [0 for i in range(roleCnt)]
userUsage = [0 for i in range(userCnt)]
while (0 in userUsage):
    rules_AND = generateRules(rules_AND,roleCnt,attributes,maxRuleConditionCnt,ruleUsage,userUsage)
    URMatrix = assignUsersToRoles(users,roles,rules_AND)
    userUsage = [ sum(x) for x in URMatrix]
    ruleUsage = [ sum(x) for x in zip(*URMatrix)]
URMatrix = numpy.matrix(URMatrix,dtype=int)
print("\nRULES:")
for r in rules_AND:
    print(r)

print("\nURMatrix: "+str(URMatrix))

RPMatrix = createRPMatrix(roles,permissionCnt)
RPMatrix = numpy.matrix(RPMatrix,dtype=int)
print("\nRPMatrix: "+str(RPMatrix))

UPMatrix = numpy.matrix(URMatrix,dtype=bool) * numpy.matrix(RPMatrix,dtype=bool)

print("\nUPMatrix:")
UPMatrix = numpy.matrix(UPMatrix,dtype=int)
print(UPMatrix)

UPMatrixWithNoise = addNoise(URMatrix, noise)

timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
directory = "..\\TestData\\Data_"+timestamp+"_"+str(userCnt)+"x"+str(permissionCnt)
if not os.path.exists(directory):
    os.makedirs(directory)

configCSVfile = directory+"\\config.csv"
print("Write into CSV file "+str(configCSVfile)+"...")
if not os.path.exists(configCSVfile):
    with open(configCSVfile, "a") as outfile:
        outfile.write("sep=;\n")
        outfile.write("userCnt;"+str(userCnt)+"\n")
        outfile.write("userTypeCnt;"+str(userTypeCnt)+"\n")
        outfile.write("permissionCnt;"+str(permissionCnt)+"\n")
        outfile.write("roleCnt;"+str(roleCnt)+"\n")
        outfile.write("configPermissionsForRoles;"+str(configPermissionsForRoles)+"\n")
        outfile.write("maxPermissionUsage;"+str(maxPermissionUsage)+"\n")
        outfile.write("maxRuleConditionCnt;"+str(maxRuleConditionCnt)+"\n")
        outfile.write("noise;"+str(noise)+"\n")
        outfile.close()
print("DONE.\n")

printDataIntoFiles(directory, users, roles, UPMatrix, URMatrix, RPMatrix, rules_AND, UPMatrixWithNoise, noise)
visual.showRoleModel(URMatrix, RPMatrix, UPMatrix, UPMatrixWithNoise, directory+"\\role_model", True, False, True, True)

#visual.showAllRoles(population,0,Original, directory+"\\mytest_best", False, False, True, True)