import random
import numpy
from deap import creator, base, tools, algorithms
import matplotlib.pyplot as plt
import networkx
import pickle
import re
import rm_MatrixOperators as matrixOps

# -----------------------------------------------------------------------------------
# Data Generation for RoleMiner
# -----------------------------------------------------------------------------------
def generateGoalMatrix(roles, users, permissions):
    A = matrixOps.createRandomMatrix(users, roles)
    B = matrixOps.createRandomMatrix(roles, permissions)
    Original = matrixOps.multiplyMatrix(A, B)
    # printMatrix(Original)
    return Original

# -----------------------------------------------------------------------------------
# Help functions
# -----------------------------------------------------------------------------------
def resolveChromosomeIntoMatrix(chromosome, users, permissions):
    matrix = matrixOps.createEmptyMatrix(users, permissions)
    # Iterate through all genes of a chromosome
    for gene in range(0, len(chromosome)):
        # print("Gene: " +str(gene))
        # print(chromosome[gene])
        user_list = chromosome[gene][0]
        permission_list = chromosome[gene][1]
        for user in user_list:
            for permission in permission_list:
                matrix[user - 1][permission - 1] = 1
    return matrix

def generateGene():
    gene = []
    # Create random length list of users
    user_list = []
    for i in range(1, users + 1):
        if (random.randint(0, 1)):
            user_list.append(i)
    if (len(user_list) < 1):
        user_list.append(random.randint(1, users))
    gene.append(user_list)
    # Create random length list of permissions
    permisson_list = []
    for i in range(1, permissions + 1):
        if (random.randint(0, 1)):
            permisson_list.append(i)
    if (len(permisson_list) < 1):
        permisson_list.append(random.randint(1, permissions))
    gene.append(permisson_list)
    return gene

def combineObjects(offspring, index):
    values = numpy.array(offspring)[:, index]
    removalList = []
    # print("\nUSER COMBINING: "+str(values))
    for x, left in enumerate(values):
        for y, right in enumerate(values[x:]):
            if ((y + x not in removalList) & (x != y + x) & (len(left) == len(right)) & (
                        len(left) == (len(set(left) & set(right))))):
                print(
                    "USER COMBINING: item%s in %s has %s values in common with item%s" % (x, values, len(left), y + x))
                offspring[x][1] = list(set(offspring[x][1]) | set(offspring[y + x][1]))
                offspring[y + x][0] = []
                removalList.append(y + x)
    i = len(removalList) - 1
    while i >= 0:
        del offspring[removalList[i]]
        i = i - 1
    return offspring

def localOptimization(offspring):
    'Combine Users'
    offspring = combineObjects(offspring, 0)
    'Combine Permissions'
    offspring = combineObjects(offspring, 1)
    # print("\nOPTIMIZATION: "+str(offspring))
    return offspring

# -----------------------------------------------------------------------------------
# Evolutionary algorithm functions
# -----------------------------------------------------------------------------------
# Initialization
def generateChromosome(maxRoles):
    chromosome = []
    # Create random number of genes (roles) for one chromosome
    for i in range(0, random.randint(1, maxRoles)):
        gene = generateGene()
        # Add gene to chromosome
        chromosome.append(gene)
    chromosome = localOptimization(chromosome)
    return chromosome


# Evaluation Function
def evalFunc(individual):
    # print("----------------------------------------")
    # print("EVALUATE INDIVIDUAL: "+str(individual[0]))
    matrix = resolveChromosomeIntoMatrix(individual[0])
    diffMatrix = matrixOps.subtractMatrix(matrix, Original)
    'Violation of confidentiality and data availability'
    conf, accs = matrixOps.countDiffs(diffMatrix)
    numberOfRoles = len(individual[0])
    #return conf, accs, numberOfRoles
    #temp = (conf+accs)
    return numberOfRoles,


# Mutation Function
def mutFunc(individual, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB):
    print("----------------------------------------")
    print("MUTATE INDIVIDUAL: " + str(individual[0]))
    if random.random() < addRolePB:
        gene = generateGene()
        print("--> Add a role: " + str(gene))
        individual[0].append(gene)
        individual[0] = localOptimization(individual[0])
    if ((len(individual[0]) > 1) & (random.random() < removeRolePB)):
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        print("--> Remove a role: " + str(role))
        del role
    if random.random() < removeUserPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        print("--> Remove user of a role: " + str(role[0]))
        if (len(role[0]) > 1):
            del role[0][random.randint(0, len(role[0]) - 1)]
            individual[0] = localOptimization(individual[0])
    if random.random() < removePermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        print("--> Remove permission of a role: " + str(role[1]))
        if (len(role[1]) > 1):
            del role[1][random.randint(0, len(role[1]) - 1)]
            individual[0] = localOptimization(individual[0])
    if random.random() < addUserPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        print("--> Add user to a role: " + str(role[0]))
        length = len(role[0])
        while ((length < users) & (len(role[0]) == length)):
            role[0] = list(set(role[0]) | {random.randint(1, users)})
        individual[0] = localOptimization(individual[0])
    if random.random() < addPermissionPB:
        role = individual[0][random.randint(0, len(individual[0]) - 1)]
        print("--> Add permission to a role: " + str(role[1]))
        length = len(role[1])
        while ((length < permissions) & (len(role[1]) == length)):
            role[1] = list(set(role[1]) | {random.randint(1, permissions)})
        individual[0] = localOptimization(individual[0])
    print("MUTATED INDIVIDUAL: " + str(individual[0]))
    return individual,


