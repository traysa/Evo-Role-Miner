__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# Help functions
# -----------------------------------------------------------------------------------

import random
import numpy
import rm_MatrixOperators as matrixOps


# -----------------------------------------------------------------------------------
# Data Generation for RoleMiner
# -----------------------------------------------------------------------------------
def generateGoalMatrix(roles, users, permissions):
    A = matrixOps.createRandomMatrix(users, roles)
    B = matrixOps.createRandomMatrix(roles, permissions)
    C = matrixOps.multiplyBoolMatrix(A, B)
    return C

# -----------------------------------------------------------------------------------
# Resolves a chromosome into an boolean UP-matrix
# -----------------------------------------------------------------------------------
def resolveChromosomeIntoArray(chromosome, userSize, permissionSize):
    matrix = matrixOps.createEmptyMatrix(userSize, permissionSize)
    # Iterate through all genes of a chromosome
    for gene in range(0, len(chromosome)):
        # print("Gene: " +str(gene))
        # print(chromosome[gene])
        user_list = chromosome[gene][0]
        permission_list = chromosome[gene][1]
        for user in user_list:
            for permission in permission_list:
                matrix[user][permission] = 1
    return matrix

# -----------------------------------------------------------------------------------
# Resolves a chromosome into an integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveChromosomeIntoArray2(chromosome, userSize, permissionSize):
    matrix = matrixOps.createEmptyMatrix(userSize, permissionSize)
    # Iterate through all genes of a chromosome
    for gene in range(0, len(chromosome)):
        # print("Gene: " +str(gene))
        # print(chromosome[gene])
        user_list = chromosome[gene][0]
        permission_list = chromosome[gene][1]
        for user in user_list:
            for permission in permission_list:
                matrix[user][permission] += 1
                #if (matrix[user][permission] == 0):
                #    matrix[user][permission] += 1 #gene+1
                #else:
                #    matrix[user][permission] += 1 #len(chromosome)+1
    return matrix

# -----------------------------------------------------------------------------------
# Resolves a chromosome into an UR-matrix, RP-matrix and integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveChromosomeIntoArrays(chromosome, userSize, permissionSize):

    UMatrix = matrixOps.createEmptyMatrix(userSize, len(chromosome))
    for gene in range(0, len(chromosome)):
        user_set = chromosome[gene][0]
        for user in user_set:
            UMatrix[user][gene] = 1
    #print("\nUMatrix")
    #print(UMatrix)

    PMatrix = matrixOps.createEmptyMatrix(len(chromosome),permissionSize)
    for gene in range(0, len(chromosome)):
        permission_list = chromosome[gene][1]
        for permission in permission_list:
            PMatrix[gene][permission] = 1
    #print("\nPMatrix")
    #print(PMatrix)

    UPMatrix = resolveChromosomeIntoArray2(chromosome, userSize, permissionSize)
    #print("\nUPMatrix")
    #print(UPMatrix)

    return UMatrix, PMatrix, UPMatrix

# -----------------------------------------------------------------------------------
# Resolves individuals into an boolean UP-matrix
# -----------------------------------------------------------------------------------
def resolveIndividualsIntoArray(individuals, userSize, permissionSize):
    matrix = matrixOps.createEmptyMatrix(userSize, permissionSize)
    for ind in individuals:
        user_list = ind[0][0]
        permission_list = ind[0][1]
        for user in user_list:
            for permission in permission_list:
                matrix[user][permission] = 1
    return matrix

# -----------------------------------------------------------------------------------
# Resolves a chromosome into an UR-matrix, RP-matrix and integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveIndividualsIntoArrays(individuals, userSize, permissionSize):

    UMatrix = matrixOps.createEmptyMatrix(userSize, len(individuals))
    for i,ind in enumerate(individuals):
        user_list = ind[0][0]
        for user in user_list:
            UMatrix[user][i] = 1

    PMatrix = matrixOps.createEmptyMatrix(len(individuals),permissionSize)
    for i,ind in enumerate(individuals):
        permission_list = ind[0][1]
        for permission in permission_list:
            PMatrix[i][permission] = 1

    UPMatrix = resolveIndividualsIntoArray(individuals, userSize, permissionSize)

    return UMatrix, PMatrix, UPMatrix

# -----------------------------------------------------------------------------------
# Generate a random gene (role)
# -----------------------------------------------------------------------------------
def generateGene(userSize, permissionSize):
    gene = []
    # Create random length list of users
    user_list = []
    for i in range(0, userSize):
        if (random.randint(0, 1)):
            user_list.append(i)
    if (len(user_list) < 1):
        user_list.append(random.randint(0, userSize))
    gene.append(user_list)
    # Create random length list of permissions
    permission_list = []
    for i in range(0, permissionSize):
        if (random.randint(0, 1)):
            permission_list.append(i)
    if (len(permission_list) < 1):
        permission_list.append(random.randint(0, permissionSize))
    gene.append(permission_list)
    return gene

def generateGene3(userUsage, permissionUsage):
    gene = []
    # Create random length list of users
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

    # Create random length list of permissions
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

def generateGene2(permissions, attributes):
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

# -----------------------------------------------------------------------------------
# Combine roles if they have the same user-lists (permission-lists)
# -----------------------------------------------------------------------------------
def combineObjects(offspring, index):
    values = numpy.array(offspring)[:, index]
    removalSet = set()
    # print("\nUSER COMBINING: "+str(values))
    for x, left in enumerate(values):
        for y, right in enumerate(values[x+1:]):
            if ((y+1+x) not in removalSet and len(left ^ right)==0):
                offspring[x][index] = offspring[x][index] | offspring[y+1 + x][index]
                offspring[y+1 + x][index] = set()
                removalSet.add(y+1 + x)
    removalList = list(removalSet)
    sorted(removalList)
    if (len(removalList) > 1):
        temp = 0
    while removalList:
        try:
            del offspring[removalList.pop()]
        except IndexError:
            temp = 0
            raise
    return offspring


# -----------------------------------------------------------------------------------
# Local optimization by user combining and permission combining
# -----------------------------------------------------------------------------------
def localOptimization(offspring):
    if (True):
        'Combine Permissions'
        offspring = combineObjects(offspring, 1)
        'Combine Users'
        offspring = combineObjects(offspring, 0)

        # print("\nOPTIMIZATION: "+str(offspring))
        #'Remove similar Genes'
        #offspring = removeSimilarGenes(offspring)
    return offspring

def compareMatrices(MatrixA,MatrixB):
    diffMatrix = matrixOps.subtractIntMatrix(A=numpy.matrix(MatrixA,dtype=bool), B=numpy.matrix(MatrixB,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    return conf, accs