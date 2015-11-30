__author__ = 'Theresa Brandt von Fackh'

import rm_EAInitialization as init
import rm_EAOptimizer as optimizer
import rm_EADecoder as decoder
import MatrixOperators as matrixOps
import random
import numpy
from collections import Counter
import logging
logger = logging.getLogger('root')

# -----------------------------------------------------------------------------------
# Adds a role to a rolemodel
# -----------------------------------------------------------------------------------
def addRole(rolemodel, userSize, permissionSize, alternativeOption,optimization):
    if ((len(rolemodel) < userSize) and (len(rolemodel) < permissionSize)):
        permissionUsage = [0 for i in range(0,permissionSize)]
        userUsage = [0 for i in range(0,userSize)]
        role, userUsage, permissionUsage = init.generateGene_optimized(userUsage, permissionUsage)
        rolemodel.append(role)
        if (optimization[0]):
            rolemodel = optimizer.combineObjects(rolemodel, 1)
        if (optimization[1]):
            rolemodel = optimizer.combineObjects(rolemodel, 0)
    else:
        logger.debug("No role could be added, since max. role number is already achieved")
        if (alternativeOption):
            rolemodel = removeRole(rolemodel, userSize, permissionSize, False, optimization)
    return rolemodel

# -----------------------------------------------------------------------------------
# Removes a role from a rolemodel
# -----------------------------------------------------------------------------------
def removeRole(rolemodel, userSize, permissionSize, alternativeOption, optimization):
    if (len(rolemodel) > 1):
        # Collect users, which only occur in 1 role in the rolemodel
        userUsage = []
        permissionUsage = []
        for role in rolemodel:
            userUsage += [user for user in role[0]]
            permissionUsage += [permission for permission in role[1]]
        usersWithOneTimeOccurance = [k for k,v in Counter(userUsage).items() if v<2]
        permissionsWithOneTimeOccurance = [k for k,v in Counter(permissionUsage).items() if v<2]

        # Select roles, which can be removed
        # A role with a user, which only occurs once in the rolemodel, cannot be removed
        selectedRoles = []
        if (usersWithOneTimeOccurance or permissionsWithOneTimeOccurance):
            for role in rolemodel:
                lastUserOccurance = [u for u in usersWithOneTimeOccurance if u in role[0]]
                lastPermissionOccurance = [p for p in permissionsWithOneTimeOccurance if p in role[1]]
                if (len(lastUserOccurance) <= 0 and len(lastPermissionOccurance) <= 0):
                    selectedRoles.append(role)
        else:
            selectedRoles = rolemodel

        # Remove a role from the selected roles
        if (selectedRoles):
            role = selectedRoles[random.randint(0, len(selectedRoles)-1)]
            rolemodel.remove(role)
        else:
            logger.debug("No role could be removed, since all roles contain at least one user, which does not occur in other roles")
            if (alternativeOption):
                rolemodel = addRole(rolemodel, userSize, permissionSize, False, optimization)
    else:
        logger.debug("No role could be removed, since the rolemodel only contains one role")
        if (alternativeOption):
            rolemodel = addRole(rolemodel, userSize, permissionSize, False, optimization)
    return rolemodel

# -----------------------------------------------------------------------------------
# Removes an user from a role
# -----------------------------------------------------------------------------------
def removeUser(rolemodel, userSize, alternativeOption,optimization):
    # Collect users, which only occur in 1 role in the rolemodel
    userUsage = []
    for role in rolemodel:
        userUsage += [user for user in role[0]]
    usersWithOneTimeOccurance = [k for k,v in Counter(userUsage).items() if v<2]

    # Select roles, which contain more than one user
    selectedRoles = [role for role in rolemodel if (len(role[0]) > 1)]

    userRemoved = False
    while(selectedRoles and not userRemoved):
        index = random.randint(0, len(selectedRoles)-1)
        role = selectedRoles.pop(index)
        selectedUsers = [user for user in role[0] if user not in usersWithOneTimeOccurance]
        if(selectedUsers):
            # Remove a user from the selected users of the selected roles
            user = selectedUsers[random.randint(0, len(selectedUsers)-1)]
            role[0].remove(user)
            if (optimization[1]):
                rolemodel = optimizer.combineObjects(rolemodel, 0)
            userRemoved = True

    if (not userRemoved):
        logger.debug("No user could be removed, since all roles only contain one user or users, which only occur once in the rolemodel")
        if (alternativeOption):
            rolemodel = addUser(rolemodel, userSize, False, optimization)

    return rolemodel

