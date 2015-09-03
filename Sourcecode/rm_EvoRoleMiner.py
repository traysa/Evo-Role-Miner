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
import fortin2013
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx

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

# Evaluation Function from paper (5)
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

# Evaluation Function
def evalFunc_Obj1(individual, userSize, permissionSize, orig):
    array = utils.resolveChromosomeIntoArray(individual[0], userSize, permissionSize)
    diffMatrix = matrixOps.subtractIntMatrix(A=array, B=numpy.matrix(orig,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    #numberOfRoles = len(individual[0])
    #return conf, accs, numberOfRoles
    temp = (conf+accs)
    return temp,

# Evaluation Function
def evalFunc_Obj2(individual, userSize, permissionSize, orig):
    numberOfRoles = len(individual[0])
    return numberOfRoles,

# Evaluation Function
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
        # Pick random gene (role)
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        length = len(role[0])
        #userSet = {x for x in range(1, userSize + 1)}
        # Add exactly 1 user, if the role does not already contain all users
        while ((length < userSize) & (len(role[0]) == length)):            #
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
# Evolutionary algorithm
# -----------------------------------------------------------------------------------
def evolution(Original, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6, NGEN, freq, checkpoint, pickleFile):
    print("Prepare evolutionary algorithm...")
    time = []
    results = defaultdict(list)
    genStart = 0
    pop = []

    # Creator
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # Get Checkpoint
    if (checkpoint & os.path.isfile(pickleFile)):
        print("Use checkpoint: True")
        cp = pickle.load(open(pickleFile, "rb"))
        pop = cp["population"]
        genStart = int(cp["generation"])
        Original = cp["Original"]
        results=cp["results"]
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
    toolbox.register("evaluate", evalFunc_Obj1, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=MUTPB_1, removeRolePB=MUTPB_2, removeUserPB=MUTPB_3, removePermissionPB=MUTPB_4,
                     addUserPB=MUTPB_5, addPermissionPB=MUTPB_6, userSize=userSize, permissionSize=permissionSize)
    toolbox.register("select", tools.selTournament, tournsize=5)

    # Creating the Population
    if (not pop):
        print("Generate new Population of "+str(POP_SIZE)+" individuals")
        pop = toolbox.population(n=POP_SIZE)

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Begin the evolution
    print("Start evolution...")
    start = datetime.datetime.now()
    print("Start time: "+str(start))
    #hof = tools.HallOfFame(maxsize=1)
    #stats = tools.Statistics(lambda ind: ind.fitness.values)
    #stats.register("avg", numpy.mean)
    #stats.register("std", numpy.std)
    #stats.register("min", numpy.min)
    #stats.register("max", numpy.max)
    stop = False
    g = genStart+1
    print("Start evolution with Generation "+str(g))
    while ((not stop) & (g <= genStart+NGEN)):
        pop = toolbox.select(pop, k=len(pop))
        pop = algorithms.varAnd(pop, toolbox, cxpb=CXPB, mutpb=MUTPB_All)

        # Evaluate individuals, which need a evaluation
        invalids = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalids)
        for ind, fit in zip(invalids, fitnesses):
            ind.fitness.values = fit
            # Stop condition
            #if (fit[0] == 0):
            #    stop = True

        # Add Fitness values to results
        if g % freq == 0:
            print("Generation "+str(g))
            for ind in pop:
                results[g].append(ind.fitness.values)

        g += 1

    end = datetime.datetime.now()
    timediff = end-start
    time.append(timediff.total_seconds())
    g -= 1
    # Print final population
    #visual.printPopulation(pop)
    print("==> Generation "+str(g))
    print("DONE.\n")

    # Set Checkpoint
    cp = dict(population=pop,
              generation=g,
              rndstate=random.getstate(),
              Original=Original,
              results=results,
              time=time,
              POP_SIZE=POP_SIZE,
              CXPB=CXPB,
              MUTPB_All=MUTPB_All,
              MUTPB_1=MUTPB_1,
              MUTPB_2=MUTPB_2,
              MUTPB_3=MUTPB_3,
              MUTPB_4=MUTPB_4,
              MUTPB_5=MUTPB_5,
              MUTPB_6=MUTPB_6,)
    if (not checkpoint):
        k = pickleFile.rfind("\\")
        pickleFile = pickleFile[:k+1] + datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")+"_" + pickleFile[k+1:]
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("Save checkpoint into "+str(pickleFile))

    return pop, results, g, time

# -----------------------------------------------------------------------------------
# Evolutionary algorithm
# -----------------------------------------------------------------------------------
def evolution_multi(Original, POP_SIZE, CXPB, MUTPB, NGEN, checkpoint, pickleFile):
    start = datetime.datetime.now()
    print("Start time: "+str(start))
    time = 0
    results = []
    genStart = 0
    pop = []

    # Creator
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # Get Checkpoint
    if (checkpoint & os.path.isfile(pickleFile)):
        print("Use checkpoint: True")
        cp = pickle.load(open(pickleFile, "rb"))
        pop = cp["population"]
        genStart = int(cp["generation"])
        Original = cp["Original"]
        results=cp["results"]
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
    toolbox.register("evaluate", evalFunc_Multi, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=0.25, removeRolePB=0.25, removeUserPB=0.25, removePermissionPB=0.25,
                     addUserPB=0.25, addPermissionPB=0.25, userSize=userSize, permissionSize=permissionSize)
    toolbox.register("select", tools.selNSGA2)

    # History, tracks the genealogy of the individuals in a population
    history = tools.History()
    toolbox.decorate("mate", history.decorator)
    toolbox.decorate("mutate", history.decorator)

    # Creating the Population
    if (not pop):
        print("Creating new Population of "+str(POP_SIZE))
        pop = toolbox.population(n=POP_SIZE)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))

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
        #print("Generation: "+str(g))

        # Vary the population
        offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]
        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)
            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values
        #offspring = algorithms.varOr(pop, toolbox, 100, cxpb=CXPB, mutpb=MUTPB)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            #if (fit[0] == 0):
            #    stop = True

        # Select the next generation population
        pop = toolbox.select(pop + offspring, len(pop))

        #record = stats.compile(pop)
        #logbook.record(gen=gen, evals=len(invalid_ind), **record)
        #print(logbook.stream)

        # Add Fitness values of population to results
        for ind in pop:
            results.append([g,ind.fitness.values])

        g += 1

    #top1 = tools.selBest(pop, k=1)

    #pareto_ind=pareto.items
    #pareto_data=numpy.array(toolbox.map(toolbox.evaluate, pareto_ind))
    #plt.plot(pareto_data[:,0],pareto_data[:,1])
    #plt.ylim(-0.5,0.0)
    #plt.show()

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
    cp = dict(population=pop, generation=g, rndstate=random.getstate(), Original=Original, results=results, time=time)
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("Dump Pickle")

    return pop, results, g, time

