__author__ = 'Theresa'

import MatrixOperators as matrixOps
import rm_EADecoder as decoder
import numpy
import itertools
import copy

# -----------------------------------------------------------------------------------
# RoleModel measures
# - Number of Roles
# - Confidentiality Violations
# - Availability Violations
# - Interpretability
# -----------------------------------------------------------------------------------
def roleModelMeasures(rolemodel, userSize, permissionSize, orig, userAttributeValues=[]):
    numberOfRoles = len(rolemodel)

    array = decoder.resolveRoleModelChromosomeIntoBoolArray(rolemodel, userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)

    interp = 0
    if (userAttributeValues):
        userAttributeValuesWithClass = copy.deepcopy(userAttributeValues)
        for user in userAttributeValuesWithClass:
            user.append(False)
        interp = measureInterpretability(rolemodel, userAttributeValuesWithClass)

    numberOfUR = 0
    for userlists in numpy.array(rolemodel)[:,0]:
        numberOfUR += len(userlists)

    numberOfRP = 0
    for permissionlists in numpy.array(rolemodel)[:,1]:
        numberOfRP += len(permissionlists)

    return conf, accs, numberOfRoles, numberOfUR, numberOfRP, interp

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Violation of confidentiality
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Confidentiality(individual, userSize, permissionSize, orig, userAttributeValues=[], constraints=[]):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_conf = orig.size - orig.sum()
        fitness = worstCase_conf
    else:
        fitness = conf
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Violation of availability
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Availability(individual, userSize, permissionSize, orig, userAttributeValues=[], constraints=[]):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_accs = orig.sum()
        fitness = worstCase_accs
    else:
        fitness = accs
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Confidentiality and Accessibility Violations
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Violations(individual, userSize, permissionSize, orig, userAttributeValues=[], constraints=[]):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = 3
        fitness = worstCase_fitness
    else:
        worstCase_accs = orig.sum() # All permissions are assigned directly to user
        bestCase_accs = 0 # No direct assignements required
        range_accs = worstCase_accs-bestCase_accs+1
        accs_normalized = (accs-bestCase_accs+1)/range_accs

        worstCase_conf = orig.size - orig.sum() # All permissions are assigned directly to user
        bestCase_conf = 0 # No direct assignements required
        range_conf = worstCase_conf-bestCase_conf+1
        conf_normalized = (conf-bestCase_conf+1)/range_conf

        fitness = (conf_normalized+accs_normalized)

    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Average confidentiality violations of all roles
