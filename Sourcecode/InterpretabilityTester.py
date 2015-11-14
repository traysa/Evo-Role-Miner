__author__ = 'Theresa'

import rm_EAEvaluations as eval
import numpy
import MatrixOperators as matrixOps
import rm_FileParser as parser
import math
import itertools


# ----------------------------------------------------------------------------------------------------------------------
# DATA SETS
# ----------------------------------------------------------------------------------------------------------------------
def getDataSet(DATA):
    Original = []
    userAttributes = []
    userAttributeValues = []
    constraints = []
    URMatrix = None
    RPMatrix = None
    if (DATA=="healthcare"):
        Original = numpy.matrix(parser.read("..\\TestData\\healthcare.rbac"))
    elif (DATA=="testdata"):
        testdata = [[1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 1, 1], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 1, 1], [1, 0, 0, 1, 1]]
        testdata2 = [[3, 3, 0, 0, 0], [2, 0, 0, 2, 2], [1, 0, 1, 1, 1], [2, 0, 0, 2, 2], [2, 0, 0, 2, 2], [4, 3, 0, 2, 2], [2, 0, 0, 2, 2]]
        Original = numpy.matrix(testdata2)
    elif (DATA=="random"):
        Original = matrixOps.generateGoalMatrix(4, 10, 10)
    elif (DATA=="GeneratedData"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151004-191825\\testdata.rbac"))
        userAttributes, userAttributeValues = parser.readUserAttributes("..\\TestData\\Data_20151004-191825\\users.csv")
        #constraints = parser.readConstraints("..\\TestData\\Data_20151004-191825\\constraints.csv")
        #URMatrix
        #RPMatrix
    elif (DATA=="GeneratedData_small"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151005-194203\\testdata.rbac"))
        userAttributes, userAttributeValues = parser.readUserAttributes("..\\TestData\\Data_20151005-194203\\users.csv")
        constraints = parser.readConstraints("..\\TestData\\Data_20151005-194203\\constraints.csv")
        URMatrix = parser.readURAssignments("..\\TestData\\Data_20151005-194203\\UsersToRoles.csv")
        RPMatrix = parser.readRPAssignments("..\\TestData\\Data_20151005-194203\\Roles.csv")
    elif (DATA=="GeneratedData_Set1"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151113-143930_10x10\\testdata.rbac"))
        userAttributes, userAttributeValues = parser.readUserAttributes("..\\TestData\\Data_20151113-143930_10x10\\users.csv")
        #constraints = parser.readConstraints("..\\TestData\\Data_20151113-143930_10x10\\constraints.csv")
        URMatrix = parser.readURAssignments2("..\\TestData\\Data_20151113-143930_10x10\\URMatrix.csv")
        RPMatrix = parser.readRPAssignments("..\\TestData\\Data_20151113-143930_10x10\\RPMatrix.csv")
    return Original, URMatrix, RPMatrix, userAttributeValues, userAttributes, constraints

# ----------------------------------------------------------------------------------------------------------------------
# Silhouette Coefficient for fuzzy role-clusters
# ----------------------------------------------------------------------------------------------------------------------
def calculateSilhouetteCoefficient(roles, userSize, userAttributeValues):
    silhouetteCoefficients = []
    for user in range(0,userSize):
        print("User: "+str(user))
        userCompactnessList = []
        userSeparationList = []

        for role in roles:
            print("Role: "+str(role))
            user_set = role[0]
            print("Users in Role: "+str(user_set))
            sumDist = 0
            for user2 in user_set:
                if (user != user2): #Users are not compared with themselves
                    sumDist += sum(distance(user, user2, userAttributeValues)) #sum up distance between current user and users in the role
            if (user in user_set): #IntraDist
                userCompactnessList.append(sumDist / len(user_set))
                print("IntraDist: "+str(sumDist / len(user_set)))
            else: #InterDist
                userSeparationList.append(sumDist / len(user_set))
                print("InterDist: "+str(sumDist / len(user_set)))
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

# Measures the distance between 2 users according to their user attribute values
def distance(user1, user2, userAttributeValues):
    user1_attributeValues = userAttributeValues[user1]
    user2_attributeValues = userAttributeValues[user2]
    distance = [0 for d in range(0,len(userAttributeValues[0]))]
    for attr,value in enumerate(user1_attributeValues):
        if (value != user2_attributeValues[attr]):
            distance[attr]+=1
    #print("User1: "+str(user1_attributeValues))
    #print("User2: "+str(user2_attributeValues))
    #print("Distance: "+str(distance)+" ==> "+str(sum(distance)))
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

# ----------------------------------------------------------------------------------------------------------------------
# Role-Classifier-Rule
# ----------------------------------------------------------------------------------------------------------------------
def measureRule(rule, D):
    pos = 0
    neg = 0
    cnt = 0
    for d in D:
        i = 0
        notMet = False
        while (not notMet and i < len(rule)-1):
            if (rule[i]!=None and rule[i] != d[i]):
                notMet = True
            i += 1
        if (not notMet):
            cnt +=1
            if (d[-1]==True):
                pos += 1
            else:
                neg += 1
    if (cnt <= 0 or neg >= pos):
        return 1
    measure = 0
    if cnt > 0:
        if (pos > 0):
            measure = -(pos/cnt)*math.log2(pos/cnt)
        if (neg > 0):
            measure += -(neg/cnt)*math.log2(neg/cnt)
    return measure

def Learn_One_Rule(D, Att_vals, rule):
    attributesToConsider = [a for a,c in enumerate(rule) if c == None]
    bestMeasure = 1
    bestRule = ()
    for a in attributesToConsider:
        for attrVal in Att_vals[a]:
            ruleL = list(rule)
            ruleL[a] = attrVal
            measureCurrentRule = measureRule(ruleL,D)
            if (bestMeasure > measureCurrentRule):
                bestMeasure = measureCurrentRule
                bestRule = tuple(ruleL)
    return [bestRule,bestMeasure]

def Learn_Several_Rule(D, Att_vals, rule):
    attributesToConsider = [a for a,c in enumerate(rule) if c == None]
    measures = []
    rules = []
    for a in attributesToConsider:
        for attrVal in Att_vals[a]:
            ruleL = list(rule)
            ruleL[a] = attrVal
            measureCurrentRule = measureRule(ruleL,D)
            rules.append(tuple(ruleL))
            measures.append(measureCurrentRule)
    bestRules = []
    bestMeasure = min(measures)
    if bestMeasure == 1:
        return bestRules
    bestMeasureIndices = [i for i,m in enumerate(measures) if m == bestMeasure]
    for i in bestMeasureIndices:
        bestRules.append([rules[i],measures[i]])
    return bestRules

def applyRule(rule,D):
    notMetByRule = []
    for d in D:
        i = 0
        notMet = False
        while (not notMet and i < len(rule)):
            if (rule[i]!=None and rule[i] != d[i]):
                notMet = True
            i += 1
        if (notMet):
            notMetByRule.append(d)
    return notMetByRule

def sequentialCovering(D, Att_vals, prevRule):
    ruleSet = set()
    stop = False
    while (not stop):
        if rule[1]==1:
            rule = Learn_One_Rule(D, Att_vals, prevRule)
        else:
            rule = Learn_One_Rule(D, Att_vals, rule)
        D = applyRule(rule[0],D)
        ruleSet.add(rule[0])
        NoMoreTuplesInDWithClassC = True
        for d in D:
            NoMoreTuplesInDWithClassC = NoMoreTuplesInDWithClassC and not d[-1]
        stop = NoMoreTuplesInDWithClassC
    return ruleSet


def sequentialCoveringK(D, Att_vals, rule):
    ruleSet = []
    stop = True
    for d in D:
        stop = stop and not d[-1]
    if (not stop):
        #print("D: "+str(D))
        rules = Learn_Several_Rule(D, Att_vals, rule)
        #print("RULES: "+str(rules))
        for rule in rules:
            subrules = sequentialCoveringK(applyRule(rule[0],D),Att_vals,rule[0])
            ruleChain = [rule[0]]
            if (subrules):
                for sr in subrules:
                    ruleChain.append(sr)
                    ruleSet.append(ruleChain)
            else:
                ruleSet.append(ruleChain)
    return ruleSet


def calculateProbabilityInClass(classMembers,rule):
    numberOfMembers = len(classMembers)
    disqualifiedMembers = list()
    counter = 0
    for member in classMembers:
        allAttrSatisfied = True
        attr = 0
        while (allAttrSatisfied and attr < len(rule)):
            if (len(rule[attr])>0):
                if (member[attr] not in rule[attr]):
                    allAttrSatisfied = False
            attr += 1
        if (allAttrSatisfied):
            counter += 1
        else:
            disqualifiedMembers.append(member)
    return counter/numberOfMembers,disqualifiedMembers

def calculateRules(roleMembers,notRoleMembers,allAttrSets):
    ruleSet = list()
    for member in roleMembers:
        memberAttrValueResults = dict()
        for attrSet in allAttrSets:
            stop = False
            for attr in attrSet:
                if ((attr,) in list(memberAttrValueResults.keys()) and memberAttrValueResults[(attr,)][1] <= 0.0):
                    memberAttrValueResults[attrSet] = (None,0.0)
                    stop = True
            if (not stop):
                attrValues = [None,None,None]
                for attr in attrSet:
                    attrValues[attr] = member[attr]
                probabilityInsideRole, disqualifiedMembers = calculateProbabilityInClass(roleMembers,attrValues)
                probabilityOutsideRole = calculateProbabilityInClass(notRoleMembers,attrValues)[0]
                memberAttrValueResults[attrSet] = (probabilityInsideRole,probabilityOutsideRole)
                if (probabilityOutsideRole <= 0.0):
                    if (probabilityInsideRole < 1.0):
                        ruleSet.append(calculateRules(disqualifiedMembers,notRoleMembers,allAttrSets))
                    else:
                        ruleSet.append(tuple(attrValues))
    return ruleSet

def calculateRules2(membersNotConsideredInRule,roleMembers,notRoleMembers,allAttrSets,rule,level):
    print("Level: "+str(level))
    ruleSet = list()
    while (len(membersNotConsideredInRule) > 0):
        member = membersNotConsideredInRule.pop()
        while (len(allAttrSets) > 0):
            attrSet = allAttrSets.pop()
            # Create new rule with current attribute combination
            newRule = [set(),set(),set()]
            for attr in attrSet:
                newRule[attr].add(member[attr])
            # Join previous executed rule with new rule
            for attr,attrValue in enumerate(rule):
                newRule[attr].update(attrValue)
            if (newRule != rule):
                # Get probability of members inside role, when rule is executed
                # Get members from role, which do not fulfill the rule
                probabilityInsideRole, membersNotConsideredInRule = calculateProbabilityInClass(roleMembers,newRule)
                # Get probability of not members outside role, when rule is executed
                probabilityOutsideRole = calculateProbabilityInClass(notRoleMembers,newRule)[0]
                # If no one outside the role fulfills rule
                if (probabilityOutsideRole <= 0.34):
                    # If not everyone inside the role fulfills the rule
                    if (probabilityInsideRole < 0.65):
                        # Try to extend current rule
                        extendedRules = calculateRules2(membersNotConsideredInRule,roleMembers,notRoleMembers,[attrSet],newRule,level+1)
                        if (len(extendedRules)>0):
                            for extendedRule in extendedRules:
                                # If extended rule can be found, which is not fulfilled by one not-member, add the generated rule to result
                                ruleSet.append(extendedRule)
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
                        # If everyone inside the role fulfills rule, add the generated rule to result
                        ruleSet.append((newRule,probabilityInsideRole,probabilityOutsideRole))
                        # To avoid unnecessary rules, remove attribute combinations, which contain all attributes of an existing rule
                        if (probabilityOutsideRole == 0.0 and probabilityInsideRole == 1.0):
                            i = 0
                            while (len(allAttrSets)>0 and i < len(allAttrSets)):
                                x = allAttrSets[i]
                                if set(attrSet).issubset(set(x)):
                                    allAttrSets.remove(x)
                                else:
                                    i+=1

    return ruleSet

def myAlgorithm(D):
    roleMembers = [user for user in D if user[-1]]
    roleMembers2 = [user for user in D if user[-1]]
    notRoleMembers = [user for user in D if not user[-1]]
    ruleSize = 1
    attrSize = len(roleMembers[0])-1
    allAttrSets = []
    for ruleSize in range(1,attrSize+1):
        allAttrSets += list(itertools.combinations(range(0,attrSize), ruleSize))
    allAttrSets.sort(key=lambda t: len(t), reverse=True)

    return roleMembers,calculateRules2(roleMembers2,roleMembers,notRoleMembers,allAttrSets,[set(),set(),set()],0)

def calculateAccuracy(rule, roleMembers, userCnt):
    P = len(roleMembers)
    print("P: "+str(P))
    TP = rule[1]*P
    print("TP: "+str(TP))
    N = userCnt-len(roleMembers)
    print("N: "+str(N))
    TN = (1-rule[2])*N
    print("TN: "+str(TN))
    result = (TP+TN)/(P+N)
    return result

def calculateErrorRate(rule, roleMembers, userCnt):
    P = len(roleMembers)
    FP = rule[2]*P
    print("FP: "+str(FP))
    N = userCnt-len(roleMembers)
    FN = (1-rule[1])*N
    print("FN: "+str(FN))
    result = (FP+FN)/(P+N)
    return result

def calculateSensitivity(rule, roleMembers, userCnt):
    P = len(roleMembers)
    TP = rule[1]*P
    result = TP / P
    return result

def calculateSpecificity(rule, roleMembers, userCnt):
    N = userCnt-len(roleMembers)
    TN = (1-rule[2])*N
    result = TN / N
    return result

def calculatePrecision(rule, roleMembers, userCnt):
    P = len(roleMembers)
    TP = rule[1]*P
    FP = rule[2]*P
    result = TP / (TP+FP)
    return result

# ----------------------------------------------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------------------------------------------
Original, URMatrix, RPMatrix, userAttributes, userAttributeValues, constraints = getDataSet("GeneratedData_small")

# Role-Classifier-Rule
print("Role-Classifier-Rule")
for user in userAttributeValues:
    user.append(False)
for role in range(0,3):
    print("===================================================================")
    for u, user in enumerate(userAttributeValues):
        if (URMatrix[u][role] == 1):
            user[-1] = True
        else:
            user[-1] = False
    #ruleSet = sequentialCovering(userAttributeValues,userAttributes,rule=(None,None,None,True))
    roleMembers,ruleSet = myAlgorithm(userAttributeValues)
    print("ROLE "+str(role)+": "+str(roleMembers))
    for r in ruleSet:
        print("---------------------------------------------------------------")
        print(r)
        print("Accuracy: "+str(calculateAccuracy(r,roleMembers,len(userAttributeValues))))
        print("ErrorRate: "+str(calculateErrorRate(r,roleMembers,len(userAttributeValues))))
        print("Sensitivity (Recall): "+str(calculateSensitivity(r,roleMembers,len(userAttributeValues))))
        print("Specificity: "+str(calculateSpecificity(r,roleMembers,len(userAttributeValues))))
        print("Precision: "+str(calculatePrecision(r,roleMembers,len(userAttributeValues))))

'''# Silhouette Coefficient for fuzzy role-clusters
print("Silhouette Coefficient for fuzzy role-clusters")
rolemodel = [[set(),set()] for role in RPMatrix]
for u,user in enumerate(URMatrix):
    for r,role in enumerate(user):
        if (role==1):
            rolemodel[r][0].update([u])
for r,role in enumerate(RPMatrix):
    for p,permission in enumerate(role):
        if (permission==1):
            rolemodel[r][1].update([p])
userSize = len(URMatrix)
result = avgRoleFitness(rolemodel, userSize, userAttributeValues)
print(result)
'''

