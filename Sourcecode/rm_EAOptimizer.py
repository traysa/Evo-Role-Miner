__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# Help functions
# -----------------------------------------------------------------------------------

import random
import numpy

# -----------------------------------------------------------------------------------
# Combine roles if they have the same user-lists (permission-lists)
# -----------------------------------------------------------------------------------
def combineObjects(offspring, index):
    #print("Before optimization: "+str(offspring))
    values = numpy.array(offspring)[:, index]
    removalSet = set()
    # print("\nUSER COMBINING: "+str(values))
    for x, left in enumerate(values):
        for y, right in enumerate(values[x+1:]):
            if ((y+1+x) not in removalSet and len(left ^ right)==0):
                offspring[x][abs(index-1)] = offspring[x][abs(index-1)] | offspring[y+1 + x][abs(index-1)]
                offspring[y+1 + x][abs(index-1)] = set()
                removalSet.add(y+1 + x)
    removalList = list(removalSet)
    removalList.sort()
    while removalList:
        index = removalList.pop()
        del offspring[index]
    #print("After optimization: "+str(offspring))
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
