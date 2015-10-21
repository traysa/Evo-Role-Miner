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
import rm_FileParser as parser
import rm_Visualization as visual
import itertools

# ----------------------------------------------------------------------------------------------------------------------
# DATA SETS
# ----------------------------------------------------------------------------------------------------------------------
def getDataSet(DATA):
    Original = []
    if (DATA=="healthcare"):
        Original = numpy.matrix(parser.read("..\\TestData\\healthcare.rbac"))
    elif (DATA=="testdata"):
        testdata = [[1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 1, 1], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 1, 1], [1, 0, 0, 1, 1]]
        testdata2 = [[3, 3, 0, 0, 0], [2, 0, 0, 2, 2], [1, 0, 1, 1, 1], [2, 0, 0, 2, 2], [2, 0, 0, 2, 2], [4, 3, 0, 2, 2], [2, 0, 0, 2, 2]]
        Original = numpy.matrix(testdata2)
    elif (DATA=="random"):
        Original = utils.generateGoalMatrix(4, 10, 10)
    return Original

# -----------------------------------------------------------------------------------
# Evolutionary algorithm functions
# -----------------------------------------------------------------------------------
# Initialization
def generateChromosome(userSize, permissionSize):
    chromosome = []
    # Create a role as chromosome
    chromosome = utils.generateGene(userSize, permissionSize)
    return chromosome

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
def evaluation(population, u, Original):
    for ind in population:
        ind.fitness.values = (0,)

    trialReport = [0 for i in population]
    #print(trialReport)
    stop = False
    trialnumber = 0

    while not stop:
        trialnumber += 1
        #print("Trial: "+str(trialnumber))
        pick = random.sample(range(0,len(population)),u)
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
    violations = evalFunc_Obj1(individuals, Original)
    for ind in individuals:
        ind.fitness.values = (list(ind.fitness.values)[0] + violations),
        temp = 0
    return individuals

# -----------------------------------------------------------------------------------
# Single Objective Evaluation Functions
# -----------------------------------------------------------------------------------
# Violations
def evalFunc_Obj1(individuals, orig):
    array = utils.resolveIndividualsIntoArray(individuals,int(orig.shape[0]), int(orig.shape[1]))
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    #numberOfRoles = len(individual[0])
    #return conf, accs, numberOfRoles
    violations = (conf+accs)
    return violations

# Mutation Function
def mutFunc(individual, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, userSize, permissionSize):
    #print("Mutation")
    #print("BEFORE: "+str(individual))
    role = individual[0]
    if random.random() < removeUserPB:
        if (len(role[0]) > 1):
            del role[0][random.randint(0, len(role[0]) - 1)]
    if random.random() < removePermissionPB:
        if (len(role[1]) > 1):
            del role[1][random.randint(0, len(role[1]) - 1)]
    if random.random() < addUserPB:
        # Pick random gene (role)
        length = len(role[0])
        #userSet = {x for x in range(1, userSize + 1)}
        # Add exactly 1 user, if the role does not already contain all users
        while ((length < userSize) and (len(role[0]) == length)):            #
            role[0] = list(set(role[0]) | {random.randint(1, userSize)})
    if random.random() < addPermissionPB:
        length = len(role[1])
        while ((length < permissionSize) and (len(role[1]) == length)):
            role[1] = list(set(role[1]) | {random.randint(1, permissionSize)})
    #print("AFTER: "+str(individual))
    return individual,

# Crossover Function
def mateFunc(ind1, ind2, r):
    #print("User-Crossover")
    #print("BEFORE: "+str(ind1)+" -- "+str(ind2))
    if random.random() < r:
        temp1 = ind1[0][0]
        temp2 = ind2[0][0]
        size = min(len(temp1), len(temp2))
        if size > 1:
            cxpoint = random.randint(1, size - 1)
            temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
    else:
        temp1 = ind1[0][1]
        temp2 = ind2[0][1]
        size = min(len(temp1), len(temp2))
        if size > 1:
            cxpoint = random.randint(1, size - 1)
            temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
    #print("AFTER: "+str(ind1)+" -- "+str(ind2))
    return ind1, ind2


