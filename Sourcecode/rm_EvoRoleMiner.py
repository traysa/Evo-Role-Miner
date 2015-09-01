import random
import numpy
from deap import creator, base, tools, algorithms
import pickle
import rm_MatrixOperators as matrixOps
import rm_Utils as utils
import rm_Visualization as visual
import rm_FileParser as parser
import time
import os.path
import datetime

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


# Evaluation Function
def evalFunc(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    #numberOfRoles = len(individual[0])
    #return conf, accs, numberOfRoles
    temp = (conf+accs)
    return temp,

# Evaluation Function
def evalFunc2(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    return numberOfRoles,

# Mutation Function
def mutFunc(individual, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, userSize, permissionSize):
    if random.random() < addRolePB:
        gene = utils.generateGene(userSize, permissionSize)
        individual[0].append(gene)
        individual[0] = utils.localOptimization(individual[0])
    if ((len(individual[0]) > 1) & (random.random() < removeRolePB)):
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
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        length = len(role[0])
        while ((length < userSize) & (len(role[0]) == length)):
            role[0] = list(set(role[0]) | {random.randint(1, userSize)})
        individual[0] = utils.localOptimization(individual[0])
    if random.random() < addPermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        length = len(role[1])
        while ((length < permissionSize) & (len(role[1]) == length)):
            role[1] = list(set(role[1]) | {random.randint(1, permissionSize)})
        individual[0] = utils.localOptimization(individual[0])
    return individual,


# Crossover Function
def mateFunc(ind1, ind2):
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
# Evolutionary algorithm
# -----------------------------------------------------------------------------------
def evolution(Original, POP_SIZE, CXPB, MUTPB, NGEN, checkpoint, pickleFile):
    start = datetime.datetime.now()
    print(start)
    time = 0
    fitnessValues = []
    genStart = 0
    pop = []

    # Creator
    #creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # Get Checkpoint
    if (checkpoint & os.path.isfile(pickleFile)):
        print("Use checkpoint: True")
        cp = pickle.load(open(pickleFile, "rb"))
        pop = cp["population"]
        genStart = int(cp["generation"])
        Original = cp["Original"]
        fitnessValues=cp["fitnessValues"]
        time=cp["time"]
        random.setstate(cp["rndstate"])
    else:
        print("Use checkpoint: False")

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
    toolbox.register("evaluate", evalFunc, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=0.25, removeRolePB=0.25, removeUserPB=0.25, removePermissionPB=0.25,
                     addUserPB=0.25, addPermissionPB=0.25, userSize=userSize, permissionSize=permissionSize)
    toolbox.register("select", tools.selTournament, tournsize=5)
    #toolbox.register("select", tools.selTournament, tournsize=10)

    # History, tracks the genealogy of the individuals in a population
    history = tools.History()
    toolbox.decorate("mate", history.decorator)
    toolbox.decorate("mutate", history.decorator)

    # Creating the Population
    if (not pop):
        print("Creating new Population")
        pop = toolbox.population(n=POP_SIZE)

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Begin the evolution
    #hof = tools.HallOfFame(maxsize=1)
    #stats = tools.Statistics(lambda ind: ind.fitness.values)
    #stats.register("avg", numpy.mean)
    #stats.register("std", numpy.std)
    #stats.register("min", numpy.min)
    #stats.register("max", numpy.max)

    # pop, log = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, halloffame=hof, stats=stats, verbose=False)
    # cp = dict(population=pop, generation=300, rndstate=random.getstate(), Original=Original)
    # pickle.dump(cp, open("..\\Output\\checkpoint.pkl", "wb"), 2)

    freq = 50
    stop = False
    g = genStart+1
    #print("Generation "+str(g))
    while ((not stop) & (g <= genStart+NGEN)):
        #if g % freq == 0:
        #    print("Generation "+str(g))
        #if g % freq == 0:
            #results = visual.addPopulationToPlot(pop, g, Original, results)
            #results = visual.addBestIndividualToPlot(pop, g, Original, results)
        pop = toolbox.select(pop, k=len(pop))
        pop = algorithms.varAnd(pop, toolbox, cxpb=CXPB, mutpb=MUTPB)

        # Evaluate individuals, which need a evaluation
        invalids = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalids)
        for ind, fit in zip(invalids, fitnesses):
            ind.fitness.values = fit
            if (fit[0] == 0):
                stop = True

        # Add Fitness values to results
        for ind in pop:
            fitnessValues.append([g,ind.fitness.values[0]])

        g += 1

    g -= 1
    # Show history of the best
    '''h = history.getGenealogy(hof[0], max_depth=5)
	graph = networkx.DiGraph(h)
	graph = graph.reverse()     # Make the grah top-down
	colors = [toolbox.evaluate(history.genealogy_history[i])[0] for i in graph]
	#pos = networkx.graphviz_layout(graph, prog="dot")
	#networkx.draw(graph, pos, node_color=colors)
	networkx.draw(graph, node_color=colors)
	plt.show()'''

    # Add final population to results
    #results = visual.addPopulationToPlot(pop, g, Original, results)
    #results = visual.addBestIndividualToPlot(pop, g, Original, results)

    # Print final population
    #visual.printPopulation(pop)
    print("==> Generation "+str(g))

    end = datetime.datetime.now()
    timediff = end-start
    time = time + timediff.total_seconds()

    # Set Checkpoint
    cp = dict(population=pop, generation=g, rndstate=random.getstate(), Original=Original, fitnessValues=fitnessValues, time=time)
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("Dump Pickle")

    return pop, fitnessValues, g, time

# -----------------------------------------------------------------------------------
# MAINoptions
# -----------------------------------------------------------------------------------
# GLOBAL PARAMETERS
testdata = [[1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 1, 1], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 1, 1], [1, 0, 0, 1, 1]]
testdata2 = [[3, 3, 0, 0, 0], [2, 0, 0, 2, 2], [1, 0, 1, 1, 1], [2, 0, 0, 2, 2], [2, 0, 0, 2, 2], [4, 3, 0, 2, 2], [2, 0, 0, 2, 2]]
Original = numpy.matrix(testdata2)
#Original = utils.generateGoalMatrix(4, 10, 10)
#Original = numpy.matrix(parser.read("..\\TestData\\healthcare.rbac"))

pickleFile = "..\\Output\\checkpoint.pkl"

# EVOLUTION PARAMETERS
POP_SIZE = 5
CXPB = 0.25
MUTPB = 0.25
NGEN = 5

population, fitnessValues, generation, time = evolution(Original, POP_SIZE, CXPB, MUTPB, NGEN, True, pickleFile)

print("Total in seconds: "+str(time))
minutes = int(time/60)
if (minutes > 0):
    print("Minutes: "+str(minutes))
    print("Seconds: "+str(time-(minutes*60)))

visual.showBestResult(population,generation,Original)
visual.showFitness(generation,POP_SIZE,fitnessValues)


