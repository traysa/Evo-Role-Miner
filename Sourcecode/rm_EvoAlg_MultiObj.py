__author__ = 'Theresa'

import random
import numpy
from deap import creator, base, tools, algorithms
import pickle
import os.path
import datetime
import fortin2013
import nsga2_classic as nsga2
import rm_EAOperators as operators
import rm_EAInitialization as init
import rm_EAEvaluations as evals
from collections import defaultdict

# -----------------------------------------------------------------------------------
# Evolutionary algorithm - Multi objective
# -----------------------------------------------------------------------------------
def evolution_multi(Original, evalFunc, populationSize, CXPB, addRolePB, removeRolePB, removeUserPB,
                    removePermissionPB, addUserPB, addPermissionPB, NGEN, freq, numberTopRoleModels,
                    fortin=False, pickleFile="", checkpoint=False, prevFiles=""):
    # Validations
    if (len(evalFunc)<2):
        raise ValueError("Less than 2 objectives not possible")
    if (len(evalFunc)>3):
        raise ValueError("More than 3 objectives not supported")
    if (not(populationSize % 4 == 0)):
        raise ValueError("Population size has to be a multiple of 4")

    print("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    population = []

    # Create Logbook
    logbook = tools.Logbook()

    # Creator
    weights = ()
    for obj in evalFunc:
        if (obj=="Confidentiality"):
            weights+=(-1.0,)
        elif (obj=="Availability"):
            weights+=(-1.0,)
        elif (obj=="RoleCnt"):
            weights+=(-1.0,)
        elif (obj=="Violations"):
            weights+=(-1.0,)
        elif (obj=="Saenko"):
            weights+=(1.0,)
        elif (obj=="Saenko_Euclidean"):
            weights+=(1.0,)
        elif (obj=="WSC"):
            weights+=(-1.0,)
        elif (obj=="WSC_Star"):
            weights+=(-1.0,)
        else:
            raise ValueError("Evaluation function for '"+obj+"' not known")
    creator.create("FitnessMinMax", base.Fitness, weights=weights)
    creator.create("Individual", list, fitness=creator.FitnessMinMax)

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
    toolbox.register("chromosome", init.generateChromosome, userSize, userSize, permissionSize)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    toolbox.register("evaluate", evals.evalFunc_Multi, userSize=userSize, permissionSize=permissionSize, orig=Original, evalFunc=evalFunc)

    toolbox.register("mate", operators.mateFunc)
    toolbox.register("mutate", operators.mutFunc, addRolePB=addRolePB,
              removeRolePB=removeRolePB,
              removeUserPB=removeUserPB,
              removePermissionPB=removePermissionPB,
              addUserPB=addUserPB,
              addPermissionPB=addPermissionPB, userSize=userSize, permissionSize=permissionSize)
    if (fortin):
        toolbox.register("preselect", fortin2013.selTournamentFitnessDCD)
        toolbox.register("select", fortin2013.selNSGA2)
    else:
        toolbox.register("preselect", tools.selTournamentDCD)
        toolbox.register("select", tools.selNSGA2)

    # Register statistics
    mstats = None
    if (len(evalFunc)>=2):
        statsObj1 = tools.Statistics(key=lambda ind: ind.fitness.values[0])
        statsObj2 = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    if (len(evalFunc)==3):
        statsObj3 = tools.Statistics(key=lambda ind: ind.fitness.values[2])
        mstats = tools.MultiStatistics(fitnessObj1=statsObj1, fitnessObj2=statsObj2, fitnessObj3=statsObj3)
    else:
        mstats = tools.MultiStatistics(fitnessObj1=statsObj1, fitnessObj2=statsObj2)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)
    logbook.header = "gen", "evals"
    for o in range(1, len(evalFunc)+1):
        logbook.chapters["fitnessObj"+str(o)].header = "min", "avg", "max", "std"

    # Creating the population
    if (not population):
        print("Generate new population of "+str(populationSize)+" individuals")
        population = toolbox.population(n=populationSize)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # Log statistics for first generation
    if ((len(logbook)==0) or (logbook.pop(len(logbook)-1)["gen"] != genStart)):
        record = mstats.compile(population)
        logbook.record(gen=genStart, evals=len(invalid_ind), **record)
        printText = "Generation "+str(genStart)+":\t"+str(logbook.stream)
        for o in range(1, len(evalFunc)+1):
            printText += "\n"+str(logbook.chapters["fitnessObj"+str(o)].stream)
        print(printText)

    # Begin the evolution
    print("Start evolution...")
    start = datetime.datetime.now()
    print("Start time: "+str(start))
    #hof = tools.HallOfFame(maxsize=1)

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    population = toolbox.select(population, len(population))

    stop = False
    generation = genStart+1
    print("Start evolution with Generation "+str(genStart))
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
            printText = "Generation "+str(generation)+":\t"+str(logbook.stream)
            for o in range(1, len(evalFunc)+1):
                printText += "\t"+str(logbook.chapters["fitnessObj"+str(o)].stream)+"\t"
            print(printText)

        generation += 1

    end = datetime.datetime.now()
    timediff = end-start
    time.append(timediff.total_seconds())
    generation -= 1
    # Print final population
    #visual.printpopulation(population)
    print("==> Generation "+str(generation))
    print("DONE.\n")

    # Set Checkpoint
    fileExt = "_Multi"
    for obj in evalFunc:
        fileExt+= "_" +obj
    fileExt+= "_"+str(len(population)) + "_" + str(generation) + "_" + str(CXPB)
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

    return population, results, generation, time, prevFiles, tools.selBest(population, k=numberTopRoleModels), logbook, fileExt