def evolution_multi_fortin2013(Original, POP_SIZE, CXPB, MUTPB, NGEN, checkpoint, pickleFile):
    start = datetime.datetime.now()
    print(start)
    time = 0
    results = []
    genStart = 0
    pop = []

    # Creator
    #creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # Get Checkpoint
    if (checkpoint & os.path.isfile(pickleFile)):
        print("Use checkpoint: True")
        cp = pickle.load(open(pickleFile, "rb"))
        pop = cp["population"]
        genStart = int(cp["generation"])
        Original = cp["Original"]
        results=cp["results"]
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
    toolbox.register("evaluate", evalFunc_Multi, userSize=userSize, permissionSize=permissionSize, orig=Original)
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=0.25, removeRolePB=0.25, removeUserPB=0.25, removePermissionPB=0.25,
                     addUserPB=0.25, addPermissionPB=0.25, userSize=userSize, permissionSize=permissionSize)
    #toolbox.register("select", tools.selTournament, tournsize=5)
    #toolbox.register("select", tools.selNSGA2)

    toolbox.register("preselect", fortin2013.selTournamentFitnessDCD)
    toolbox.register("select", fortin2013.selNSGA2)

    # History, tracks the genealogy of the individuals in a population
    history = tools.History()
    toolbox.decorate("mate", history.decorator)
    toolbox.decorate("mutate", history.decorator)

    # Creating the Population
    if (not pop):
        print("Creating new Population")
        pop = toolbox.population(n=POP_SIZE)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))

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
        #print("Generation: "+str(g))

        # Vary the population
        #offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = toolbox.preselect(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]
        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)
            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values
        #offspring = algorithms.varOr(pop, toolbox, 100, cxpb=CXPB, mutpb=MUTPB)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            #if (fit[0] == 0):
            #    stop = True

        # Select the next generation population
        pop = toolbox.select(pop + offspring, len(pop))

        #record = stats.compile(pop)
        #logbook.record(gen=gen, evals=len(invalid_ind), **record)
        #print(logbook.stream)

        # Add Fitness values of population to results
        for ind in pop:
            results.append([g,ind.fitness.values])

        g += 1

    #top1 = tools.selBest(pop, k=1)

    #pareto_ind=pareto.items
    #pareto_data=numpy.array(toolbox.map(toolbox.evaluate, pareto_ind))
    #plt.plot(pareto_data[:,0],pareto_data[:,1])
    #plt.ylim(-0.5,0.0)
    #plt.show()

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
    cp = dict(population=pop, generation=g, rndstate=random.getstate(), Original=Original, results=results, time=time)
    pickle.dump(cp, open(pickleFile, "wb"), 2)
    print("Dump Pickle")

    return pop, results, g, time

# -----------------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------------
# GLOBAL PARAMETERS
testdata = [[1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 1, 1], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 1, 1], [1, 0, 0, 1, 1]]
testdata2 = [[3, 3, 0, 0, 0], [2, 0, 0, 2, 2], [1, 0, 1, 1, 1], [2, 0, 0, 2, 2], [2, 0, 0, 2, 2], [4, 3, 0, 2, 2], [2, 0, 0, 2, 2]]
#Original = numpy.matrix(testdata2)
#Original = utils.generateGoalMatrix(4, 10, 10)
Original = numpy.matrix(parser.read("..\\TestData\\healthcare.rbac"))

pickleFile = "..\\Output\\checkpoint.pkl"

# EVOLUTION PARAMETERS
POP_SIZE = 100
CXPB = 0.25
MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6 = 0.25,0.25,0.25,0.25,0.25,0.25,0.25
NGEN = 100
freq = 5

#population, results, generation, time = evolution_multi_fortin2013(Original, POP_SIZE, CXPB, MUTPB, NGEN, False, pickleFile)
population, results, generation, timeArray = evolution(Original, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6, NGEN, freq, False, pickleFile)

time = sum(timeArray)
print("Total in seconds: "+str(time))
minutes = int(time/60)
if (minutes > 0):
    print("Minutes: "+str(minutes))
    print("Seconds: "+str(time-(minutes*60)))

visual.showFitnessInPlot(results, NGEN, 10)
#visual.showFitnessForMultiObjectives(generation,POP_SIZE,results)
#visual.showBestResult(population,generation,Original)
#visual.printPopulation(population)



