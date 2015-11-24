__author__ = 'Theresa'

import os, pickle, numpy
from deap import creator, base, tools, algorithms
import rm_Statistics as statistics
import rm_FileParser as parser
import rm_Visualization as visual
import rm_EAEvaluations as evals
import nsga2_classic as nsga2
from collections import defaultdict

# -----------------------------------------------------------------------------------
# Read population pickle file
# -----------------------------------------------------------------------------------
def populationReader(populationFile):
    creator.create("FitnessMinMax", base.Fitness, weights=(-1.0,))  # MINIMIZATION
    creator.create("Individual", list, fitness=creator.FitnessMinMax)
    cp = pickle.load(open(populationFile, "rb"))
    population = cp["population"]
    return population

# -----------------------------------------------------------------------------------
# Read population pickle file
# -----------------------------------------------------------------------------------
def populationReader_Multi(populationFile):
    creator.create("FitnessMinMax", base.Fitness, weights=(-1.0,-1.0))  # MINIMIZATION
    creator.create("Individual", list, fitness=creator.FitnessMinMax)
    cp = pickle.load(open(populationFile, "rb"))
    population = cp["population"]
    return population

# -----------------------------------------------------------------------------------
# Print statistics of a population
# -----------------------------------------------------------------------------------
def printStatistics(population, OriginalFile, topk=1):
    Original = numpy.matrix(parser.read(OriginalFile))
    #top_inds = population
    top_inds = tools.selNSGA2(population, k=topk)
    i = 0
    for top_ind in top_inds:
        conf = statistics.Conf(top_ind[0],Original)
        accs = statistics.Accs(top_ind[0],Original)
        roleCnt = statistics.RoleCnt(top_ind[0])
        urCnt = statistics.URCnt(top_ind[0])
        rpCnt = statistics.RPCnt(top_ind[0])
        print("\nTOP INDIVIDUAL: "+str(i))
        print("conf: "+str(conf))
        print("accs: "+str(accs))
        print("roleCnt: "+str(roleCnt))
        print("urCnt: "+str(urCnt))
        print("rpCnt: "+str(rpCnt))
        i+=1

def getIndWithLowestRoleCnt(population, OriginalFile, topk=1):
    Original = numpy.matrix(parser.read(OriginalFile))
    #top_inds = population
    toplist = []
    for ind in population:
        roleCnt = statistics.RoleCnt(ind[0])
        if (len(toplist) <= topk):
            toplist.append([roleCnt,ind])
            toplist.sort(key=lambda tup: tup[0])
        else:
            if (roleCnt < toplist[0][0]):
                toplist[0] = [roleCnt,ind]
                toplist.sort(key=lambda tup: tup[0])

    for t in toplist:
        print(str(t[0])+":\t"+str(t[1]))

def getIndWithLowestURRPCnt(population, OriginalFile, topk=1):
    Original = numpy.matrix(parser.read(OriginalFile))
    #top_inds = population
    toplist = []
    for ind in population:
        count = statistics.URCnt(ind[0])+statistics.RPCnt(ind[0])
        if (len(toplist) <= topk):
            toplist.append([count,ind])
            toplist.sort(key=lambda tup: tup[0])
        else:
            if (count < toplist[0][0]):
                toplist[0] = [count,ind]
                toplist.sort(key=lambda tup: tup[0])

    for t in toplist:
        print(str(t[0])+":\t"+str(t[1]))

# -----------------------------------------------------------------------------------
# Read URMatrix from csv of generated dataset
# -----------------------------------------------------------------------------------
def urMatrixReader(filename, outputFile):
    UPMatrix = numpy.matrix(parser.read(filename))
    visual.visualizeUPMatrix(UPMatrix,)

# -----------------------------------------------------------------------------------
# Count UPA of generated dataset
# -----------------------------------------------------------------------------------
def countUPA(filename):
    UPMatrix = numpy.matrix(parser.readURMatrix(filename))
    print(UPMatrix.sum())

# -----------------------------------------------------------------------------------
# Draw pareto front of population
# -----------------------------------------------------------------------------------
def drawPareto(population, output_filename):
    evalFunc=["Confidentiality","Availability"]
    results = defaultdict(list)
    for ind in population:
        results[1].append(ind.fitness.values)
    generations = 1
    freq = 1
    visual.showFitnessInPlotForMultiObjective(results, generations, freq, output_filename, "First Population", "Info", evalFunc)

populationFile = "..\\Output\\EXPERIMENTS\\Experiments - Phase 3\\Healthcare\\Setup2_FEdgeMin\\Populations\\3_3_Populations\\Generation_1000_population.pkl"
OriginalFile = "..\\TestData\\healthcare.rbac"
#population = populationReader(populationFile)
#printStatistics(population,OriginalFile,1)

filename = "..\\TestData\\emea.rbac"
outputFile = "..\\TestData\\emea"
#urMatrixReader(filename, outputFile)

filename = "..\\TestData\\GeneratedData_Set2\\UPMatrix.csv"
#countUPA(filename)

populationFile = "..\\Output\\20151124-1629_EXP_Multi\\Multi_Conf_Accs\\Populations\\1_1_Populations\\Generation_1000_population.pkl"
output_filename = "..\\Output\\lastpopulation"
OriginalFile = "..\\TestData\\GeneratedData_Set1\\URMatrix.csv"
OriginalFile = "..\\TestData\\healthcare.rbac"
population = populationReader_Multi(populationFile)

front = nsga2.sortNondominated(population, len(population), first_front_only=True)

printStatistics(front[0],OriginalFile,10)
#getIndWithLowestRoleCnt(population,OriginalFile,10)
#getIndWithLowestURRPCnt(population,OriginalFile,10)
drawPareto(population,output_filename)