# -----------------------------------------------------------------------------------
def evalFunc_AvgRoleConfViolations(individual, userSize, permissionSize, orig, userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_conf = orig.size - orig.sum()
        fitness = worstCase_conf
    else:
        sumOfRoleConfViolations = 0
        for r in range(0,numberOfRoles):
            role_array = decoder.resolveGeneIntoBoolArray(individual[0][r], userSize, permissionSize)
            role_conf, role_accs = matrixOps.compareMatrices(role_array,orig)
            sumOfRoleConfViolations += role_conf
        fitness = sumOfRoleConfViolations/numberOfRoles

    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Average confidentiality violations of all roles and
# Availability Violations of the RoleModel
# -----------------------------------------------------------------------------------
def evalFunc_AvgRoleConfViolations_Availability(individual, userSize, permissionSize, orig,userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = 3
        fitness = worstCase_fitness
    else:
        sumOfRoleConfViolations = 0
        for r in range(0,numberOfRoles):
            role_array = decoder.resolveGeneIntoBoolArray(individual[0][r], userSize, permissionSize)
            role_conf, role_accs = matrixOps.compareMatrices(role_array,orig)
            sumOfRoleConfViolations += role_conf
        avgRoleConfViolation = sumOfRoleConfViolations/numberOfRoles

        worstCase_avgRoleConfViolation = orig.size - orig.sum()
        bestCase_avgRoleConfViolation = 0
        range_avgRoleConfViolation = worstCase_avgRoleConfViolation-bestCase_avgRoleConfViolation+1
        avgRoleConfViolation_normalized = (avgRoleConfViolation-bestCase_avgRoleConfViolation+1)/range_avgRoleConfViolation

        worstCase_accs = orig.sum() # All permissions are assigned directly to user
        bestCase_accs = 0 # No direct assignements required
        range_accs = worstCase_accs-bestCase_accs+1
        accs_normalized = (accs-bestCase_accs+1)/range_accs

        fitness = avgRoleConfViolation_normalized + accs_normalized
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_RoleCnt(individual, userSize, permissionSize, orig, userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles
    else:
        fitness = numberOfRoles
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_URCnt(individual, userSize, permissionSize, orig, userAttributeValues=[], constraints=[]):
    numberOfUR = 0
    for userlists in numpy.array(individual[0])[:,0]:
        numberOfUR += len(userlists)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles
    else:
        fitness = numberOfUR
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_RPCnt(individual, userSize, permissionSize, orig, userAttributeValues=[], constraints=[]):
    numberOfRP = 0
    for permissionlists in numpy.array(individual[0])[:,1]:
        numberOfRP += len(permissionlists)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_numberOfRoles = min(userSize,permissionSize)
        fitness = worstCase_numberOfRoles
    else:
        fitness = numberOfRP
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Interpretability
# Interpretability is the average Role Fitness (calculation based on Generalized Intra-Inter Silhouette Index)
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Interpretability(individual, userSize, permissionSize, orig, userAttributeValues, constraints=[]):
    interp = 0
    if (userAttributeValues):
        userAttributeValuesWithClass = copy.deepcopy(userAttributeValues)
        for user in userAttributeValuesWithClass:
            user.append(False)
        interp = measureInterpretability(individual[0], userAttributeValuesWithClass)
    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_interp = 0
        fitness = worstCase_interp
    else:
        fitness = interp
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Saenko(individual, userSize, permissionSize, orig, weights, userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = 0
        fitness = worstCase_fitness
    else:
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

    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Saenko(individual, userSize, permissionSize, orig, weights, userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = 0
        fitness = worstCase_fitness
    else:
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

    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Number of Roles + Violations (Eucledean distance)
# With Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Saenko_Euclidean(individual, userSize, permissionSize, orig, weights, userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = 0
        fitness = worstCase_fitness
    else:
        array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
        dist = numpy.linalg.norm(array-numpy.matrix(orig,dtype=bool)) #Frobenius norm, also called the Euclidean norm
        w1 = weights[0]
        w2 = weights[1]
        fitness = (w1 * numberOfRoles + w2 * dist)**(-1)
    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC = Number of Roles + Number of UR + Number of RP + Number of UP
# With Normalization
# WSC = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP
# -----------------------------------------------------------------------------------
def evalFunc_WSC(individual, userSize, permissionSize, orig, weights, userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)

    numberOfUR = 0
    for userlists in numpy.array(individual[0])[:,0]:
        numberOfUR += len(userlists)

    numberOfRP = 0
    for permissionlists in numpy.array(individual[0])[:,1]:
        numberOfRP += len(permissionlists)

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = len(weights)
        fitness = worstCase_fitness
    else:
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

    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC* = Number of Roles + Number of UR + Number of RP +
# Number of UP + Number of Confidentiality violations
# With Normalization
# WSC* = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP + w5 * conf
# -----------------------------------------------------------------------------------
def evalFunc_WSC_Star(individual, userSize, permissionSize, orig, weights,userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)

    numberOfUR = 0
    for userlists in numpy.array(individual[0])[:,0]:
        numberOfUR += len(userlists)

    numberOfRP = 0
    for permissionlists in numpy.array(individual[0])[:,1]:
        numberOfRP += len(permissionlists)

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = len(weights)
        fitness = worstCase_fitness
    else:
        numberOfUP = accs

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]
        w4 = weights[3]
        w5 = weights[4]

        worstCase_numberOfRoles = min(userSize,permissionSize)
        bestCase_numberOfRoles = 1
        range_numberOfRoles = worstCase_numberOfRoles-bestCase_numberOfRoles
        numberOfRoles_normalized = (numberOfRoles-bestCase_numberOfRoles)/range_numberOfRoles

        worstCase_numberOfUR = userSize * worstCase_numberOfRoles # Each user is assigned to at all roles
        bestCase_numberOfUR = userSize # Each user gets at least 1 role
        range_numberOfUR = worstCase_numberOfUR-bestCase_numberOfUR
        numberOfUR_normalized = (numberOfUR-bestCase_numberOfUR)/range_numberOfUR

        worstCase_numberOfRP = permissionSize * worstCase_numberOfRoles # Each permission is assigned to at all roles
        bestCase_numberOfRP = permissionSize  # Each permission is assigned to at least 1 role
        range_numberOfRP = worstCase_numberOfRP-bestCase_numberOfRP
        numberOfRP_normalized = (numberOfRP-bestCase_numberOfRP)/range_numberOfRP

        worstCase_numberOfUP = orig.sum() # All permissions are assigned directly to user
        bestCase_numberOfUP = 0 # No direct assignements required
        range_numberOfUP = worstCase_numberOfUP-bestCase_numberOfUP
        numberOfUP_normalized = (numberOfUP-bestCase_numberOfUP)/range_numberOfUP

        worstCase_conf = orig.size - orig.sum() # All permissions are assigned directly to user
        bestCase_conf = 0 # No direct assignements required
        range_conf = worstCase_conf-bestCase_conf
        conf_normalized = (conf-bestCase_conf)/range_conf

        fitness = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * numberOfUP_normalized + w5 * conf_normalized)

    return fitness

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC* = Number of Roles + Number of UR + Number of RP +
# Number of UP + Number of Confidentiality violations
# With Normalization
# WSC* = w1 * numberOfRoles + w2 * numberOfUR + w3 * numberOfRP + w4 * numberOfUP + w5 * conf + w6 * roleDis
# -----------------------------------------------------------------------------------
def evalFunc_WSC_Star_RoleDis(individual, userSize, permissionSize, orig, weights, population,userAttributeValues=[], constraints=[]):
    numberOfRoles = len(individual[0])
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(individual[0], userSize, permissionSize)
    conf, accs = matrixOps.compareMatrices(array,orig)

    numberOfUR = 0
    for userlists in numpy.array(individual[0])[:,0]:
        numberOfUR += len(userlists)

    numberOfRP = 0
    for permissionlists in numpy.array(individual[0])[:,1]:
        numberOfRP += len(permissionlists)

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = len(weights)
        fitness = worstCase_fitness
    else:
        count = 0
        for rm in population:
            count += len(rm[0])
        numberOfRolesInPop = count/len(population)
        roleDis = abs(numberOfRolesInPop-numberOfRoles)
        if (roleDis < 3):
            roleDis = 0

        numberOfUP = accs

        w1 = weights[0]
        w2 = weights[1]
        w3 = weights[2]
        w4 = weights[3]
        w5 = weights[4]
        w6 = weights[5]

        worstCase_numberOfRoles = min(userSize,permissionSize)
        bestCase_numberOfRoles = 1
        range_numberOfRoles = worstCase_numberOfRoles-bestCase_numberOfRoles
        numberOfRoles_normalized = (numberOfRoles-bestCase_numberOfRoles)/range_numberOfRoles

        worstCase_numberOfUR = userSize * worstCase_numberOfRoles # Each user is assigned to at all roles
        bestCase_numberOfUR = userSize # Each user gets at least 1 role
        range_numberOfUR = worstCase_numberOfUR-bestCase_numberOfUR
        numberOfUR_normalized = (numberOfUR-bestCase_numberOfUR)/range_numberOfUR

        worstCase_numberOfRP = permissionSize * worstCase_numberOfRoles # Each permission is assigned to at all roles
        bestCase_numberOfRP = permissionSize  # Each permission is assigned to at least 1 role
        range_numberOfRP = worstCase_numberOfRP-bestCase_numberOfRP
        numberOfRP_normalized = (numberOfRP-bestCase_numberOfRP)/range_numberOfRP

        worstCase_numberOfUP = orig.sum() # All permissions are assigned directly to user
        bestCase_numberOfUP = 0 # No direct assignements required
        range_numberOfUP = worstCase_numberOfUP-bestCase_numberOfUP
        numberOfUP_normalized = (numberOfUP-bestCase_numberOfUP)/range_numberOfUP

        worstCase_conf = orig.size - orig.sum() # All permissions are assigned directly to user
        bestCase_conf = 0 # No direct assignements required
        range_conf = worstCase_conf-bestCase_conf
        conf_normalized = (conf-bestCase_conf)/range_conf

        worstCase_roleDis = max(numberOfRolesInPop,permissionSize-numberOfRolesInPop,userSize-numberOfRolesInPop)
        bestCase_roleDis = 0
        range_roleDis = worstCase_roleDis-bestCase_roleDis
        roleDis_normalized = (roleDis-bestCase_roleDis)/range_roleDis

        fitness = (w1 * numberOfRoles_normalized + w2 * numberOfUR_normalized + w3 * numberOfRP_normalized + w4 * numberOfUP_normalized + w5 * conf_normalized + w6 * roleDis_normalized)

    return fitness



# -----------------------------------------------------------------------------------
# Single Objective Evaluation: WSC* + Interpretability
# WSC* = Number of Roles + Number of UR + Number of RP + Number of UP + Number of Confidentiality violations
# Interpretability = average Role Fitness (calculation based on Generalized Intra-Inter Silhouette Index)
# -----------------------------------------------------------------------------------
def evalFunc_WSC_INT(individual, userSize, permissionSize, orig, weights, userAttributeValues, constraints=[]):
    fitness = evalFunc_WSC_Star(individual, userSize, permissionSize, orig, weights[:-1],userAttributeValues=userAttributeValues)

    interp = 0
    if (userAttributeValues):
        userAttributeValuesWithClass = copy.deepcopy(userAttributeValues)
        for user in userAttributeValuesWithClass:
            user.append(False)
        interp = measureInterpretability(individual[0], userAttributeValuesWithClass)

    if (constraints and not feasible(individual, userSize, permissionSize, constraints)):
        worstCase_fitness = len(weights)
        fitness = worstCase_fitness
    else:
        int_weight = weights[-1]
        fitness += int_weight * (1-interp)
    return fitness


# -----------------------------------------------------------------------------------
# Silhouette Coefficient for fuzzy role-clusters
# -----------------------------------------------------------------------------------
def calculateSilhouetteCoefficient(roles, userSize, userAttributeValues):
    silhouetteCoefficients = []
    for user in range(0,userSize):
        userCompactnessList = []
        userSeparationList = []
        for role in roles:
            user_set = role[0]
            sumDist = 0
            for user2 in user_set:
                if (user != user2):
                    sumDist += distance(user, user2, userAttributeValues)
            if (user in user_set): #IntraDist
                userCompactnessList.append(sumDist / len(user_set))
            else: #InterDist
                userSeparationList.append(sumDist / len(user_set))
        if (userCompactnessList):
            userCompactnessDistance = min(userCompactnessList)
        else:
            userCompactnessDistance = 0
        if (userSeparationList):
            userSeparationsDistance = min(userSeparationList)
        else:
            userSeparationsDistance = 0
        if (userCompactnessDistance==0 and userSeparationsDistance==0):
            silhouetteCoefficients.append(0)
        else:
            silhouetteCoefficients.append((userSeparationsDistance-userCompactnessDistance)/max(userCompactnessDistance,userSeparationsDistance))

    return silhouetteCoefficients

def distance(user1, user2, userAttributeValues):
    user1_attributeValues = userAttributeValues[user1]
    user2_attributeValues = userAttributeValues[user2]
    distance = 0
    for attr,value in enumerate(user1_attributeValues):
        if (value != user2_attributeValues[attr]):
            distance+=1
    return distance

def avgSilhouetteCoefficient(roles, userSize, userAttributeValues):
    silhouetteCoefficients = calculateSilhouetteCoefficient(roles, userSize, userAttributeValues)
    avgSilhouetteCoefficient = sum(silhouetteCoefficients) / float(len(silhouetteCoefficients))
    return avgSilhouetteCoefficient

def avgRoleFitness(roles, userSize, userAttributeValues):
    silhouetteCoefficients = calculateSilhouetteCoefficient(roles, userSize, userAttributeValues)
    sumRoleFitness = 0
    for role in roles:
        user_set = role[0]
        sumSilhouetteCoefficients = 0
        for user in user_set:
            sumSilhouetteCoefficients += silhouetteCoefficients[user]
        sumRoleFitness += sumSilhouetteCoefficients/len(user_set)
    avgRoleFitness = sumRoleFitness / len(roles)

    return avgRoleFitness

# -----------------------------------------------------------------------------------
# Accuracy and Coverage for classifier rules
# -----------------------------------------------------------------------------------
def calculateProbabilityInClass(classMembers,rule):
    numberOfMembers = len(classMembers)
    disqualifiedMembers = list()
    if numberOfMembers==0:
        return 0, disqualifiedMembers
    counter = 0
    for member in classMembers:
        oneRuleSatisfied = False
        r_OR = 0
        while (not oneRuleSatisfied and r_OR < len(rule)):
            attr = 0
            rule_OR = rule[r_OR]
            allAttrSatisfied = True
            while(allAttrSatisfied and attr < len(rule_OR)):
                if (len(rule_OR[attr])>0):
                    if (member[attr] not in rule_OR[attr]):
                        allAttrSatisfied = False
                attr += 1
            if (allAttrSatisfied):
                oneRuleSatisfied = True
            r_OR += 1
        if (oneRuleSatisfied):
            counter += 1
        else:
            disqualifiedMembers.append(member)
    return counter/numberOfMembers,disqualifiedMembers

def ruleInduction(membersNotConsideredInRule,roleMembers,notRoleMembers,current_rule,current_ruleSize,max_ruleSize):
    attrSize = len(roleMembers[0])-1
    allAttrSets = []
    for ruleSize in range(1,attrSize+1):
        allAttrSets += list(itertools.combinations(range(0,attrSize), ruleSize))
    allAttrSets.sort(key=lambda t: len(t), reverse=True)
    ruleSet = list()
    while (len(membersNotConsideredInRule) > 0):
        member = membersNotConsideredInRule.pop()
        while (len(allAttrSets) > 0):
            attrSet = allAttrSets.pop()
            # Create new rule with current attribute combination
            rule_AND = []
            newRule_OR = [set() for a in range(0,attrSize)]
            for attr in attrSet:
                newRule_OR[attr].add(member[attr])
            if (len(current_rule) > 0):
                for rule_OR in current_rule:
                    rule_AND.append(rule_OR)
            rule_AND.append(newRule_OR)
            # Get probability of none-members outside role, which fulfill the rule
            probabilityOutsideRole = calculateProbabilityInClass(notRoleMembers,rule_AND)[0]
            # If only few outside the role fulfills the rule
            if (probabilityOutsideRole <= (1/3)):
                # Get probability of members inside role, which fulfill the rule
                # Get members from role, which do not fulfill the rule
                probabilityInsideRole, membersNotConsideredInRule = calculateProbabilityInClass(roleMembers,rule_AND)
                # If not everyone inside the role fulfills the rule, search for another OR-Rule
                if (probabilityInsideRole < (2/3)):
                    if (current_ruleSize < max_ruleSize):
                        # Try to extend current rule
                        extendedRules = ruleInduction(membersNotConsideredInRule,roleMembers,notRoleMembers,rule_AND,current_ruleSize+1,max_ruleSize)
                        if (len(extendedRules)>0):
                            for extendedRule in extendedRules:
                                # If extended rule can be found, which is not fulfilled by one none-member, add the generated rule to result
                                ruleSet.append(extendedRule)
                                # To avoid unnecessary rules, remove attribute combinations, which contain all attributes of an existing rule
                                if (extendedRule[2] == 0.0 and extendedRule[1] == 1.0):
                                    i = 0
                                    while (len(allAttrSets)>0 and i < len(allAttrSets)):
                                        x = allAttrSets[i]
                                        if set(attrSet).issubset(set(x)):
                                            allAttrSets.remove(x)
                                        else:
                                            i+=1
                else:
                    # If everyone inside the role fulfills rule, add the generated rule to result
                    ruleSet.append((rule_AND,probabilityInsideRole,probabilityOutsideRole))
                    #print("Add rule: "+str(rule_AND))
                    # To avoid unnecessary rules, remove attribute combinations, which contain all attributes of an existing rule
                    if (probabilityOutsideRole == 0.0 and probabilityInsideRole == 1.0):
                        i = 0
                        while (len(allAttrSets)>0 and i < len(allAttrSets)):
                            x = allAttrSets[i]
                            if set(attrSet).issubset(set(x)):
                                allAttrSets.remove(x)
                            else:
                                i+=1
            else:
                # If too many outside the role fulfill the rule, the rule is discarded
                # and membersNotConsideredInRule is resetted #
                rule_AND.remove(newRule_OR)

    return ruleSet

def measureInterpretability(rolemodel, userAttributeValues):
    measure = 0
    userCnt = len(userAttributeValues)
    for role in rolemodel:
        for u,user in enumerate(userAttributeValues):
            user[-1] = (u in role[0])
        roleMembers = [user for user in userAttributeValues if user[-1]]
        roleMembers2 = [user for user in userAttributeValues if user[-1]]
        notRoleMembers = [user for user in userAttributeValues if not user[-1]]
        max_ruleSize = 0
        current_ruleSize = 0
        current_rule = []
        ruleSet = ruleInduction(roleMembers2,roleMembers,notRoleMembers,current_rule,current_ruleSize,max_ruleSize)
        rule = 0
        bestAccuracy = 0.0
        while (rule < len(ruleSet) and bestAccuracy < 1.0):
            accuracy = calculateAccuracy(ruleSet[rule], roleMembers, userCnt)
            if accuracy > bestAccuracy:
                bestAccuracy = accuracy
            rule += 1
        measure += bestAccuracy
    measure = measure/len(rolemodel)
    return measure

def calculateAccuracy(rule, roleMembers, userCnt):
    P = len(roleMembers)
    #print("P: "+str(P))
    TP = rule[1]*P
    #print("TP: "+str(TP))
    N = userCnt-len(roleMembers)
    #print("N: "+str(N))
    TN = (1-rule[2])*N
    #print("TN: "+str(TN))
    result = (TP+TN)/(P+N)
    return result

# -----------------------------------------------------------------------------------
# Multi Objective Evaluation: Number of Roles + Violations
# -----------------------------------------------------------------------------------
def evalFunc_Multi(individual, userSize, permissionSize, orig, evalFunc):
    fitness = ()
    for obj in evalFunc:
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
