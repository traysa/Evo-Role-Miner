__author__ = 'Theresa'

import rm_EAInitialization as init
import rm_EAOptimizer as optimizer
import random

# -----------------------------------------------------------------------------------
# Mutation Function
# -----------------------------------------------------------------------------------
def mutFunc(individual, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, userSize, permissionSize):
    #print("Mutation: "+str(individual[0]))
    if (random.random() < addRolePB) and (len(individual[0]) < userSize) and (len(individual[0]) < permissionSize):
        permissionUsage = [0 for i in range(0,permissionSize)]
        userUsage = [0 for i in range(0,userSize)]
        gene, userUsage, permissionUsage = init.generateGene_optimized(userUsage, permissionUsage)
        individual[0].append(gene)
        #print("Add role: "+str(individual[0]))
        individual[0] = optimizer.combineObjects(individual[0], 1)
        individual[0] = optimizer.combineObjects(individual[0], 0)
    if ((len(individual[0]) > 1) and (random.random() < removeRolePB)):
        role = random.randint(0, len(individual[0]) - 1)
        del individual[0][role]
        #print("Remove role: "+str(individual[0]))
    if random.random() < removeUserPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        if (len(role[0]) > 1):
            # Remove exactly 1 user
            user = random.sample(role[0],1)[0]
            role[0].remove(user)
            #del role[0][random.randint(0, len(role[0]) - 1)]
        #print("Remove user: "+str(individual[0]))
        individual[0] = optimizer.combineObjects(individual[0], 0)
    if random.random() < removePermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        if (len(role[1]) > 1):
            # Remove exactly 1 permission
            role[1].remove(random.sample(role[1],1)[0])
            #del role[1][random.randint(0, len(role[1]) - 1)]
        #print("Remove permission: "+str(individual[0]))
        individual[0] = optimizer.combineObjects(individual[0], 1)
    if random.random() < addUserPB:
        # Pick random gene (role)
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        userCnt = len(role[0])
        #userSet = {x for x in range(1, userSize + 1)}
        if (userCnt < userSize):
            # Add exactly 1 user, if the role does not already contain all users
            user = random.randint(0, userSize-1)
            while (user in role[0]):
                user = random.randint(0, userSize-1)
            role[0].add(user)
            #role[0] = list(set(role[0]) | {random.randint(1, userSize)})
        #print("Add user: "+str(individual[0]))
        individual[0] = optimizer.combineObjects(individual[0], 0)
    if random.random() < addPermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        permissionCnt = len(role[1])
        if (permissionCnt < permissionSize):
            permission = random.randint(0, permissionSize-1)
            while (permission in role[1]):
                permission = random.randint(0, permissionSize-1)
            role[1].add(permission)
            #role[1] = list(set(role[1]) | {random.randint(1, permissionSize)})
        #print("Add permission: "+str(individual[0]))
        individual[0] = optimizer.combineObjects(individual[0], 1)
    return individual,

# -----------------------------------------------------------------------------------
# Crossover Function
# -----------------------------------------------------------------------------------
def mateFunc(ind1, ind2):
    #print("Crossover")
    temp1 = ind1[0]
    temp2 = ind2[0]
    size = min(len(temp1), len(temp2))
    if size > 1:
        cxpoint = random.randint(1, size - 1)
        temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
        temp1 = optimizer.localOptimization(temp1)
        temp2 = optimizer.localOptimization(temp2)
    return ind1, ind2
