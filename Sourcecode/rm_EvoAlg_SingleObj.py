import random
import numpy
from deap import creator, base, tools, algorithms
import pickle
import os.path
import datetime
import rm_EAOperators as ops
import rm_EAEvaluations as evals
from collections import defaultdict


# -----------------------------------------------------------------------------------
# Evolutionary algorithm - One objective
# -----------------------------------------------------------------------------------
def evolution(Original, evalFunc, populationSize, CXPB, MUTPB_All, addRolePB, removeRolePB, removeUserPB,
              removePermissionPB, addUserPB, addPermissionPB, NGEN, freq, numberTopRoleModels, checkpoint, prevFiles, directory, pickleFile):
    print("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    population = []

    # Create Logbook
    logbook = tools.Logbook()

    # Creator
    if (evalFunc=="Obj1"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) #Minimization
    elif (evalFunc=="Obj1"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) #Minimization
    elif (evalFunc=="Saenko"):
        creator.create("FitnessMin", base.Fitness, weights=(1.0,)) #Maximization
    elif (evalFunc=="Saenko_Euclidean"):
        creator.create("FitnessMin", base.Fitness, weights=(1.0,)) #Maximization
    elif (evalFunc=="WSC"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) #Minimization
    else:
        raise ValueError('Evaluation function not known')
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # Get Checkpoint
    if (checkpoint and len(prevFiles)!=0):
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
        checkpoint = False

    userSize = int(Original.shape[0])
    permissionSize = int(Original.shape[1])

    # Toolbox
    toolbox = base.Toolbox()
    # Chromosome generator
    toolbox.register("chromosome", ops.generateChromosome, maxRoles=userSize, userSize=userSize, permissionSize=permissionSize)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    if (evalFunc=="Obj1"):
        toolbox.register("evaluate", evals.evalFunc_Obj1, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Obj2"):
        toolbox.register("evaluate", evals.evalFunc_Obj2, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Saenko"):
        toolbox.register("evaluate", evals.evalFunc_Saenko, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Saenko_Euclidean"):
        toolbox.register("evaluate", evals.evalFunc_Saenko_Euclidean, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="WSC"):
        toolbox.register("evaluate", evals.evalFunc_WSC, userSize=userSize, permissionSize=permissionSize, orig=Original)
    else:
        raise ValueError('Evaluation function not known')
    toolbox.register("mate", ops.mateFunc)
    toolbox.register("mutate", ops.mutFunc, addRolePB=addRolePB, removeRolePB=removeRolePB, removeUserPB=removeUserPB,
                     removePermissionPB=removePermissionPB, addUserPB=addUserPB, addPermissionPB=addPermissionPB,
                     userSize=userSize, permissionSize=permissionSize)
    toolbox.register("select", tools.selTournament, tournsize=5)

    # Register statistics
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    # Creating the population
    if (not population):
        print("Generate new population of "+str(populationSize)+" individuals")
        population = toolbox.population(n=populationSize)
        #print(numpy.array(population))

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # Log statistics for first generation
    if ((len(logbook)==0) or (logbook.pop(len(logbook)-1)["gen"] != genStart)):
        record = stats.compile(population)
        logbook.record(gen=genStart, evals=len(invalid_ind), **record)
        print("Generation "+str(genStart)+":\t"+str(logbook.stream))

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
        invalids = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalids)
        for ind, fit in zip(invalids, fitnesses):
            ind.fitness.values = fit
            # Stop condition
            #if (fit[0] == 0):
            #    stop = True

        # Add Fitness values to results
        if generation % freq == 0:
            for ind in population:
                results[generation].append(ind.fitness.values)
            # Log statistics for generation
            record = stats.compile(population)
            logbook.record(gen=generation, evals=len(invalids), **record)
            print("Generation "+str(generation)+":\t"+str(logbook.stream))

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
    fileExt = "_" + str(len(population)) + "_" + str(generation) + "_" + str(CXPB) + "_" + str(MUTPB_All)
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

    return population, results, generation, time, prevFiles, tools.selBest(population, k=numberTopRoleModels), logbook, fileExt
