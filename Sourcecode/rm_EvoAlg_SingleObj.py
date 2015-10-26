__author__ = 'Theresa'

import random
import numpy
from deap import creator, base, tools, algorithms
import pickle
import os.path
import datetime
import rm_EAOperators as operators
import rm_EAInitialization as init
import rm_EAEvaluations as evals
import rm_Visualization as visual
from collections import defaultdict

# -----------------------------------------------------------------------------------
# Evolutionary algorithm - One objective
# -----------------------------------------------------------------------------------
def evolution(Original, evalFunc, populationSize, CXPB, MUTPB_All, addRolePB, removeRolePB, removeUserPB,
              removePermissionPB, addUserPB, addPermissionPB, NGEN, freq, numberTopRoleModels,
              untilSolutionFound=False, eval_weights=[], pickleFile="", checkpoint=False, prevFiles="",
              userAttributeValues=[],userAttributes=[], printPopulations=False, pop_directory=""):

    print("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    population = []

    # Create Logbook
    logbook = tools.Logbook()

    # Register Optimization
    weights = None
    if (evalFunc=="Confidentiality"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="Availability"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="RoleCnt"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="Violations"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="Interpretability"):
        weights=(1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="Saenko"):
        weights=(1.0,1.0,1.0,1.0)
    elif (evalFunc=="Saenko_Euclidean"):
        weights=(1.0,1.0,1.0,1.0)
    elif (evalFunc=="WSC"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="WSC_Star"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="AvgRoleConf"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="AvgRoleConf_A"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="WSC_INT"):
         weights=(-1.0,-1.0,-1.0,-1.0)
    elif (evalFunc=="WSC_Star_RoleDis"):
        weights=(-1.0,-1.0,-1.0,-1.0)
    else:
        raise ValueError("Evaluation function '"+str(evalFunc)+"' not known")
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
            raise ValueError("Checkpoint file does not exit")
    else:
        print("Use checkpoint: False")
        checkpoint = False'''

    userSize = int(Original.shape[0])
    permissionSize = int(Original.shape[1])

    # Toolbox
    toolbox = base.Toolbox()
    # Register Chromosome Generator
    toolbox.register("chromosome", init.generateChromosome, maxRoles=userSize, userSize=userSize, permissionSize=permissionSize)
    # Register Individual and Population Initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Register Evaluation Function
    if (evalFunc=="Confidentiality"):
        toolbox.register("evaluate", evals.evalFunc_Confidentiality, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Availability"):
        toolbox.register("evaluate", evals.evalFunc_Availability, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="RoleCnt"):
        toolbox.register("evaluate", evals.evalFunc_RoleCnt, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Violations"):
        toolbox.register("evaluate", evals.evalFunc_Violations, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Interpretability"):
       toolbox.register("evaluate", evals.evalFunc_Interpretability, userSize=userSize, permissionSize=permissionSize, orig=Original, userAttributeValues=userAttributeValues)
    elif (evalFunc=="Saenko"):
        toolbox.register("evaluate", evals.evalFunc_Saenko, userSize=userSize, permissionSize=permissionSize, orig=Original, weights=eval_weights)
    elif (evalFunc=="Saenko_Euclidean"):
        toolbox.register("evaluate", evals.evalFunc_Saenko_Euclidean, userSize=userSize, permissionSize=permissionSize, orig=Original, weights=eval_weights)
    elif (evalFunc=="WSC"):
        toolbox.register("evaluate", evals.evalFunc_WSC, userSize=userSize, permissionSize=permissionSize, orig=Original, weights=eval_weights)
    elif (evalFunc=="WSC_Star"):
        toolbox.register("evaluate", evals.evalFunc_WSC_Star, userSize=userSize, permissionSize=permissionSize, orig=Original, weights=eval_weights)
    elif (evalFunc=="AvgRoleConf"):
        toolbox.register("evaluate", evals.evalFunc_AvgRoleConfViolations, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="AvgRoleConf_A"):
        toolbox.register("evaluate", evals.evalFunc_AvgRoleConfViolations_Availability, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="WSC_INT"):
        toolbox.register("evaluate", evals.evalFunc_WSC_INT, userSize=userSize, permissionSize=permissionSize, orig=Original, weights=eval_weights, userAttributeValues=userAttributeValues)
    elif (evalFunc=="WSC_Star_RoleDis"):
        toolbox.register("evaluate", evals.evalFunc_WSC_Star_RoleDis, userSize=userSize, permissionSize=permissionSize, orig=Original, weights=eval_weights)
    else:
        raise ValueError('Evaluation function not known')

    # Register Variation Operators
    toolbox.register("mate", operators.mateFunc)
    toolbox.register("mutate", operators.mutFunc, addRolePB=addRolePB, removeRolePB=removeRolePB, removeUserPB=removeUserPB,
                     removePermissionPB=removePermissionPB, addUserPB=addUserPB, addPermissionPB=addPermissionPB,
                     userSize=userSize, permissionSize=permissionSize)
    toolbox.register("select", tools.selTournament, tournsize=5)

    # Register Statistics
    '''
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)'''
    statsFitness = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    statsConf = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    statsAccs = tools.Statistics(key=lambda ind: ind.fitness.values[2])
    statsRoleCnt = tools.Statistics(key=lambda ind: ind.fitness.values[3])
    mstats = tools.MultiStatistics(Fitness=statsFitness,Conf=statsConf,Accs=statsAccs,RoleCnt=statsRoleCnt)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)
    logbook.header = "gen", "evals"
    logbook.chapters["Fitness"].header = "min", "avg", "max", "std"
    logbook.chapters["Conf"].header = "min", "avg", "max", "std"
    logbook.chapters["Accs"].header = "min", "avg", "max", "std"
    logbook.chapters["RoleCnt"].header = "min", "avg", "max", "std"

    # Creating the population
    if (not population):
        print("Generate new population of "+str(populationSize)+" individuals")
        population = toolbox.population(n=populationSize)
        if (printPopulations):
            pop_subdirectory = pop_directory+"\\Generation_"+str(genStart)
            if not os.path.exists(pop_subdirectory):
                os.makedirs(pop_subdirectory)
            visual.showBestResult(population, genStart, Original, pop_subdirectory+"\\Individual", "Individual", "Individual from Generation "+str(genStart), False, False, True, False)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    if (evalFunc=="WSC_Star_RoleDis"):
        fitnesses = [toolbox.evaluate(population=population, individual=ind) for ind in invalid_ind]
    else:
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # Log statistics for first generation
    if ((len(logbook)==0) or (logbook.pop(len(logbook)-1)["gen"] != genStart)):
        '''record = stats.compile(population)
        logbook.record(gen=genStart, evals=len(invalid_ind), **record)
        print("Generation "+str(genStart)+":\t"+str(logbook.stream))'''
        record = mstats.compile(population)
        logbook.record(gen=genStart, evals=len(invalid_ind), **record)
        print("Generation "+str(genStart)+":\t"
              +str(logbook.stream)+"\n"
              +str(logbook.chapters["Fitness"].stream)+"\n"
              +str(logbook.chapters["Conf"].stream)+"\n"
              +str(logbook.chapters["Accs"].stream)+"\n"
              +str(logbook.chapters["RoleCnt"].stream)
              )

    # Begin the evolution
    print("Start evolution...")
    start = datetime.datetime.now()
    print("Start time: "+str(start))
    #hof = tools.HallOfFame(maxsize=1)

    generation = genStart+1
    stop = False
    print("Start evolution with Generation "+str(genStart))
    while ((not stop) and (generation <= genStart+NGEN)):
        population = toolbox.select(population, k=len(population))
        population = algorithms.varAnd(population, toolbox, cxpb=CXPB, mutpb=MUTPB_All)

        # Evaluate individuals, which need a evaluation
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        if (evalFunc=="WSC_Star_RoleDis"):
            fitnesses = [toolbox.evaluate(population=population, individual=ind) for ind in invalid_ind]
        else:
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            # Stop condition
            if (untilSolutionFound and fit[0] == 0):
                stop = True

        # Add Fitness values to results
        if generation % freq == 0:
            for ind in population:
                results[generation].append(ind.fitness.values)
            # Log statistics for generation
            '''record = stats.compile(population)
            logbook.record(gen=generation, evals=len(invalids), **record)
            print("Generation "+str(generation)+":\t"+str(logbook.stream))'''
            record = mstats.compile(population)
            logbook.record(gen=generation, evals=len(invalid_ind), **record)
            print("Generation "+str(generation)+":\t"
                  +str(logbook.stream)+"\t"
                  +str(logbook.chapters["Fitness"].stream)+"\t\t"
                  +str(logbook.chapters["Conf"].stream)+"\t\t"
                  +str(logbook.chapters["Accs"].stream)+"\t\t"
                  +str(logbook.chapters["RoleCnt"].stream)
                  )

        if (printPopulations):
            pop_subdirectory = pop_directory+"\\Generation_"+str(generation)
            if not os.path.exists(pop_subdirectory):
                os.makedirs(pop_subdirectory)
            visual.showBestResult(population, genStart, Original, pop_subdirectory+"\\Individual", "Individual", "Individual from Generation "+str(generation), False, False, True, False)

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
    fileExt = "_Single_" + evalFunc + "_" + str(len(population)) + "_" + str(generation) + "_" + str(CXPB) + "_" + str(MUTPB_All)
    '''
    if (checkpoint):
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
    print("DONE.\n")
    '''

    return population, results, generation, time, prevFiles, tools.selBest(population, k=numberTopRoleModels), logbook, fileExt
