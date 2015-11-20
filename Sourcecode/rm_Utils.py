__author__ = 'Theresa'

import json
import pickle
import os
import itertools
import rm_Visualization as visual
import logging
logger = logging.getLogger('root')

# -----------------------------------------------------------------------------------
# Normaliztion Function
# -----------------------------------------------------------------------------------
def normalization(value,bestCase,worstCase):
    return (value-bestCase+1)/(worstCase-bestCase+1)

# -----------------------------------------------------------------------------------
# Save role count diversity in JSON file
# -----------------------------------------------------------------------------------
def saveDiversity(gen,population,filename):
    individualBuckets = dict()
    for ind in population:
        roleCnt = len(ind[0])
        if roleCnt not in individualBuckets:
            individualBuckets[roleCnt] = [ind]
        else:
            individualBuckets[roleCnt].append(ind)
    entryList = dict()
    entryList["gen"] = gen
    for roleCnt in individualBuckets:
        entryList[roleCnt] = len(individualBuckets[roleCnt])
        logger.debug("RoleCnt="+str(roleCnt)+" Individuals: "+str(len(individualBuckets[roleCnt])))
    with open(filename, "w") as outfile:
        json.dump(entryList, outfile, indent=4)
        outfile.close()

# -----------------------------------------------------------------------------------
# Save all individuals of a population in a pickle file
# -----------------------------------------------------------------------------------
def savePopulation(gen,population,filename):
    cp = dict(population=population)
    pickle.dump(cp, open(filename, "wb"), 2)

# -----------------------------------------------------------------------------------
# Plot role count diversity for a generation in a boxplot
# -----------------------------------------------------------------------------------
def printDiversity(pop_folder,freq):
    json_files = [pos_json for pos_json in os.listdir(pop_folder) if pos_json.endswith('_diversity.json')]
    cnt_jsonFiles = len(json_files)
    logger.debug("json_files: "+str(cnt_jsonFiles))
    logger.debug(json_files)
    data = [[] for g in range(0,cnt_jsonFiles)]
    gen_labels = [str(g*freq) for g in range(0,cnt_jsonFiles)]
    for js in json_files:
        with open(os.path.join(pop_folder, js)) as json_file:
            gen_data = json.load(json_file)
            generation = int(gen_data.pop('gen'))
            data_list = []
            for item in gen_data:
                for cnt in range(0,int(gen_data[item])):
                    data_list.append(float(item))
            data[int(generation/freq)]=data_list
            json_file.close()

    freq2 = int(cnt_jsonFiles / 10)
    visual.diversityBoxplot(gen_labels[0::freq2],data[0::freq2],pop_folder+"\\diversity_boxplot")

# -----------------------------------------------------------------------------------
# Build individual out of URMatrix and RPMatrix
# -----------------------------------------------------------------------------------
def buildIndividual(URMatrix,RPMatrix):
    roleCnt = len(RPMatrix)
    rolemodel = [[set(),set()] for role in range(0,roleCnt)]
    for u,user in enumerate(URMatrix):
        for r,role in enumerate(user):
            if (role==1):
                rolemodel[r][0].update({u})
    for r,role in enumerate(RPMatrix):
        for p,permission in enumerate(role):
            if (permission==1):
                rolemodel[r][1].update({p})
    return rolemodel

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

