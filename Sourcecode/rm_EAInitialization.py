__author__ = 'Theresa Brandt von Fackh'

import random
import rm_EAInitialization as init
import rm_EAOptimizer as optimizer

# -----------------------------------------------------------------------------------
# Initialization of Population (Chromosomes)
# RoleModel
# -----------------------------------------------------------------------------------
def generateChromosome(maxRoles, userSize, permissionSize, optimization=True, fixedRoleCnt=0):
    chromosome = []
    # Create random number of genes (roles) for one chromosome
    if fixedRoleCnt > 0:
        maxRoleCnt = fixedRoleCnt
    else:
        maxRoleCnt = random.randint(1, maxRoles)
    #print("ROLESIZE: "+str(maxRoleCnt))
    permissionUsage = [0 for i in range(0,permissionSize)]
    #print("permissionUsage: "+str(permissionUsage))
    userUsage = [0 for i in range(0,userSize)]
    #print("userUsage: "+str(userUsage))
    #for i in range(0, rolesize):
    roleCnt = 0
    while(((0 in permissionUsage) or (0 in userUsage) or roleCnt<maxRoleCnt) and (roleCnt<maxRoles)):
    #for i in range(0, int(maxRoles/2)):
        #gene = utils.generateGene(userSize, permissionSize)
        gene, userUsage, permissionUsage = init.generateGene_optimized(userUsage, permissionUsage)
        # Add gene to chromosome
        chromosome.append(gene)
        roleCnt += 1
    #print("permissionUsage: "+str(permissionUsage))
    if (0 in permissionUsage):
        print("WARNING: Invalid Rolemodel. A permission has not been used")
    if (0 in userUsage):
        print("WARNING: Invalid Rolemodel. A user has not been used")
    #print("userUsage: "+str(userUsage))
    if (optimization):
        chromosome = optimizer.localOptimization(chromosome)


    userUsage = []
    for role in chromosome:
        userUsage += [user for user in role[0]]
    check = [u for u in range(0,userSize) if u not in userUsage]
    if (len(check) > 0):
        temp = 0

    return chromosome

# -----------------------------------------------------------------------------------
# Generate a random role (gene)
# -----------------------------------------------------------------------------------
def generateGene_simple(userSize, permissionSize):
    gene = []
    # Create random length set of users
    user_set = set()
    for i in range(0, userSize):
        if (random.randint(0, 1)):
            user_set.add(i)
    if (len(user_set) < 1):
        user = random.randint(0, userSize-1)
        user_set.add(user)
    gene.append(user_set)
    # Create random length set of permissions
    permission_set = set()
    for i in range(0, permissionSize):
        if (random.randint(0, 1)):
            permission_set.add(i)
    if (len(permission_set) < 1):
        permission = random.randint(0, permissionSize-1)
        if (permission == 6):
            temp = 0
        permission_set.add(permission)
    gene.append(permission_set)
    return gene

# -----------------------------------------------------------------------------------
# Generate a random role (gene)
# -----------------------------------------------------------------------------------
def generateGene_optimized(userUsage, permissionUsage):
    gene = []
    # Create random length set of users
    user_set = set()
    unusedUsers = [u for u in range(len(userUsage)) if userUsage[u]==0]
    if (unusedUsers):
        user = random.sample(unusedUsers,1)[0] # Ensure that user list is not empty and unused users are used first
        user_set.add(user)
        userUsage[user] += 1
    for i in range(random.randint(0,len(userUsage))):
        user = random.sample(range(0,len(userUsage)),1)[0]
        if (user not in user_set):
            user_set.add(user)
            userUsage[user] += 1
    if (len(user_set)==0):
        user = random.sample(range(0,len(userUsage)),1)[0]
        user_set.add(user)
        userUsage[user] += 1
    gene.append(user_set)

    # Create random length set of permissions
    permission_set = set()
    unusedPermissions = [u for u in range(len(permissionUsage)) if permissionUsage[u]==0]
    if (unusedPermissions):
        permission = random.sample(unusedPermissions,1)[0] # Ensure that user list is not empty and unused users are used first
        permission_set.add(permission)
        permissionUsage[permission] += 1
    for i in range(random.randint(0,len(permissionUsage))):
        permission = random.sample(range(0,len(permissionUsage)),1)[0]
        if (permission not in permission_set):
            permission_set.add(permission)
            permissionUsage[permission] += 1
    if (len(permission_set)==0):
        permission = random.sample(range(0,len(permissionUsage)),1)[0]
        permission_set.add(permission)
        userUsage[user] += 1
    gene.append(permission_set)
    return gene, userUsage, permissionUsage

# -----------------------------------------------------------------------------------
# Generate a random role (gene)
# -----------------------------------------------------------------------------------
def generateGene_unknown(permissions, attributes):
    gene = []
    attr_list = {}
    for attr in list(attributes.keys()):
        if (random.randint(0, 1)):
            randomAttribute = attr
            randomAttributeValue = random.choice(list(attributes[randomAttribute]))
            attr_list[randomAttribute] = randomAttributeValue
    print(attr_list)
    randomPermissions = random.sample(permissions,random.randint(1, len(permissions)))
    print(randomPermissions)
    gene.append["h":randomPermissions]
    print(gene)
    return gene
