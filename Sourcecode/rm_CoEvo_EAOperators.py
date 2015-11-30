__author__ = 'Theresa Brandt von Fackh'

import random

# -----------------------------------------------------------------------------------
# Mutation Function
# -----------------------------------------------------------------------------------
def mutFunc(individual, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, userSize, permissionSize):
    #print("Mutation")
    #print("BEFORE: "+str(individual))
    role = individual[0]
    if random.random() < removeUserPB:
        if (len(role[0]) > 1):
            # Remove exactly 1 user
            user = random.sample(role[0],1)[0]
            role[0].remove(user)
    if random.random() < removePermissionPB:
        if (len(role[1]) > 1):
            # Remove exactly 1 permission
            role[1].remove(random.sample(role[1],1)[0])
    if random.random() < addUserPB:
        userCnt = len(role[0])
        #userSet = {x for x in range(1, userSize + 1)}
        if (userCnt < userSize):
            # Add exactly 1 user, if the role does not already contain all users
            user = random.randint(0, userSize-1)
            while (user in role[0]):
                user = random.randint(0, userSize-1)
            role[0].add(user)
    if random.random() < addPermissionPB:
        permissionCnt = len(role[1])
        if (permissionCnt < permissionSize):
            permission = random.randint(0, permissionSize-1)
            while (permission in role[1]):
                permission = random.randint(0, permissionSize-1)
            role[1].add(permission)
    #print("AFTER: "+str(individual))
    return individual,


# -----------------------------------------------------------------------------------
# Crossover Function
# -----------------------------------------------------------------------------------
def mateFunc(ind1, ind2, r):
    #print("Crossover")
    #print("BEFORE: "+str(ind1)+" -- "+str(ind2))
    if random.random() < r:
        temp1 = ind1[0][0]
        temp2 = ind2[0][0]
        size = min(len(temp1), len(temp2))
        if size > 1:
            cxpoint = random.randint(1, size - 1)
            removeFromTemp1 = list(temp1)[cxpoint:]
            removeFromTemp2 = list(temp2)[cxpoint:]
            for i in removeFromTemp1:
                temp1.remove(i)
            for i in removeFromTemp2:
                temp2.remove(i)
                temp1.add(i)
            for i in removeFromTemp1:
                temp2.add(i)
    else:
        temp1 = ind1[0][1]
        temp2 = ind2[0][1]
        size = min(len(temp1), len(temp2))
        if size > 1:
            cxpoint = random.randint(1, size - 1)
            removeFromTemp1 = list(temp1)[cxpoint:]
            removeFromTemp2 = list(temp2)[cxpoint:]
            for i in removeFromTemp1:
                temp1.remove(i)
            for i in removeFromTemp2:
                temp2.remove(i)
                temp1.add(i)
            for i in removeFromTemp1:
                temp2.add(i)
    #print("AFTER: "+str(ind1)+" -- "+str(ind2))
    return ind1, ind2

