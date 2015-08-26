__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# Help functions
# -----------------------------------------------------------------------------------

import random
import numpy
import rm_MatrixOperators as matrixOps

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
    i = len(removalList) - 1
    #print(removalList)
    while i >= 0:
        #print("offspring:\n" + str(offspring))
        del offspring[removalList[i]]
        i = i - 1
    return offspring

def localOptimization(offspring):
    if (True):
        'Combine Users'
        offspring = combineObjects(offspring, 0)
        'Combine Permissions'
        offspring = combineObjects(offspring, 1)
        # print("\nOPTIMIZATION: "+str(offspring))
    return offspring