# -----------------------------------------------------------------------------------
# Removes a permission from a role
# -----------------------------------------------------------------------------------
def removePermission(rolemodel, permissionSize, alternativeOption,optimization):

    # Collect permissions, which only occur in 1 role in the rolemodel
    permissionUsage = []
    for role in rolemodel:
        permissionUsage += [permission for permission in role[1]]
    permissionsWithOneTimeOccurance = [k for k,v in Counter(permissionUsage).items() if v<2]

    # Select roles, which contain more than one permission
    selectedRoles = [role for role in rolemodel if (len(role[1]) > 1)]

    permissionRemoved = False
    while(selectedRoles and not permissionRemoved):
        index = random.randint(0, len(selectedRoles)-1)
        role = selectedRoles.pop(index)
        selectedPermissions = [permission for permission in role[1] if permission not in permissionsWithOneTimeOccurance]
        if(selectedPermissions):
            # Remove a user from the selected users of the selected roles
            permission = selectedPermissions[random.randint(0, len(selectedPermissions)-1)]
            role[1].remove(permission)
            if (optimization[0]):
                rolemodel = optimizer.combineObjects(rolemodel, 1)
            permissionRemoved = True

    if (not permissionRemoved):
        logger.debug("No permission could be removed, since all roles only contain one permission or permissions, which only occur once in the rolemodel")
        if (alternativeOption):
            rolemodel = addPermission(rolemodel, permissionSize, False, optimization)

    return rolemodel

# -----------------------------------------------------------------------------------
# Add an user from a role
# -----------------------------------------------------------------------------------
def addUser(rolemodel, userSize, alternativeOption,optimization):
    # Select roles, which do not have all permissions
    selectedRoles = [role for role in rolemodel if len(role[0])<userSize]

    # Pick random role from selected roles
    userAdded = False
    while (selectedRoles and not userAdded):
        index = random.randint(0, len(selectedRoles) - 1)
        role = selectedRoles.pop(index)
        missingUsers = [user for user in range(0,userSize) if user not in role[0]]
        if (missingUsers):
            user = missingUsers[random.randint(0, len(missingUsers)-1)]
            role[0].add(user)
            if (optimization[1]):
                rolemodel = optimizer.combineObjects(rolemodel, 0)
            userAdded = True

    if (not userAdded):
        logger.debug("No user could be added, since all roles already contain all users")
        if (alternativeOption):
            rolemodel = removeUser(rolemodel, userSize, False, optimization)

    return rolemodel

# -----------------------------------------------------------------------------------
# Add a permission from a role
# -----------------------------------------------------------------------------------
def addPermission(rolemodel, permissionSize, alternativeOption, optimization):
    # Select roles, which do not have all permissions
    selectedRoles = [role for role in rolemodel if len(role[1])<permissionSize]

    # Pick random role from selected roles
    permissionAdded = False
    while (selectedRoles and not permissionAdded):
        index = random.randint(0, len(selectedRoles) - 1)
        role = selectedRoles.pop(index)
        missingPermissions = [user for user in range(0,permissionSize) if user not in role[1]]
        if (missingPermissions):
            permission = missingPermissions[random.randint(0, len(missingPermissions)-1)]
            role[1].add(permission)
            if (optimization[0]):
                rolemodel = optimizer.combineObjects(rolemodel, 1)
            permissionAdded = True

    if (not permissionAdded):
        logger.debug("No permission could be added, since all roles already contain all permissions")
        if (alternativeOption):
            rolemodel = removePermission(rolemodel, permissionSize,False, optimization)

    return rolemodel

