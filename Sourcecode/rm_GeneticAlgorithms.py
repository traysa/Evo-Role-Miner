import random
import numpy
from deap import creator, base, tools, algorithms
import pickle
import rm_MatrixOperators as matrixOps
import rm_Utils as utils
import os.path
import datetime
import fortin2013
from collections import defaultdict

# -----------------------------------------------------------------------------------
# Evolutionary algorithm functions
# -----------------------------------------------------------------------------------
# Initialization
def generateChromosome(maxRoles, userSize, permissionSize):
    chromosome = []
    # Create random number of genes (roles) for one chromosome
    for i in range(0, random.randint(1, maxRoles)):
        gene = utils.generateGene(userSize, permissionSize)
        # Add gene to chromosome
        chromosome.append(gene)
    chromosome = utils.localOptimization(chromosome)
    return chromosome

# -----------------------------------------------------------------------------------
# Single Objective Evaluation Functions
# -----------------------------------------------------------------------------------
# Violataions
def evalFunc_Obj1(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    #numberOfRoles = len(individual[0])
    #return conf, accs, numberOfRoles
    temp = (conf+accs)
    return temp,
# Number of Roles
def evalFunc_Obj2(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    return numberOfRoles,
# Number of Roles + Violations (from paper)
def evalFunc_Saenko(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    numberOfRoles = len(individual[0])
    #return conf, accs, numberOfRoles
    w1 = 0.00001
    w2 = 1
    w3 = 1
    temp = (w1 * numberOfRoles + w2 * conf + w3 * accs)**(-1)
    return temp,

# -----------------------------------------------------------------------------------
# Multi Objective Evaluation Functions
# -----------------------------------------------------------------------------------
def evalFunc_Multi(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    numberOfRoles = len(individual[0])
    temp = (conf+accs)
    return temp,numberOfRoles

# Mutation Function
def mutFunc(individual, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, userSize, permissionSize):
    #print("Mutation")
    if random.random() < addRolePB:
        gene = utils.generateGene(userSize, permissionSize)
        individual[0].append(gene)
        individual[0] = utils.localOptimization(individual[0])
    if ((len(individual[0]) > 1) and (random.random() < removeRolePB)):
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        del role
    if random.random() < removeUserPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        if (len(role[0]) > 1):
            del role[0][random.randint(0, len(role[0]) - 1)]
            individual[0] = utils.localOptimization(individual[0])
    if random.random() < removePermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        if (len(role[1]) > 1):
            del role[1][random.randint(0, len(role[1]) - 1)]
            individual[0] = utils.localOptimization(individual[0])
    if random.random() < addUserPB:
        # Pick random gene (role)
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        length = len(role[0])
        #userSet = {x for x in range(1, userSize + 1)}
        # Add exactly 1 user, if the role does not already contain all users
        while ((length < userSize) and (len(role[0]) == length)):            #
            role[0] = list(set(role[0]) | {random.randint(1, userSize)})
        individual[0] = utils.localOptimization(individual[0])
    if random.random() < addPermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        length = len(role[1])
        while ((length < permissionSize) and (len(role[1]) == length)):
            role[1] = list(set(role[1]) | {random.randint(1, permissionSize)})
        individual[0] = utils.localOptimization(individual[0])
    return individual,

# Crossover Function
def mateFunc(ind1, ind2):
    #print("Crossover")
    temp1 = ind1[0]
    temp2 = ind2[0]
    size = min(len(temp1), len(temp2))
    if size > 1:
        cxpoint = random.randint(1, size - 1)
        temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
        temp1 = utils.localOptimization(temp1)
        temp2 = utils.localOptimization(temp2)
    return ind1, ind2


# -----------------------------------------------------------------------------------
# Evolutionary algorithm - One objective
# -----------------------------------------------------------------------------------
def evolution(Original, evalFunc, populationSize, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6, NGEN, freq, checkpoint, prevFiles, directory, pickleFile):
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
    toolbox.register("chromosome", generateChromosome, userSize, userSize, permissionSize)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    if (evalFunc=="Obj1"):
        toolbox.register("evaluate", evalFunc_Obj1, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Obj2"):
        toolbox.register("evaluate", evalFunc_Obj2, userSize=userSize, permissionSize=permissionSize, orig=Original)
    elif (evalFunc=="Saenko"):
        toolbox.register("evaluate", evalFunc_Saenko, userSize=userSize, permissionSize=permissionSize, orig=Original)
    else:
        raise ValueError('Evaluation function not known')
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=MUTPB_1, removeRolePB=MUTPB_2, removeUserPB=MUTPB_3,
                     removePermissionPB=MUTPB_4, addUserPB=MUTPB_5, addPermissionPB=MUTPB_6,
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
              MUTPB_1=MUTPB_1,
              MUTPB_2=MUTPB_2,
              MUTPB_3=MUTPB_3,
              MUTPB_4=MUTPB_4,
              MUTPB_5=MUTPB_5,
              MUTPB_6=MUTPB_6,
              logbook=logbook)
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("DONE.\n")

    return population, results, generation, time, prevFiles, tools.selBest(population, k=5), logbook, fileExt

# -----------------------------------------------------------------------------------
# Evolutionary algorithm - Multi objective
# -----------------------------------------------------------------------------------
def evolution_multi(Original, populationSize, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6, NGEN, freq, checkpoint, prevFiles, directory, pickleFile):
    print("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    population = []

    # Create Logbook
    logbook = tools.Logbook()

    # Creator
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))
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
            print("Checkpoint file does not exit")
    else:
        print("Use checkpoint: False")
        checkpoint = False

    userSize = int(Original.shape[0])
    permissionSize = int(Original.shape[1])

    # Toolbox
    toolbox = base.Toolbox()
    # Chromosome generator
    toolbox.register("chromosome", generateChromosome, userSize, userSize, permissionSize)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    toolbox.register("evaluate", evalFunc_Multi, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=MUTPB_1, removeRolePB=MUTPB_2, removeUserPB=MUTPB_3, removePermissionPB=MUTPB_4,
                     addUserPB=MUTPB_5, addPermissionPB=MUTPB_6, userSize=userSize, permissionSize=permissionSize)
    toolbox.register("select", tools.selNSGA2)

    # Register statistics
    statsObj1 = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    statsObj2 = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    mstats = tools.MultiStatistics(fitnessObj1=statsObj1, fitnessObj2=statsObj2)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)
    logbook.header = "gen", "evals"
    logbook.chapters["fitnessObj1"].header = "min", "avg", "max", "std"
    logbook.chapters["fitnessObj2"].header = "min", "avg", "max", "std"

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
        print("Generation "+str(genStart)+":\t"
              +str(logbook.stream)+"\n"
              +str(logbook.chapters["fitnessObj1"].stream)+"\n"
              +str(logbook.chapters["fitnessObj2"].stream)
              )

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
        offspring = tools.selTournamentDCD(population, len(population))
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
            print("Generation "+str(generation)+":\t"
                  +str(logbook.stream)+"\t"
                  +str(logbook.chapters["fitnessObj1"].stream)+"\t\t"
                  +str(logbook.chapters["fitnessObj2"].stream)
                  )

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
              MUTPB_1=MUTPB_1,
              MUTPB_2=MUTPB_2,
              MUTPB_3=MUTPB_3,
              MUTPB_4=MUTPB_4,
              MUTPB_5=MUTPB_5,
              MUTPB_6=MUTPB_6,
              logbook=logbook)
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("DONE.\n")

    return population, results, generation, time, prevFiles, tools.selBest(population, k=5), logbook, fileExt

# -----------------------------------------------------------------------------------
# Evolutionary algorithm - Multi objective with Fortin2013
# -----------------------------------------------------------------------------------
def evolution_multi_fortin2013(Original, populationSize, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6, NGEN, freq, checkpoint, prevFiles, directory, pickleFile):
    print("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    population = []

    # Create Logbook
    logbook = tools.Logbook()

    # Creator
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))
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
            print("Checkpoint file does not exit")
    else:
        print("Use checkpoint: False")
        checkpoint = False

    userSize = int(Original.shape[0])
    permissionSize = int(Original.shape[1])

    # Toolbox
    toolbox = base.Toolbox()
    # Chromosome generator
    toolbox.register("chromosome", generateChromosome, userSize, userSize, permissionSize)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    toolbox.register("evaluate", evalFunc_Multi, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=MUTPB_1, removeRolePB=MUTPB_2, removeUserPB=MUTPB_3, removePermissionPB=MUTPB_4,
                     addUserPB=MUTPB_5, addPermissionPB=MUTPB_6, userSize=userSize, permissionSize=permissionSize)
    toolbox.register("preselect", fortin2013.selTournamentFitnessDCD)
    toolbox.register("select", fortin2013.selNSGA2)

    # Register statistics
    statsObj1 = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    statsObj2 = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    mstats = tools.MultiStatistics(fitnessObj1=statsObj1, fitnessObj2=statsObj2)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)
    logbook.header = "gen", "evals"
    logbook.chapters["fitnessObj1"].header = "min", "avg", "max", "std"
    logbook.chapters["fitnessObj2"].header = "min", "avg", "max", "std"

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
        print("Generation "+str(genStart)+":\t"
              +str(logbook.stream)+"\n"
              +str(logbook.chapters["fitnessObj1"].stream)+"\n"
              +str(logbook.chapters["fitnessObj2"].stream))

    # Begin the evolution
    print("Start evolution...")
    start = datetime.datetime.now()
    print("Start time: "+str(start))
    #hof = tools.HallOfFame(maxsize=1)

    # This is just to assign the crowding distance to the individuals
    #  no actual selection is done
    population = toolbox.select(population, len(population))

    stop = False
    generation = genStart+1
    print("Start evolution with Generation "+str(genStart))
    while ((not stop) and (generation <= genStart+NGEN)):

        # Vary the population
        #offspring = tools.selTournamentDCD(population, len(population))
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
            print("Generation "+str(genStart)+":\t"
              +str(logbook.stream)+"\n"
              +str(logbook.chapters["fitnessObj1"].stream)+"\n"
              +str(logbook.chapters["fitnessObj2"].stream))

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
              MUTPB_1=MUTPB_1,
              MUTPB_2=MUTPB_2,
              MUTPB_3=MUTPB_3,
              MUTPB_4=MUTPB_4,
              MUTPB_5=MUTPB_5,
              MUTPB_6=MUTPB_6,
              logbook=logbook)
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("DONE.\n")

    return population, results, generation, time, prevFiles, tools.selBest(population, k=5), logbook, fileExt