# Crossover Function
def mateFunc(ind1, ind2):
    temp1 = ind1[0]
    temp2 = ind2[0]
    size = min(len(temp1), len(temp2))
    if size > 1:
        print("----------------------------------------")
        print("CROSSOVER INDIVIDUALS")
        # print("Ind1: "+str(ind1[0])+"\nInd2: "+str(ind2[0])))
        cxpoint = random.randint(1, size - 1)
        temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
        temp1 = localOptimization(temp1)
        temp2 = localOptimization(temp2)
    # print("Ind1: "+str(ind1[0])+"\nInd2: "+str(ind2[0]))
    # else:
    # print("skip mating")
    return ind1, ind2


# -----------------------------------------------------------------------------------
# Evolutionary algorithm
# -----------------------------------------------------------------------------------
def evolution(Original, POP_SIZE, CXPB, MUTPB, NGEN, checkpoint):
    # Creator
    #creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # Toolbox
    toolbox = base.Toolbox()
    # Chromosome generator
    toolbox.register("chromosome", generateChromosome, users)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.chromosome, 1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic Operators
    toolbox.register("evaluate", evalFunc)
    toolbox.register("mate", mateFunc)
    toolbox.register("mutate", mutFunc, addRolePB=0.25, removeRolePB=0.25, removeUserPB=0.25, removePermissionPB=0.25,
                     addUserPB=0.25, addPermissionPB=0.25)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # History, tracks the genealogy of the individuals in a population
    history = tools.History()
    toolbox.decorate("mate", history.decorator)
    toolbox.decorate("mutate", history.decorator)

    # Creating the Population
    pop = toolbox.population(n=POP_SIZE)
    if (checkpoint):
        print("Use checkpoint: True")
        cp = pickle.load(open("..\\Output\\checkpoint.pkl", "rb"))
        pop = cp["population"]
        g = cp["generation"]
        Original = cp["Original"]
        random.setstate(cp["rndstate"])

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Begin the evolution
    hof = tools.HallOfFame(maxsize=1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    # pop, log = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, halloffame=hof, stats=stats, verbose=False)
    # cp = dict(population=pop, generation=300, rndstate=random.getstate(), Original=Original)
    # pickle.dump(cp, open("..\\Output\\checkpoint.pkl", "wb"), 2)
    freq = NGEN / 2
    pickleFreq = 5
    for g in range(NGEN):
        print("=======================================================")
        print("GENERATION: " + str(g))
        if g % freq == 0:
            addPopulationToPlot(pop, g)
            #addBestIndividualToPlot(pop, g)
        pop = toolbox.select(pop, k=len(pop))
        pop = algorithms.varAnd(pop, toolbox, cxpb=CXPB, mutpb=MUTPB)
        invalids = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalids)
        for ind, fit in zip(invalids, fitnesses):
            ind.fitness.values = fit
        # Checkpoint
        if g % freq == 0:
            cp = dict(population=pop, generation=g, rndstate=random.getstate(), Original=Original)
            pickle.dump(cp, open("checkpoint.pkl", "wb"), 2)

        for ind in pop:
            Xs.append(g)
            Ys.append(ind.fitness.values[0])

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
    addPopulationToPlot(pop, g)
    #addBestIndividualToPlot(pop, g)


# -----------------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------------
def read(filename):
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = max(list(map(int, re.findall('u_U(.+?) ', data))))+1
    print(userCount)

    # Count permissions
    permCount = max(list(map(int, re.findall('p_P(.+?) ', data))))+1
    print(permCount)

    # Create UP Matrix
    UPmatrix = [[0 for i in range(permCount)] for j in range(userCount)]
    for line in lines:
        if line.startswith("u_"):
            parts = line.split(" ")
            user = parts[0]
            userId = int(user[3:])
            for i in range(len(parts)-1):
                perm = parts[i+1]
                permId = int(perm[3:])
                #print(str(userId)+" , "+str(permId))
                UPmatrix[userId][permId] = 1
    return UPmatrix, userCount, permCount


# -----------------------------------------------------------------------------------
# MAINoptions
# -----------------------------------------------------------------------------------
# GLOBAL PARAMETERS
results = []
users = 5
permissions = 8
Original = generateGoalMatrix(4, users, permissions)
#Original, users, permissions = read("..\\TestData\\healthcare.rbac")
#Original = numpy.matrix(temp)

# EVOLUTION PARAMETERS
POP_SIZE = 50
CXPB = 0.25
MUTPB = 0.25
NGEN = 10
Xs = []
Ys = []

evolution(Original, POP_SIZE, CXPB, MUTPB, NGEN, False)
#showResults(POP_SIZE)


# Find lowest values for cost and highest for savings
#p_front = pareto_frontier(Xs, Ys, maxX = False, maxY = False)
# Plot a scatter graph of all results
colors = plt.cm.rainbow(numpy.linspace(0, 1, NGEN))
start = 0
for c in colors:
    plt.scatter(Xs[start:start+POP_SIZE], Ys[start:start+POP_SIZE], color=c)
    start += POP_SIZE
#plt.scatter(Xs[:9], Ys[:9], c='b')
#plt.scatter(Xs[10:19], Ys[10:19], c='g')
#plt.scatter(Xs[20:29], Ys[20:29], c='r')
# Then plot the Pareto frontier on top
#plt.plot(p_front[0], p_front[1], c='r')
plt.show()