# -----------------------------------------------------------------------------------
# Mutation Function
# -----------------------------------------------------------------------------------
def mutFunc(individual, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, userSize, permissionSize, optimization):
    #print("Mutation: "+str(individual[0]))

    if (random.random() < addRolePB):
        #print("Add role")
        individual[0] = addRole(individual[0], userSize, permissionSize, True,optimization)

    if random.random() < addUserPB:
        #print("Add User")
        individual[0] = addUser(individual[0], userSize, True,optimization)

    if random.random() < addPermissionPB:
        #print("Add Permission")
        individual[0] = addPermission(individual[0], permissionSize, True,optimization)

    if (random.random() < removeRolePB):
        #print("Remove role")
        individual[0] = removeRole(individual[0],userSize, permissionSize, True,optimization)

    if random.random() < removeUserPB:
        #print("Remove User")
        individual[0] = removeUser(individual[0],userSize, True,optimization)

    if random.random() < removePermissionPB:
        #print("Remove Permission")
        individual[0] = removePermission(individual[0],permissionSize, True,optimization)

    #print("==>: "+str(individual[0]))

    return individual,

# -----------------------------------------------------------------------------------
# Mutation Function, which allows invalid rolemodels
# -----------------------------------------------------------------------------------
def mutFunc_old(individual, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, userSize, permissionSize, optimization):
    #print("Mutation: "+str(individual[0]))
    if (random.random() < addRolePB) and (len(individual[0]) < userSize) and (len(individual[0]) < permissionSize):
        permissionUsage = [0 for i in range(0,permissionSize)]
        userUsage = [0 for i in range(0,userSize)]
        gene, userUsage, permissionUsage = init.generateGene_optimized(userUsage, permissionUsage)
        individual[0].append(gene)
        if (optimization[0]):
            individual[0] = optimizer.combineObjects(individual[0], 1)
        if (optimization[1]):
            individual[0] = optimizer.combineObjects(individual[0], 0)
    if ((len(individual[0]) > 1) and (random.random() < removeRolePB)):
        role = random.randint(0, len(individual[0]) - 1)
        del individual[0][role]
    if random.random() < removeUserPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        if (len(role[0]) > 1):
            # Remove exactly 1 user
            user = random.sample(role[0],1)[0]
            role[0].remove(user)
        if (optimization[1]):
            individual[0] = optimizer.combineObjects(individual[0], 0)
    if random.random() < removePermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        if (len(role[1]) > 1):
            # Remove exactly 1 permission
            role[1].remove(random.sample(role[1],1)[0])
        if (optimization[0]):
            individual[0] = optimizer.combineObjects(individual[0], 1)
    if random.random() < addUserPB:
        # Pick random gene (role)
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        userCnt = len(role[0])
        if (userCnt < userSize):
            # Add exactly 1 user, if the role does not already contain all users
            user = random.randint(0, userSize-1)
            while (user in role[0]):
                user = random.randint(0, userSize-1)
            role[0].add(user)
        if (optimization[1]):
            individual[0] = optimizer.combineObjects(individual[0], 0)
    if random.random() < addPermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        permissionCnt = len(role[1])
        if (permissionCnt < permissionSize):
            permission = random.randint(0, permissionSize-1)
            while (permission in role[1]):
                permission = random.randint(0, permissionSize-1)
            role[1].add(permission)
        if (optimization[0]):
            individual[0] = optimizer.combineObjects(individual[0], 1)
    return individual,

# -----------------------------------------------------------------------------------
# Crossover Function
# -----------------------------------------------------------------------------------
def mateFunc(ind1, ind2,optimization):
    #logger.debug("Crossover")
    temp1 = ind1[0]
    temp2 = ind2[0]
    size = min(len(temp1), len(temp2))
    if size > 1:
        cxpoint = random.randint(1, size - 1)
        temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
        if (optimization):
            temp1 = optimizer.localOptimization(temp1)
            temp2 = optimizer.localOptimization(temp2)
    return ind1, ind2

# -----------------------------------------------------------------------------------
# Crossover Function
# -----------------------------------------------------------------------------------
def mateFunc_old(ind1, ind2,optimization):
    logger.debug("Crossover")
    temp1 = ind1[0]
    temp2 = ind2[0]
    size = min(len(temp1), len(temp2))
    if size > 1:
        cxpoint = random.randint(1, size - 1)
        temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
        if (optimization):
            temp1 = optimizer.localOptimization(temp1)
            temp2 = optimizer.localOptimization(temp2)
    return ind1, ind2
