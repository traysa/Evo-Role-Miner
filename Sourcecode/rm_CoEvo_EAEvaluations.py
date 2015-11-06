__author__ = 'Theresa'

import MatrixOperators as matrixOps
import rm_CoEvo_EADecoder as decoder
import numpy
import random
import rm_EAEvaluations as base

# -----------------------------------------------------------------------------------
# Evaluation.
# A set of u neurons is selected randomly from the population to form a hidden layer
# of a feed- forward network. The network is submitted to a trial in which it is
# evaluated on the task and awarded a fitness score. The score is added to the
# cumulative fitness of each neuron that participated in the network. This process is
# repeated until each neuron has participated in an average of e.g. 10 trials.
#
# Recombination.
# The average fitness of each neuron is calculated by dividing its cumulative fitness
# by the number of trials in which it participated. Neurons are then ranked by
# average fitness. Each neuron in the top quartile is recombined with a
# higher-ranking neuron using 1-point crossover and mutation at low levels to create
# the offspring to replace the lowest-ranking half of the population.
#
# -----------------------------------------------------------------------------------
def evaluation(population, numberOfTrialItems, Original):
    for ind in population:
        ind.fitness.values = (0,)

    trialReport = [0 for i in population]
    #print(trialReport)
    stop = False
    trialnumber = 0

    while not stop:
        trialnumber += 1
        #print("Trial: "+str(trialnumber))
        pick = random.sample(range(0,len(population)),numberOfTrialItems)
        individuals = [population[i] for i in pick]
        trial(individuals, Original)
        for i in pick:
            trialReport[i] += 1
        #print(trialReport)
        stop = all(i >= 10 for i in trialReport)

    for i,ind in enumerate(population):
        ind.fitness.values = (list(ind.fitness.values)[0]/trialReport[i]),

    return trialnumber

def trial(individuals, Original):
    violations = evalFunc_Violations(individuals, Original)
    for ind in individuals:
        ind.fitness.values = (list(ind.fitness.values)[0] + violations),
        temp = 0
    return individuals

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Confidentiality
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Confidentiality(individuals, orig):
    array = decoder.resolveRoleChromosomesIntoBoolArray(individuals,int(orig.shape[0]), int(orig.shape[1]))
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    return conf

# -----------------------------------------------------------------------------------
# Single Objective Evaluation: Interpretability
# Interpretability is the average Role Fitness (calculation based on Generalized Intra-Inter Silhouette Index)
# No Normalization
# -----------------------------------------------------------------------------------
def evalFunc_Interpretability(individuals, userSize, permissionSize, orig, userAttributeValues):

    return fitness
