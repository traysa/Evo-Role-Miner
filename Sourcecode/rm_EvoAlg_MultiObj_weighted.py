__author__ = 'Theresa'

import random
import numpy
from deap import creator, base, tools
import pickle
import os.path
import datetime
import fortin2013_weighted
import nsga2_weighted
import rm_EAOperators as operators
import rm_EAInitialization as init
import rm_EAEvaluations as evals
import rm_Statistics as statistics
from collections import defaultdict
import rm_Utils as utils
import logging
logger = logging.getLogger('root')

# -----------------------------------------------------------------------------------
# Evolutionary algorithm - Multi objective with weights
# -----------------------------------------------------------------------------------
def evolution_multi_weighted(Original, evalFunc, populationSize, obj_weights, CXPB, addRolePB, removeRolePB,
                             removeUserPB, removePermissionPB, addUserPB, addPermissionPB, NGEN, freq, numberTopRoleModels,
                             optimization, fortin=False, untilSolutionFound=False, pickleFile="", checkpoint=False, prevFiles="",
                             userAttributeValues=[], constraints=[], printPopulations=False, pop_directory="",fixedRoleCnt=0):

    # Validations
    if (len(evalFunc)<2):
        raise ValueError("Less than 2 objectives not possible")
    if (len(evalFunc)>3):
        raise ValueError("More than 3 objectives not supported")
    if (not(populationSize % 4 == 0)):
        raise ValueError("Population size has to be a multiple of 4")

    logger.debug("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    population = []

    # Create Logbook
    logbook = tools.Logbook()

    # Register Optimization
    weights = ()
    for obj in evalFunc:
        if (obj=="FBasic" or obj=="FEdge"):
            weights+=(1.0,)
        else:
            weights+=(-1.0,)
    creator.create("FitnessMinMax", base.Fitness, weights=weights)
    creator.create("Individual", list, fitness=creator.FitnessMinMax)
    probabilitiesForObjectives = obj_weights

    # Get Checkpoint
    '''if (checkpoint and len(prevFiles)!=0):
        prevFile = prevFiles[0]
        if (os.path.isfile(prevFile)):
            print("Read checkpoint...")
            cp = pickle.load(open(prevFile, "rb"))
            population = cp["population"]
            genStart = int(cp["generation"])
            Original = cp["Original"]
            results=cp["results"]
            time=cp["time"]
            prevFiles=cp["prevFiles"]
            prevFiles.append(prevFile)
            logbook=cp["logbook"]
            random.setstate(cp["rndstate"])
            print("DONE.\n")
        else:
            print("Checkpoint file does not exit")
    else:
        print("Use checkpoint: False")
        checkpoint = False'''

    userSize = int(Original.shape[0])
    permissionSize = int(Original.shape[1])

    # Toolbox
    toolbox = base.Toolbox()
    # Chromosome generator
    toolbox.register("chromosome", init.generateChromosome, userSize, userSize, permissionSize, optimization=optimization, fixedRoleCnt=fixedRoleCnt)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    toolbox.register("evaluate", evals.evalFunc_Multi, Original=Original, evalFunc=evalFunc, userAttributeValues=userAttributeValues, constraints=constraints)

    toolbox.register("mate", operators.mateFunc, optimization=optimization)
    toolbox.register("mutate", operators.mutFunc, addRolePB=addRolePB,
              removeRolePB=removeRolePB,
              removeUserPB=removeUserPB,
              removePermissionPB=removePermissionPB,
              addUserPB=addUserPB,
              addPermissionPB=addPermissionPB, userSize=userSize, permissionSize=permissionSize,
              optimization=[optimization,optimization])

    if (fortin):
        toolbox.register("preselect", fortin2013_weighted.selTournamentFitnessDCD, probabilitiesForObjectives=probabilitiesForObjectives)
        toolbox.register("select", fortin2013_weighted.selNSGA2, probabilitiesForObjectives=probabilitiesForObjectives)
    else:
        toolbox.register("preselect", nsga2_weighted.selTournamentDCD, probabilitiesForObjectives=probabilitiesForObjectives)
        toolbox.register("select", nsga2_weighted.selNSGA2, probabilitiesForObjectives=probabilitiesForObjectives)

    # Register statistics
    statsConf = tools.Statistics(key=lambda ind: statistics.Conf(ind[0],Original))
    statsAccs = tools.Statistics(key=lambda ind: statistics.Accs(ind[0],Original))
    statsRoleCnt = tools.Statistics(key=lambda ind: statistics.RoleCnt(ind[0]))
    statsURCnt = tools.Statistics(key=lambda ind: statistics.URCnt(ind[0]))
    statsRPCnt = tools.Statistics(key=lambda ind: statistics.RPCnt(ind[0]))
    statsInterp = tools.Statistics(key=lambda ind: statistics.Interp(ind[0],userAttributeValues))
    mstats = None
    if (len(evalFunc)>=2):
        statsFitness1 = tools.Statistics(key=lambda ind: ind.fitness.values[0])
        statsFitness2 = tools.Statistics(key=lambda ind: ind.fitness.values[1])
        mstats = tools.MultiStatistics(fitnessObj1=statsFitness1, fitnessObj2=statsFitness2,Conf=statsConf,Accs=statsAccs,RoleCnt=statsRoleCnt,URCnt=statsURCnt,RPCnt=statsRPCnt,Interp=statsInterp)
    if (len(evalFunc)==3):
        statsFitness3 = tools.Statistics(key=lambda ind: ind.fitness.values[2])
        mstats = tools.MultiStatistics(fitnessObj1=statsFitness1, fitnessObj2=statsFitness2, fitnessObj3=statsFitness3,Conf=statsConf,Accs=statsAccs,RoleCnt=statsRoleCnt,URCnt=statsURCnt,RPCnt=statsRPCnt,Interp=statsInterp)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)
    logbook.header = "gen", "evals"
    for o in range(1, len(evalFunc)+1):
        logbook.chapters["fitnessObj"+str(o)].header = "min", "avg", "max", "std"
    logbook.chapters["Conf"].header = "min", "avg", "max", "std"
    logbook.chapters["Accs"].header = "min", "avg", "max", "std"
    logbook.chapters["RoleCnt"].header = "min", "avg", "max", "std"
    logbook.chapters["URCnt"].header = "min", "avg", "max", "std"
    logbook.chapters["RPCnt"].header = "min", "avg", "max", "std"
    logbook.chapters["Interp"].header = "min", "avg", "max", "std"

    # Creating the population
    if (not population):
        logger.info("Generate new population of "+str(populationSize)+" individuals")
        population = toolbox.population(n=populationSize)

    solutionFound = None

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
        if (max(fit)==0):
                solutionFound = 0

    # Save population in JSON file
    if (printPopulations):
        pop_subdirectory = pop_directory+"\\Generation_"+str(genStart)
        #if not os.path.exists(pop_subdirectory):
        #    os.makedirs(pop_subdirectory)
        utils.saveDiversity(genStart,population,pop_subdirectory+"_diversity.json")
        utils.savePopulation(genStart,population,pop_subdirectory+"_population.pkl")
        #visual.showBestResult(population, genStart, Original, pop_subdirectory+"\\Individual", "Individual", "Individual from Generation "+str(genStart), False, False, True, False)

    # Log statistics for first generation
    if ((len(logbook)==0) or (logbook.pop(len(logbook)-1)["gen"] != genStart)):
        record = mstats.compile(population)
        logbook.record(gen=genStart, evals=len(invalid_ind), **record)
        printText = "Generation "+str(genStart)+":\t"+str(logbook.stream)+"\n"
        for o in range(1, len(evalFunc)+1):
            printText += "\n"+str(logbook.chapters["fitnessObj"+str(o)].stream)
        printText += str(logbook.chapters["Conf"].stream)+"\n"\
                     +str(logbook.chapters["Accs"].stream)+"\n"+\
                     str(logbook.chapters["RoleCnt"].stream)+"\n"\
                     +str(logbook.chapters["URCnt"].stream)+"\n"\
                     +str(logbook.chapters["RPCnt"].stream)+"\n"\
                     +str(logbook.chapters["Interp"].stream)
        logger.info(printText)

    # Begin the evolution
    logger.info("Start evolution...")
    start = datetime.datetime.now()
    logger.info("Start time: "+str(start))
    #hof = tools.HallOfFame(maxsize=1)

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    population = toolbox.select(population, len(population))

    stop = False
    generation = genStart+1
    logger.info("Start evolution with Generation "+str(genStart))
    while ((not stop) and (generation <= genStart+NGEN)):

        # Vary the population
        offspring = toolbox.preselect(population, len(population))
        offspring = [toolbox.clone(ind) for ind in offspring]
        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)
            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values
        #offspring = algorithms.varOr(population, toolbox, 100, cxpb=CXPB, mutpb=MUTPB)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            if (not solutionFound and max(fit)==0):
                solutionFound = generation
            #if (fit[0] == 0):
            #    stop = True

        # Select the next generation population
        population = toolbox.select(population + offspring, len(population))

        # Add Fitness values to results
        if generation % freq == 0:
            for ind in population:
                results[generation].append(ind.fitness.values)
            # Log statistics for generation
            record = mstats.compile(population)
            logbook.record(gen=generation, evals=len(invalid_ind), **record)
            printText = "Generation "+str(generation)+":\t"+str(logbook.stream)+"\t"
            for o in range(1, len(evalFunc)+1):
                printText += str(logbook.chapters["fitnessObj"+str(o)].stream)+"\t"
            printText += str(logbook.chapters["Conf"].stream)+"\t"\
                         +str(logbook.chapters["Accs"].stream)+"\t"\
                         +str(logbook.chapters["RoleCnt"].stream)+"\t"\
                         +str(logbook.chapters["URCnt"].stream)+"\t"\
                         +str(logbook.chapters["RPCnt"].stream)+"\t"\
                         +str(logbook.chapters["Interp"].stream)
            logger.info(printText)

        if generation % int((genStart+NGEN)/10) == 0:
            if (printPopulations):
                pop_subdirectory = pop_directory+"\\Generation_"+str(generation)
                #if not os.path.exists(pop_subdirectory):
                #    os.makedirs(pop_subdirectory)
                utils.saveDiversity(generation,population,pop_subdirectory+"_diversity.json")
                utils.savePopulation(generation,population,pop_subdirectory+"_population.pkl")
                #visual.showBestResult(offspring, genStart, Original, pop_subdirectory+"\\Individual", "Individual", "Individual from Generation "+str(generation), False, False, True, False)

        generation += 1

    utils.printDiversity(pop_directory, int((genStart+NGEN)/10))
    utils.savePopulation(generation,population,pop_subdirectory+"_population.pkl")

    end = datetime.datetime.now()
    timediff = end-start
    time.append(timediff.total_seconds())
    generation -= 1
    # Print final population
    #visual.printpopulation(population)
    logger.info("==> Generation "+str(generation))
    logger.info("DONE.\n")

    # Set Checkpoint
    fileExt = "_M"
    for obj in evalFunc:
        fileExt+= "_" +obj[:5]
    fileExt+= "_"+str(len(population)) + "_" + str(generation)
    '''if (checkpoint):
        fileExt = "_cont_" + str(len(population)) + "_" + str(generation) + "_" + str(CXPB) + "_" + str(MUTPB_All)
        pickleFile = "Checkpoint"+fileExt+".pkl"
    print("Save checkpoint into "+str(pickleFile))
    cp = dict(population=population,
              generation=generation,
              rndstate=random.getstate(),
              Original=Original,
              results=results,
              time=time,
              populationSize=populationSize,
              obj_weights=obj_weights,
              CXPB=CXPB,
              prevFiles=prevFiles,
              MUTPB_All=MUTPB_All,
              addRolePB=addRolePB,
              removeRolePB=removeRolePB,
              removeUserPB=removeUserPB,
              removePermissionPB=removePermissionPB,
              addUserPB=addUserPB,
              addPermissionPB=addPermissionPB,
              logbook=logbook)
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("DONE.\n")'''

    top = toolbox.select(population, k=numberTopRoleModels)

    return population, results, generation, time, prevFiles, top, logbook, fileExt, solutionFound
