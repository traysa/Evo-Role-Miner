__author__ = 'Theresa'

import MatrixOperators as matrixOps
import rm_EADecoder as decoder
import numpy
import rm_Utils as utils
import rm_Statistics as statistics

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Violation of confidentiality
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Confidentiality(individual, Original, constraints=[]):
    conf = statistics.Conf(individual[0], Original)
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_conf = Original.size - Original.sum()
        fitness = worstCase_conf
    else:
        fitness = conf
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Violation of availability
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Availability(individual, Original, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    accs = statistics.Accs(individual[0], Original)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_accs = Original.sum()
        fitness = worstCase_accs
    else:
        fitness = accs
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Confidentiality and Accessibility Violations
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Violations(individual, Original, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,Original)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = 3
        fitness = worstCase_fitness
    else:
        '''worstCase_accs = Original.sum() # All permissions are assigned directly to user
        bestCase_accs = 0 # No direct assignements required
        range_accs = worstCase_accs-bestCase_accs+1
        accs_normalized = (accs-bestCase_accs+1)/range_accs

        worstCase_conf = Original.size - Original.sum() # All permissions are assigned directly to user
        bestCase_conf = 0 # No direct assignements required
        range_conf = worstCase_conf-bestCase_conf+1
        conf_normalized = (conf-bestCase_conf+1)/range_conf

        fitness = (conf_normalized+accs_normalized)'''
        fitness = (conf+accs)

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Average confidentiality violations of all roles
# -----------------------------------------------------------------------------------
def evalFunc_AvgRoleConfViolations(individual, Original, constraints=[]):
    numberOfRoles = len(individual[0])
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_conf = Original.size - Original.sum()
        fitness = worstCase_conf
    else:
        sumOfRoleConfViolations = 0
        for r in range(0,numberOfRoles):
            role_array = decoder.resolveGeneIntoBoolArray(individual[0][r], userSize, permissionSize)
            role_conf, role_accs = matrixOps.compareMatrices(role_array,Original)
            sumOfRoleConfViolations += role_conf
        fitness = sumOfRoleConfViolations/numberOfRoles
    return fitness,


# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Average confidentiality violations of all roles and
# Availability Violations of the RoleModel
# -----------------------------------------------------------------------------------
def evalFunc_AvgRoleConfViolations_Availability(individual, Original, constraints=[]):
    numberOfRoles = len(individual[0])
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    accs = statistics.Accs(individual[0], Original)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = 3
        fitness = worstCase_fitness
    else:
        sumOfRoleConfViolations = 0
        for r in range(0,numberOfRoles):
            role_array = decoder.resolveGeneIntoBoolArray(individual[0][r], userSize, permissionSize)
            role_conf, role_accs = matrixOps.compareMatrices(role_array,Original)
            sumOfRoleConfViolations += role_conf
        avgRoleConfViolation = sumOfRoleConfViolations/numberOfRoles

        worstCase_avgRoleConfViolation = Original.size - Original.sum()
        bestCase_avgRoleConfViolation = 0
        range_avgRoleConfViolation = worstCase_avgRoleConfViolation-bestCase_avgRoleConfViolation+1
        avgRoleConfViolation_normalized = (avgRoleConfViolation-bestCase_avgRoleConfViolation+1)/range_avgRoleConfViolation

        worstCase_accs = Original.sum() # All permissions are assigned directly to user
        bestCase_accs = 0 # No direct assignements required
        range_accs = worstCase_accs-bestCase_accs+1
        accs_normalized = (accs-bestCase_accs+1)/range_accs

        fitness = avgRoleConfViolation_normalized + accs_normalized

    return fitness,


# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_RoleCnt(individual, Original, constraints=[]):
    numberOfRoles = len(individual[0])
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles
    else:
        fitness = numberOfRoles

    return fitness,


# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_URCnt(individual, Original, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    numberOfUR = statistics.URCnt(individual[0])
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles
    else:
        fitness = numberOfUR
    return fitness,


# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_RPCnt(individual, Original, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    numberOfRP = statistics.RPCnt(individual[0])
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles
    else:
        fitness = numberOfRP
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_AssignmentCnt(individual, Original, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles*2
    else:
        numberOfUR = statistics.URCnt(individual[0])
        numberOfRP = statistics.RPCnt(individual[0])
        fitness = numberOfUR+numberOfRP
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Conf_AssignmentCnt(individual, Original, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles*2
    else:
        numberOfUR = statistics.URCnt(individual[0])
        numberOfRP = statistics.RPCnt(individual[0])
        conf = statistics.Conf(individual[0], Original)
        fitness = conf+numberOfUR+numberOfRP
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Interpretability
# Interpretability is the average Role Fitness (calculation based on Generalized Intra-Inter Silhouette Index)
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Int_AssignmentCnt(individual, Original, userAttributeValues, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_interp = 1
        fitness = worstCase_interp
    else:
        AssignmentCnt = statistics.URCnt(individual[0])+statistics.RPCnt(individual[0])
        AssignmentCnt_normalized = utils.normalization(AssignmentCnt,userSize+permissionSize,userSize * permissionSize)
        interp = statistics.Interp(individual[0],userAttributeValues)
        fitness = AssignmentCnt_normalized-interp+1
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Interpretability
# Interpretability is the average Role Fitness (calculation based on Generalized Intra-Inter Silhouette Index)
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Interpretability(individual, Original, userAttributeValues, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    interp = statistics.Interp(individual[0],userAttributeValues)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_interp = 1
        fitness = worstCase_interp
    else:
        fitness = abs(interp*(-1))
    return fitness,


# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations
# With Normalization
# Maximization function
# 3 weights
# -----------------------------------------------------------------------------------
def evalFunc_FBasic(individual, Original, weights, constraints=[]):
    numberOfRoles = len(individual[0])
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,Original)

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = 0
    else:
        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]

        numberOfRoles_normalized = utils.normalization(numberOfRoles,1,min(userSize,permissionSize))
        accs_normalized = utils.normalization(accs,0,Original.sum())
        conf_normalized = utils.normalization(conf,0,Original.size - Original.sum())

        fitness = (w1 * numberOfRoles_normalized + w2 * conf_normalized + w3 * accs_normalized)**(-1)

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations
# With Normalization
# Minimization function
# 3 weights
# -----------------------------------------------------------------------------------
def evalFunc_FBasicMin(individual, Original, weights, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = len(weights)
    else:
        numberOfRoles = len(individual[0])
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        conf, accs = matrixOps.compareMatrices(array,Original)

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]

        numberOfRoles_normalized = utils.normalization(numberOfRoles,1,min(userSize,permissionSize))
        accs_normalized = utils.normalization(accs,0,Original.sum())
        conf_normalized = utils.normalization(conf,0,Original.size - Original.sum())

        fitness = w1 * numberOfRoles_normalized + w2 * conf_normalized + w3 * accs_normalized

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of UA and PA + Violations
# With Normalization
# Maximization function
# 3 weights
# -----------------------------------------------------------------------------------
def evalFunc_FEdge(individual, Original, weights, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = 0
    else:
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        conf, accs = matrixOps.compareMatrices(array,Original)
        numberOfUR = statistics.URCnt(individual[0])
        numberOfRP = statistics.RPCnt(individual[0])

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]

        worstCase_numberOfRoles = min(userSize,permissionSize)
        accs_normalized = utils.normalization(accs,0,Original.sum())
        conf_normalized = utils.normalization(conf,0,Original.size - Original.sum())
        numberOfUR_normalized = utils.normalization(numberOfUR,userSize,userSize * worstCase_numberOfRoles)
        numberOfRP_normalized = utils.normalization(numberOfRP,permissionSize,permissionSize * worstCase_numberOfRoles)

        fitness = (w1 * (numberOfUR_normalized+numberOfRP_normalized) + w2 * conf_normalized + w3 * accs_normalized)**(-1)

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of UA and PA + Violations
# With Normalization
# Minimization function
# 3 weights
# -----------------------------------------------------------------------------------
def evalFunc_FEdgeMin(individual, Original, weights, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = len(weights)
    else:
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        conf, accs = matrixOps.compareMatrices(array,Original)
        numberOfUR = statistics.URCnt(individual[0])
        numberOfRP = statistics.RPCnt(individual[0])

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]

        worstCase_numberOfRoles = min(userSize,permissionSize)
        accs_normalized = utils.normalization(accs,0,Original.sum())
        conf_normalized = utils.normalization(conf,0,Original.size - Original.sum())
        numberOfUR_normalized = utils.normalization(numberOfUR,userSize,userSize * worstCase_numberOfRoles)
        numberOfRP_normalized = utils.normalization(numberOfRP,permissionSize,permissionSize * worstCase_numberOfRoles)

        fitness = w1 * (numberOfUR_normalized+numberOfRP_normalized) + w2 * conf_normalized + w3 * accs_normalized

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations (Eucledean distance)
# With Normalization
# 2 weights
# -----------------------------------------------------------------------------------
def evalFunc_Saenko_Euclidean(individual, Original, weights, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = 0
    else:
        numberOfRoles = len(individual[0])
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        dist = numpy.linalg.norm(array-numpy.matrix(Original,dtype=bool)) #Frobenius norm, also called the Euclidean norm
        w1 = weights[0]
        w2 = weights[1]
        fitness = (w1 * numberOfRoles + w2 * dist)**(-1)
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC = Number of Roles + Number of UR + Number of RP + Number of UP
# With Normalization
# WSC = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP
# 4 weights
# -----------------------------------------------------------------------------------
def evalFunc_WSC(individual, Original, weights, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = len(weights)
    else:
        numberOfRoles = len(individual[0])
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        conf, accs = matrixOps.compareMatrices(array,Original)
        numberOfUR = statistics.URCnt(individual[0])
        numberOfRP = statistics.RPCnt(individual[0])

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]
        w4 = weights[3]

        worstCase_numberOfRoles = min(userSize,permissionSize)
        numberOfRoles_normalized = utils.normalization(numberOfRoles,1,worstCase_numberOfRoles)
        accs_normalized = utils.normalization(accs,0,Original.sum())
        numberOfUR_normalized = utils.normalization(numberOfUR,userSize,userSize * worstCase_numberOfRoles)
        numberOfRP_normalized = utils.normalization(numberOfRP,permissionSize,permissionSize * worstCase_numberOfRoles)

        fitness = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * accs_normalized)

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC* = Number of Roles + Number of UR + Number of RP +
# Number of UP + Number of Confidentiality violations
# With Normalization
# WSC* = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP + w5 * conf
# 5 weights
# -----------------------------------------------------------------------------------
def evalFunc_WSC_Star(individual, Original, weights, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = len(weights)
    else:
        numberOfRoles = len(individual[0])
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        conf, accs = matrixOps.compareMatrices(array,Original)
        numberOfUR = statistics.URCnt(individual[0])
        numberOfRP = statistics.RPCnt(individual[0])

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]
        w4 = weights[3]
        w5 = weights[4]

        worstCase_numberOfRoles = min(userSize,permissionSize)
        numberOfRoles_normalized = utils.normalization(numberOfRoles,1,worstCase_numberOfRoles)
        accs_normalized = utils.normalization(accs,0,Original.sum())
        conf_normalized = utils.normalization(conf,0,Original.size - Original.sum())
        numberOfUR_normalized = utils.normalization(numberOfUR,userSize,userSize * worstCase_numberOfRoles)
        numberOfRP_normalized = utils.normalization(numberOfRP,permissionSize,permissionSize * worstCase_numberOfRoles)

        fitness = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * accs_normalized + w5 * conf_normalized)

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC* = Number of Roles + Number of UR + Number of RP +
# Number of UP + Number of Confidentiality violations
# With Normalization
# WSC* = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP + w5 * conf + w6 * roleDis
# 6 weights
# -----------------------------------------------------------------------------------
def evalFunc_WSC_Star_RoleDis(individual, Original, weights, population, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = len(weights)
    else:
        numberOfRoles = len(individual[0])
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        conf, accs = matrixOps.compareMatrices(array,Original)
        numberOfUR = statistics.URCnt(individual[0])
        numberOfRP = statistics.RPCnt(individual[0])

        count = 0
        for rm in population:
            count += len(rm[0])
        numberOfRolesInPop = count/len(population)
        roleDis = abs(numberOfRolesInPop-numberOfRoles)
        if (roleDis < 3):
            roleDis = 0

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]
        w4 = weights[3]
        w5 = weights[4]
        w6 = weights[5]

        worstCase_numberOfRoles = min(userSize,permissionSize)
        numberOfRoles_normalized = utils.normalization(numberOfRoles,1,worstCase_numberOfRoles)
        accs_normalized = utils.normalization(accs,0,Original.sum())
        conf_normalized = utils.normalization(conf,0,Original.size - Original.sum())
        numberOfUR_normalized = utils.normalization(numberOfUR,userSize,userSize * worstCase_numberOfRoles)
        numberOfRP_normalized = utils.normalization(numberOfRP,permissionSize,permissionSize * worstCase_numberOfRoles)
        roleDis_normalized = utils.normalization(roleDis,0,max(numberOfRolesInPop,permissionSize-numberOfRolesInPop,userSize-numberOfRolesInPop))

        fitness = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * accs_normalized + w5 * conf_normalized + w6 * roleDis_normalized)

    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: FBasicMin + Interpretability
# With Normalization
# Minimization function
# 4 weights
# -----------------------------------------------------------------------------------
def evalFunc_FBasicMin_INT(individual, Original, weights, userAttributeValues, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = len(weights)
    else:
        fitness = evalFunc_FBasicMin(individual, Original, weights[:-1])
        interp = statistics.Interp(individual[0],userAttributeValues)

        int_weight = weights[-1]

        fitness = fitness[0] + int_weight * (1-interp)
    return fitness,

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: FEdgeMin + Interpretability
# With Normalization
# Minimization function
# 4 weights
# -----------------------------------------------------------------------------------
def evalFunc_FEdgeMin_INT(individual, Original, weights, userAttributeValues, constraints=[]):
    userSize = Original.shape[0]
    permissionSize = Original.shape[1]
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        fitness = len(weights)
    else:
        fitness = evalFunc_FEdgeMin(individual, Original, weights[:-1])
        interp = statistics.Interp(individual[0],userAttributeValues)

        int_weight = weights[-1]

        fitness = fitness[0] + int_weight * (1-interp)
    return fitness,

# -----------------------------------------------------------------------------------
# Multi Objective Evaluation: Number of Roles + Violations
# -----------------------------------------------------------------------------------
def evalFunc_Multi(individual, Original, evalFunc, userAttributeValues=[], constraints=[]):
    fitness = ()
    for obj in evalFunc:
        if (obj=="Confidentiality"):
            fitness+= (evalFunc_Confidentiality(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="Availability"):
            fitness+= (evalFunc_Availability(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="RoleCnt"):
            fitness+= (evalFunc_RoleCnt(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="Violations"):
            fitness+= (evalFunc_Violations(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="AvgRoleConf_A"):
            fitness+= (evalFunc_AvgRoleConfViolations_Availability(individual,  Original=Original, constraints=constraints)[0],)
        elif (obj=="URCnt"):
            fitness+= (evalFunc_URCnt(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="RPCnt"):
            fitness+= (evalFunc_RPCnt(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="AssignmentCnt"):
            fitness+= (evalFunc_AssignmentCnt(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="Conf_AssignmentCnt"):
            fitness+= (evalFunc_Conf_AssignmentCnt(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="Int_AssignmentCnt"):
            fitness+= (evalFunc_Int_AssignmentCnt(individual, Original=Original, userAttributeValues=userAttributeValues, constraints=constraints)[0],)
        elif (obj=="AvgRoleConf"):
            fitness+= (evalFunc_AvgRoleConfViolations(individual, Original=Original, constraints=constraints)[0],)
        elif (obj=="Interpretability"):
            fitness+= (evalFunc_Interpretability(individual, Original=Original, userAttributeValues=userAttributeValues, constraints=constraints)[0],)
        else:
            raise ValueError("Evaluation function for '"+obj+"' not known")
    return fitness

# -----------------------------------------------------------------------------------
# Feasability of an individual for penalty
# Feasability function for the individual. Returns True if feasible False otherwise.
# -----------------------------------------------------------------------------------
def feasible(individual, userSize, permissionSize, constraints):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    for c in constraints:
        permission1 = numpy.matrix(array)[:,c[0]]
        permission2 = numpy.matrix(array)[:,c[1]]
        for u in range(0,userSize):
            if (bool(permission1[u]) and bool(permission2[u])):
                return False
    return True
