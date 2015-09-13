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
                matrix[user - 1][permission - 1] = 1
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
                if (matrix[user - 1][permission - 1] == 0):
                    matrix[user - 1][permission - 1] += gene+1
                else:
                    matrix[user - 1][permission - 1] = len(chromosome)+1
    return matrix

# -----------------------------------------------------------------------------------
# Resolves a chromosome into an UR-matrix, RP-matrix and integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveChromosomeIntoArrays(chromosome, userSize, permissionSize):

    UMatrix = matrixOps.createEmptyMatrix(userSize, len(chromosome))
    for gene in range(0, len(chromosome)):
        user_list = chromosome[gene][0]
        for user in user_list:
            UMatrix[user - 1][gene] = 1

    PMatrix = matrixOps.createEmptyMatrix(len(chromosome),permissionSize)
    for gene in range(0, len(chromosome)):
        permission_list = chromosome[gene][1]
        for permission in permission_list:
            PMatrix[gene][permission - 1] = 1

    UPMatrix = resolveChromosomeIntoArray2(chromosome, userSize, permissionSize)

    return UMatrix, PMatrix, UPMatrix

# -----------------------------------------------------------------------------------
# Generate a random gene (role)
# -----------------------------------------------------------------------------------
def generateGene(userSize, permissionSize):
    gene = []
    # Create random length list of users
    user_list = []
    for i in range(1, userSize + 1):
        if (random.randint(0, 1)):
            user_list.append(i)
    if (len(user_list) < 1):
        user_list.append(random.randint(1, userSize))
    gene.append(user_list)
    # Create random length list of permissions
    permisson_list = []
    for i in range(1, permissionSize + 1):
        if (random.randint(0, 1)):
            permisson_list.append(i)
    if (len(permisson_list) < 1):
        permisson_list.append(random.randint(1, permissionSize))
    gene.append(permisson_list)
    return gene

# -----------------------------------------------------------------------------------
# Combine roles if they have the same user-lists (permission-lists)
# -----------------------------------------------------------------------------------
def combineObjects(offspring, index):
    values = numpy.array(offspring)[:, index]
    removalList = []
    # print("\nUSER COMBINING: "+str(values))
    for x, left in enumerate(values):
        for y, right in enumerate(values[x:]):
            if ((y + x not in removalList) & (x != y + x) & (len(left) == len(right)) & (
                        len(left) == (len(set(left) & set(right))))):
                # print("USER COMBINING: item%s in %s has %s values in common with item%s" % (x, values, len(left), y + x))
                offspring[x][1] = list(set(offspring[x][1]) | set(offspring[y + x][1]))
                offspring[y + x][0] = []
                removalList.append(y + x)
    removalList.sort()
    i = len(removalList) - 1
    #print(removalList)
    while i >= 0:
        #print("offspring:\n" + str(offspring))
        try:
            del offspring[removalList[i]]
        except IndexError:
            temp = 0
            raise
        i = i - 1
    return offspring

# -----------------------------------------------------------------------------------
# Local optimization by user combining and permission combining
# -----------------------------------------------------------------------------------
def localOptimization(offspring):
    if (True):
        'Combine Users'
        offspring = combineObjects(offspring, 0)
        'Combine Permissions'
        offspring = combineObjects(offspring, 1)
        # print("\nOPTIMIZATION: "+str(offspring))
    return offspring