# -----------------------------------------------------------------------------------
# Evolutionary algorithm - One objective
# -----------------------------------------------------------------------------------
def evolution(Original, populationSize, NGEN, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6, u, freq):
    print("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    population = []

    # Create Logbook
    logbook = tools.Logbook()

    # Creator
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) #Minimization
    creator.create("Individual", list, fitness=creator.FitnessMin)

    userSize = int(Original.shape[0])
    permissionSize = int(Original.shape[1])

    # Toolbox
    toolbox = base.Toolbox()
    # Chromosome generator
    toolbox.register("chromosome", generateChromosome, userSize=userSize, permissionSize=permissionSize)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    #toolbox.register("evaluate", evalFunc, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", mateFunc, r=0.5)
    toolbox.register("mutate", mutFunc, removeUserPB=MUTPB_3, removePermissionPB=MUTPB_4, addUserPB=MUTPB_5,
                     addPermissionPB=MUTPB_6, userSize=userSize, permissionSize=permissionSize)
    toolbox.register("select", tools.selTournament, tournsize=5)
    #toolbox.register("select", tools.selBest, k=10)

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
        print(population)

    # Evaluate the individuals with an invalid fitness
    #invalid_ind = [ind for ind in population if not ind.fitness.valid]

    # EVALUATION
    #fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    trials = evaluation(population, u, Original)

    #for ind, fit in zip(invalid_ind, fitnesses):
    #    ind.fitness.values = fit

    # Log statistics for first generation
    if ((len(logbook)==0) or (logbook.pop(len(logbook)-1)["gen"] != genStart)):
        record = stats.compile(population)
        logbook.record(gen=genStart, evals=trials, **record)
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
        #--------------------------------------------------------------------------------------------------------
        # Neurons are then ranked by average fitness. Each neuron in the top quartile is recombined with a
        # higher-ranking neuron using 1-point crossover and mutation at low levels to create the offspring to
        # replace the lowest-ranking half of the population.
        #--------------------------------------------------------------------------------------------------------

        half = int(len(population)/2)
        quartile = int(len(population)/4)

        top_half_offspring = tools.selBest(population, half)
        # Clone the selected individuals
        top_half_offspring = [toolbox.clone(ind) for ind in top_half_offspring]
        top_quartile_offspring = tools.selBest(top_half_offspring, quartile)
        # Apply crossover on the offspring
        for child1, child2 in zip(top_quartile_offspring[::2], top_quartile_offspring[1::2]):
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

        low_half_offspring = tools.selWorst(population, half)
        # Clone the selected individuals
        low_half_offspring = [toolbox.clone(ind) for ind in low_half_offspring]
        # Apply mutation on the offspring
        for mutant in low_half_offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        # Select the next generation population
        population = list(itertools.chain(list(top_half_offspring),list(low_half_offspring)))

        # Evaluate the individuals with an invalid fitness
        #invalid_ind = [ind for ind in population if not ind.fitness.valid]
        trials = evaluation(population, u, Original)

        # Add Fitness values to results
        if generation % freq == 0:
            for ind in population:
                results[generation].append(ind.fitness.values)
            # Log statistics for generation
            record = stats.compile(population)
            logbook.record(gen=generation, evals=trials, **record)
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

    return population, results, generation, time, tools.selBest(population, k=5), logbook


DATA="testdata"
Original = getDataSet(DATA)
POP_SIZE = 7 # Should be bigger than u (trialsize)
CXPB = 0.25
MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6 = 0.25,0.25,0.25,0.25,0.25,0.25,0.25
NGEN = 50
u = 3
freq = 1

population, results, generation, time, top, logbook = evolution(Original, POP_SIZE, NGEN, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6, u, freq)

timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
directory = "..\\Output\\"+timestamp+"_SANE"
if not os.path.exists(directory):
    os.makedirs(directory)
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
visual.showFitnessInPlot(results, generation, freq, directory+"\\mytest", "", False, False, True, True)
visual.showAllRoles(population,generation,Original, directory+"\\mytest_best", False, False, True, True)