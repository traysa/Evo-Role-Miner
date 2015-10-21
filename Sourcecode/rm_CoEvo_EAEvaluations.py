__author__ = 'Theresa'

import rm_MatrixOperators as matrixOps
import rm_EADecoder as decoder
import numpy

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Violation of confidentiality
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Confidentiality(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    return conf,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Violation of availability
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Availability(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    return accs,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No  Normalization
# -----------------------------------------------------------------------------------
def evalFunc_RoleCnt(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    return numberOfRoles,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Confidentiality and Accessibility Violations
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Violations(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.compareMatrices(array,orig)
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

    fitness = (conf_normalized+accs_normalized)

    return fitness,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Saenko(individual, userSize, permissionSize, orig, weights):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.compareMatrices(array,orig)
    numberOfRoles = len(individual[0])
    w1 = weights[0]
    w2 = weights[1]
    w3 = weights[2]

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

    fitness = (w1 * numberOfRoles_normalized + w2 * conf_normalized + w3 * accs_normalized)**(-1)
    return fitness,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations (Eucledean distance)
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Saenko_Euclidean(individual, userSize, permissionSize, orig, weights):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    dist = numpy.linalg.norm(array-numpy.matrix(orig,dtype=bool)) #Frobenius norm, also called the Euclidean norm
    numberOfRoles = len(individual[0])
    w1 = weights[0]
    w2 = weights[1]
    fitness = (w1 * numberOfRoles + w2 * dist)**(-1)
    return fitness,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC = Number of Roles + Number of UR + Number of RP + Number of UP
# With Normalization
# WSC = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP
# -----------------------------------------------------------------------------------
def evalFunc_WSC(individual, userSize, permissionSize, orig, weights):
    numberOfRoles = len(individual[0])

    numberOfUR = 0
    for userlists in numpy.array(individual[0])[:,0]:
        numberOfUR += len(userlists)

    numberOfRP = 0
    for permissionlists in numpy.array(individual[0])[:,1]:
        numberOfRP += len(permissionlists)

    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)

    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.compareMatrices(array,orig)
    numberOfUP = accs

    w1 = weights[0]
    w2 = weights[1]
    w3 = weights[2]
    w4 = weights[3]

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

    fitness = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * numberOfUP_normalized)

    return fitness,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC* = Number of Roles + Number of UR + Number of RP +
# Number of UP + Number of Confidentiality violations
# With Normalization
# WSC* = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP + w5 * conf
# -----------------------------------------------------------------------------------
def evalFunc_WSC_Star(individual, userSize, permissionSize, orig, weights):
    numberOfRoles = len(individual[0])

    numberOfUR = 0
    for userlists in numpy.array(individual[0])[:,0]:
        numberOfUR += len(userlists)

    numberOfRP = 0
    for permissionlists in numpy.array(individual[0])[:,1]:
        numberOfRP += len(permissionlists)

    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)

    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.compareMatrices(array,orig)
    numberOfUP = accs

    w1 = weights[0]
    w2 = weights[1]
    w3 = weights[2]
    w4 = weights[3]
    w5 = weights[4]

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

    fitness = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * numberOfUP_normalized + w5 * conf_normalized)

    '''print("numberOfRoles: "+str(numberOfRoles))
    print("numberOfUR: "+str(numberOfUR))
    print("numberOfRP: "+str(numberOfRP))
    print("numberOfUP: "+str(numberOfUP))
    print("individual: "+str(individual))
    print("===================================================== TOTAL: "+str(temp))'''

    return fitness,conf,accs,numberOfRoles

# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
def evalFunc_Generalization_Error(individual, UPA2):

    return 0

# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
def evalFunc_AvgRoleViolations(individual, userSize, permissionSize, orig):

    return 0

# -----------------------------------------------------------------------------------
# Multi Objective Evaluation: Number of Roles + Violations
# -----------------------------------------------------------------------------------
def evalFunc_Multi(individual, userSize, permissionSize, orig, objectives):
    fitness = ()
    for obj in objectives:
        if (obj=="Confidentiality"):
            fitness+= (evalFunc_Confidentiality(individual, userSize, permissionSize, orig)[0],)
        elif (obj=="Availability"):
            fitness+= (evalFunc_Availability(individual, userSize, permissionSize, orig)[0],)
        elif (obj=="RoleCnt"):
            fitness+= (evalFunc_RoleCnt(individual, userSize, permissionSize, orig)[0],)
        elif (obj=="Violations"):
            fitness+= (evalFunc_Violations(individual, userSize, permissionSize, orig)[0],)
        else:
            raise ValueError("Evaluation function for '"+obj+"' not known")
    return fitness

# -----------------------------------------------------------------------------------
# Multi Objective Evaluation: Number of Roles + Violations (Eucledean distance)
# -----------------------------------------------------------------------------------
def evalFunc_Multi_EuclideanDistance(individual, userSize, permissionSize, orig):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    dist = numpy.linalg.norm(array-numpy.matrix(orig,dtype=bool)) #Frobenius norm, also called the Euclidean norm
    numberOfRoles = len(individual[0])
    return dist, numberOfRoles
