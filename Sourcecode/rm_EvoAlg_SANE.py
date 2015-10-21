import random
import numpy
from deap import creator, base, tools
import MatrixOperators as matrixOps
import os.path
import datetime
from collections import defaultdict
import rm_FileParser as parser
import rm_CoEvo_Visualization as visual
import rm_CoEvo_EAInitialization as init
import rm_CoEvo_EAEvaluations as eval
import rm_CoEvo_EAOperators as operators
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
        Original = matrixOps.generateGoalMatrix(4, 10, 10)
    elif (DATA=="GeneratedData"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151004-191825\\testdata.rbac"))
    elif (DATA=="GeneratedData_small"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151005-194203\\testdata.rbac"))
    return Original

# -----------------------------------------------------------------------------------
# Evolutionary algorithm - One objective
# -----------------------------------------------------------------------------------
def evolution(Original, populationSize, NGEN, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, numberOfTrialItems, freq, numberTopRoleModels):
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
    toolbox.register("chromosome", init.generateChromosome, userSize=userSize, permissionSize=permissionSize)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    #toolbox.register("evaluate", evalFunc, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", operators.mateFunc, r=0.5)
    toolbox.register("mutate", operators.mutFunc, removeUserPB=removeUserPB, removePermissionPB=removePermissionPB, addUserPB=addUserPB,
                     addPermissionPB=addPermissionPB, userSize=userSize, permissionSize=permissionSize)
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
    trials = eval.evaluation(population, numberOfTrialItems, Original)

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
        trials = eval.evaluation(population, numberOfTrialItems, Original)

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

    fileExt = "_SANE_"+str(len(population)) + "_" + str(generation) + "_" + str(numberOfTrialItems)

    return population, results, generation, time, tools.selBest(population, k=numberTopRoleModels), logbook, fileExt

def execute(Original, POP_SIZE, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, NGEN, numberOfTrialItems, freq, numberTopRoleModels = 5):

    population, results, generation, time, top, logbook, fileExt = evolution(Original, POP_SIZE, NGEN, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, numberOfTrialItems, freq, numberTopRoleModels)

    info = "Hallo"
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    directory = "..\\Output\\"+timestamp+"_SANE"
    if not os.path.exists(directory):
        os.makedirs(directory)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    visual.showFitnessInPlot(results, generation, freq, directory+"\\fitness", fileExt[1:], info, "Violations", False, False, True, False)
    visual.showAllRoles(top,generation,Original, directory+"\\mytest_best", False, False, True, True)

'''
DATA = "GeneratedData_small"
Original = getDataSet(DATA)
POP_SIZE = 100
CXPB = 0.25
MUTPB_All = 0.25
removeUserPB = 0.25
removePermissionPB = 0.25
addUserPB = 0.25
addPermissionPB = 0.25
NGEN = 100
freq = 1
numberOfTrialItems = 3
numberTopRoleModels = 3

execute(Original, POP_SIZE, CXPB, MUTPB_All, removePermissionPB, removePermissionPB, addUserPB, addPermissionPB, NGEN, numberOfTrialItems, freq, 3)
'''