__author__ = 'Theresa'

import os, pickle, numpy
from deap import creator, base, tools, algorithms
import rm_Statistics as statistics
import rm_FileParser as parser
import rm_Visualization as visual

def populationReader(populationFile, OriginalFile):
    creator.create("FitnessMinMax", base.Fitness, weights=(-1.0,))  # MINIMIZATION
    creator.create("Individual", list, fitness=creator.FitnessMinMax)

    cp = pickle.load(open(populationFile, "rb"))
    population = cp["population"]

    Original = numpy.matrix(parser.read(OriginalFile))

    #top_inds = population
    top_inds = tools.selBest(population, k=1)
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

populationFile = "..\\Output\\EXPERIMENTS\\Experiments - Phase 3\\Healthcare\\Setup2_FEdgeMin\\Populations\\3_3_Populations\\Generation_1000_population.pkl"
OriginalFile = "..\\TestData\\healthcare.rbac"
populationReader(populationFile,OriginalFile)

