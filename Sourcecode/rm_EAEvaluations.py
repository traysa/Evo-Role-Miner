__author__ = 'Theresa'

import rm_MatrixOperators as matrixOps
import rm_Utils as utils
import numpy

# -----------------------------------------------------------------------------------
# Single Objective Evaluation Functions
# -----------------------------------------------------------------------------------
# Violataions
def evalFunc_Obj1(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    'Violation of confidentiality and data availability'
    conf, accs = utils.compareMatrices(array,orig)
    #numberOfRoles = len(individual[0])
    #return conf, accs, numberOfRoles

    worstCase_accs = orig.sum() # All permissions are assigned directly to user
    bestCase_accs = 0 # No direct assignements required
    range_accs = worstCase_accs-bestCase_accs+1
    accs_normalized = (accs-bestCase_accs+1)/range_accs

    worstCase_conf = orig.size - orig.sum() # All permissions are assigned directly to user
    bestCase_conf = 0 # No direct assignements required
    range_conf = worstCase_conf-bestCase_conf+1
    conf_normalized = (conf-bestCase_conf+1)/range_conf

    temp = (conf_normalized+accs_normalized)
    return temp,

# Number of Roles
def evalFunc_Obj2(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    return numberOfRoles,

# Number of Roles + Violations (from paper)
def evalFunc_Saenko(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    'Violation of confidentiality and data availability'
    conf, accs = utils.compareMatrices(array,orig)
    numberOfRoles = len(individual[0])
    w1 = 0.1
    w2 = 2
    w3 = 1

    worstCase_numberOfRoles = min(userSize,permissionSize)
    bestCase_numberOfRoles = 1
    range_numberOfRoles = worstCase_numberOfRoles-bestCase_numberOfRoles+1
    numberOfRoles_normalized = (numberOfRoles-bestCase_numberOfRoles+1)/range_numberOfRoles

    worstCase_accs = orig.sum() # All permissions are assigned directly to user
    bestCase_accs = 0 # No direct assignements required
    range_accs = worstCase_accs-bestCase_accs+1
    accs_normalized = (accs-bestCase_accs+1)/range_accs

    worstCase_conf = orig.size - orig.sum() # All permissions are assigned directly to user
    bestCase_conf = 0 # No direct assignements required
    range_conf = worstCase_conf-bestCase_conf+1
    conf_normalized = (conf-bestCase_conf+1)/range_conf

    temp = (w1 * numberOfRoles_normalized + w2 * conf_normalized + w3 * accs_normalized)**(-1)
    return temp,

# Number of Roles + Violations as euclidean (from paper)
def evalFunc_Saenko_Euclidean(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    dist = numpy.linalg.norm(array-numpy.matrix(orig,dtype=bool)) #Frobenius norm, also called the Euclidean norm
    numberOfRoles = len(individual[0])
    w1 = 1
    w2 = 10
    temp = (w1 * numberOfRoles + w2 * dist)**(-1)
    return temp,

# Weighted strcutural complexity: Number of Roles + Number of UR + Number of RP + Number of UP
def evalFunc_WSC(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])

    numberOfUR = 0
    for userlists in numpy.array(individual[0])[:,0]:
        numberOfUR += len(userlists)

    numberOfRP = 0
    for permissionlists in numpy.array(individual[0])[:,1]:
        numberOfRP += len(permissionlists)

    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)

    'Violation of confidentiality and data availability'
    conf, accs = utils.compareMatrices(array,orig)
    numberOfUP = accs

    w1 = -1.3
    w2 = 1
    w3 = 1
    w4 = 1
    w5 = 2

    worstCase_numberOfRoles = min(userSize,permissionSize)
    bestCase_numberOfRoles = 1
    range_numberOfRoles = worstCase_numberOfRoles-bestCase_numberOfRoles+1
    numberOfRoles_normalized = (numberOfRoles-bestCase_numberOfRoles+1)/range_numberOfRoles

    worstCase_numberOfUR = userSize * worstCase_numberOfRoles # Each user is assigned to at all roles
    bestCase_numberOfUR = userSize # Each user gets at least 1 role
    range_numberOfUR = worstCase_numberOfUR-bestCase_numberOfUR+1
    numberOfUR_normalized = (numberOfUR-bestCase_numberOfUR+1)/range_numberOfUR

    worstCase_numberOfRP = permissionSize * worstCase_numberOfRoles # Each permission is assigned to at all roles
    bestCase_numberOfRP = permissionSize  # Each permission is assigned to at least 1 role
    range_numberOfRP = worstCase_numberOfRP-bestCase_numberOfRP+1
    numberOfRP_normalized = (numberOfRP-bestCase_numberOfRP+1)/range_numberOfRP

    worstCase_numberOfUP = orig.sum() # All permissions are assigned directly to user
    bestCase_numberOfUP = 0 # No direct assignements required
    range_numberOfUP = worstCase_numberOfUP-bestCase_numberOfUP+1
    numberOfUP_normalized = (numberOfUP-bestCase_numberOfUP+1)/range_numberOfUP

    worstCase_conf = orig.size - orig.sum() # All permissions are assigned directly to user
    bestCase_conf = 0 # No direct assignements required
    range_conf = worstCase_conf-bestCase_conf+1
    conf_normalized = (conf-bestCase_conf+1)/range_conf

    temp = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * numberOfUP_normalized + w5 * conf_normalized)

    print("numberOfRoles: "+str(numberOfRoles))
    print("numberOfUR: "+str(numberOfUR))
    print("numberOfRP: "+str(numberOfRP))
    print("numberOfUP: "+str(numberOfUP))
    print("individual: "+str(individual))
    print("===================================================== TOTAL: "+str(temp))

    return temp,

def evalFunc_Generalization_Error(individual, UPA2):

    return 0

# -----------------------------------------------------------------------------------
# Multi Objective Evaluation Functions
# -----------------------------------------------------------------------------------
def evalFunc_Multi(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    numberOfRoles = len(individual[0])

    worstCase_numberOfRoles = min(userSize,permissionSize)
    bestCase_numberOfRoles = 1
    range_numberOfRoles = worstCase_numberOfRoles-bestCase_numberOfRoles+1
    numberOfRoles_normalized = (numberOfRoles-bestCase_numberOfRoles+1)/range_numberOfRoles

    worstCase_accs = orig.sum() # All permissions are assigned directly to user
    bestCase_accs = 0 # No direct assignements required
    range_accs = worstCase_accs-bestCase_accs+1
    accs_normalized = (accs-bestCase_accs+1)/range_accs

    worstCase_conf = orig.size - orig.sum() # All permissions are assigned directly to user
    bestCase_conf = 0 # No direct assignements required
    range_conf = worstCase_conf-bestCase_conf+1
    conf_normalized = (conf-bestCase_conf+1)/range_conf

    temp = (conf_normalized+accs_normalized)

    return temp, numberOfRoles_normalized

def evalFunc_Multi_EuclideanDistance(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    dist = numpy.linalg.norm(array-numpy.matrix(orig,dtype=bool)) #Frobenius norm, also called the Euclidean norm
    numberOfRoles = len(individual[0])
    return dist, numberOfRoles
