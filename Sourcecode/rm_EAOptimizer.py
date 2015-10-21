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
# Combine roles if they have the same user-lists (permission-lists)
# -----------------------------------------------------------------------------------
def combineObjects(offspring, index):
    log = ""
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
    log += "offspring: "+str(offspring)+"\n"
    log += "offspring len: "+str(len(offspring))+"\n"
    log += "removalList: "+str(removalList)+"\n"
    index = 0
    while removalList:
        try:
            index = removalList.pop()
            log += "remove index: "+str(index)+"\n"
            del offspring[index]
        except IndexError:
            print("offspring: "+str(offspring))
            print("offspring len: "+str(len(offspring)))
            print("removalList: "+str(removalList))
            print("Index: "+str(index))
            print("LOG:\n"+log)
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