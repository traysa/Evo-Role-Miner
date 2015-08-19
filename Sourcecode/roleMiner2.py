import random
import numpy
from deap import creator, base, tools, algorithms
import matplotlib.pyplot as plt
import networkx
import pickle

#-----------------------------------------------------------------------------------
#Data Generation
#-----------------------------------------------------------------------------------
def createRandomMatrix(x, y):
    maxVal = 1
    matrix = []
    for i in range(x):
        matrix.append([random.randint(0,maxVal) for el in range(y)])
    return matrix

def createEmptyMatrix(x, y):
    maxVal = 1
    matrix = []
    for i in range(x):
        matrix.append([0 for el in range(y)])
    return matrix

def generateGoalMatrix(roles):
	A = createRandomMatrix(users,roles)
	B = createRandomMatrix(roles,permissions)
	Original = multiplyMatrix(A,B)
	#printMatrix(Original)
	return Original

#-----------------------------------------------------------------------------------
#Matrix operations
#-----------------------------------------------------------------------------------
def printMatrix(matrix):
    matrix = numpy.array(matrix, dtype=int)
    for line in matrix:
        print("\t".join(map(str,line)))

def multiplyMatrix(A,B):
    A = numpy.matrix(A, dtype=bool)
    B = numpy.matrix(B, dtype=bool)
    C = A * B
    return C

def subtractMatrix(A,B):
    A = numpy.matrix(A, dtype=int)
    B = numpy.matrix(B, dtype=int)
    C = A - B
    return C

def countDiffs(matrix):
	diff1 = (matrix == 1).sum()
	diff2 = (matrix == -1).sum()
	return diff1,diff2

#-----------------------------------------------------------------------------------
#Population Visualization
#-----------------------------------------------------------------------------------
def showResults(populationSize):
	fig,plots= plt.subplots(divmod(len(results),populationSize+1)[0],populationSize+1)
	p = 0
	for ay in plots:
		individual = 1
		for ax in ay:
			matrix = numpy.array(results[p][1])
			x_length = matrix.shape[1]
			y_length = matrix.shape[0]
			ax.pcolor(matrix,cmap=plt.cm.Blues,edgecolors='#FFFFFF',linewidths=0.5)
			ax.set_xticks(numpy.arange(x_length)+0.5)
			ax.set_yticks(numpy.arange(y_length)+0.5)
			ax.xaxis.tick_top()
			ax.yaxis.tick_left()
			ax.set_xlim(0, x_length)
			ax.set_ylim(0, y_length)
			ax.invert_yaxis()
			ax.set_xticklabels(range(0,x_length),minor=False,fontsize=8)
			ax.set_yticklabels(range(0,y_length),minor=False,fontsize=8)
			ax.tick_params(width=0)
			if individual == len(ay):
				ax.set_ylabel('Original')
			else:
				ax.set_ylabel('Individual '+str(individual))
				ax.set_xlabel('Gen='+str(results[p][2])+'\nEval='+str(results[p][0][0])+','+str(results[p][0][1])+'\nRoles='+str(results[p][0][2]))
			individual += 1
			p = p+1	
	fig.tight_layout()
	plt.show()

def addPopulationToPlot(pop,generation):
	printPopulation(pop)
	for ind in pop:
		fit = evalFunc(ind)
		matrix = resolveChromosomeIntoMatrix(ind[0])
		results.append([fit,matrix,generation])
	results.append([0,Original])
	return results

def printPopulation(pop):
	for ind in pop:
		print(str(ind.fitness.values)+" -- "+str(ind[0]))

#-----------------------------------------------------------------------------------
#Help functions
#-----------------------------------------------------------------------------------
def generateGene():
	gene = []
	# Create random length list of users
	user_list = []
	for i in range(1,users+1):
		if (random.randint(0,1)):
			user_list.append(i)
	if (len(user_list) < 1):
		user_list.append(random.randint(1,users))
	gene.append(user_list)
	# Create random length list of permissions
	permisson_list = []
	for i in range(1,permissions+1):
		if (random.randint(0,1)):
			permisson_list.append(i)
	if (len(permisson_list) < 1):
		permisson_list.append(random.randint(1,permissions))
	gene.append(permisson_list)
	return gene

def resolveChromosomeIntoMatrix(chromosome):
	matrix = createEmptyMatrix(users, permissions)
	# Iterate through all genes of a chromosome
	for gene in range(0,len(chromosome)):
		#print("Gene: " +str(gene))
		#print(chromosome[gene])
		user_list = chromosome[gene][0]
		permission_list = chromosome[gene][1]
		for user in user_list:
			for permission in permission_list:
				matrix[user-1][permission-1] = 1				
	return matrix

def combineObjects(offspring, index):
	values = numpy.array(offspring)[:,index]
	removalList = []
	#print("\nUSER COMBINING: "+str(values))
	for x, left in enumerate(values):
		for y, right in enumerate(values[x:]):
			if ((y+x not in removalList) & (x != y+x) & (len(left)==len(right)) & (len(left)==(len(set(left) & set(right))))):				
				print("USER COMBINING: item%s in %s has %s values in common with item%s"%(x, values, len(left), y+x))
				offspring[x][1] = list(set(offspring[x][1]) | set(offspring[y+x][1]))
				offspring[y+x][0] = []
				removalList.append(y+x)
	i = len(removalList)-1
	while i >= 0:
		del offspring[removalList[i]]
		i = i-1
	return offspring

def localOptimization(offspring):
	'Combine Users'
	offspring = combineObjects(offspring, 0)
	'Combine Permissions'
	offspring = combineObjects(offspring, 1)
	#print("\nOPTIMIZATION: "+str(offspring))
	return offspring

#-----------------------------------------------------------------------------------
#Evolutionary algorithm functions
#-----------------------------------------------------------------------------------
#Initialization
def generateChromosome(maxRoles):
	chromosome = []
	#Create random number of genes (roles) for one chromosome
	for i in range(0,random.randint(1,maxRoles)):
		gene = generateGene()
		# Add gene to chromosome
		chromosome.append(gene)
	chromosome = localOptimization(chromosome)
	return chromosome

#Evaluation Function
def evalFunc(individual):	
	#print("----------------------------------------")
	#print("EVALUATE INDIVIDUAL: "+str(individual[0]))
	matrix = resolveChromosomeIntoMatrix(individual[0])
	diffMatrix = subtractMatrix(matrix,Original)
	'Violation of confidentiality and data availability'
	conf,accs = countDiffs(diffMatrix) 
	numberOfRoles = len(individual[0])
	return conf,accs,numberOfRoles

#Mutation Function
def mutFunc(individual, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB):
	print("----------------------------------------")
	print("MUTATE INDIVIDUAL: "+str(individual[0]))
	if random.random() < addRolePB:
		gene = generateGene()
		print("--> Add a role: "+str(gene))
		individual[0].append(gene)
		individual[0] = localOptimization(individual[0])
	if ((len(individual[0])>1) & (random.random() < removeRolePB)):
		role = individual[0][random.randint(0,len(individual[0])-1)]
		print("--> Remove a role: "+str(role))
		del role
	if random.random() < removeUserPB:
		role = individual[0][random.randint(0,len(individual[0])-1)]
		print("--> Remove user of a role: "+str(role[0]))
		if (len(role[0]) > 1):
			del role[0][random.randint(0,len(role[0])-1)]
			individual[0] = localOptimization(individual[0])
	if random.random() < removePermissionPB:
		role = individual[0][random.randint(0,len(individual[0])-1)]
		print("--> Remove permission of a role: "+str(role[1]))
		if (len(role[1]) > 1):
			del role[1][random.randint(0,len(role[1])-1)]
			individual[0] = localOptimization(individual[0])
	if random.random() < addUserPB:
		role = individual[0][random.randint(0,len(individual[0])-1)]
		print("--> Add user to a role: "+str(role[0]))
		length = len(role[0])
		while ((length < users) & (len(role[0]) == length)):
			role[0] = list(set(role[0])|{random.randint(1,users)})
		individual[0] = localOptimization(individual[0])
	if random.random() < addPermissionPB:
		role = individual[0][random.randint(0,len(individual[0])-1)]
		print("--> Add permission to a role: "+str(role[1]))
		length = len(role[1])
		while ((length < permissions) & (len(role[1]) == length)):
			role[1] = list(set(role[1])|{random.randint(1,permissions)})
		individual[0] = localOptimization(individual[0])
	print("MUTATED INDIVIDUAL: "+str(individual[0]))	
	return individual,

#Crossover Function
def mateFunc(ind1, ind2):
	temp1 = ind1[0]
	temp2 = ind2[0]
	size = min(len(temp1), len(temp2))
	if size > 1:
		print("----------------------------------------")
		print("CROSSOVER INDIVIDUALS")
		#print("Ind1: "+str(ind1[0])+"\nInd2: "+str(ind2[0])))
		cxpoint = random.randint(1, size - 1)
		temp1[cxpoint:], temp2[cxpoint:] = temp2[cxpoint:], temp1[cxpoint:]
		temp1 = localOptimization(temp1)
		temp2 = localOptimization(temp2)
		#print("Ind1: "+str(ind1[0])+"\nInd2: "+str(ind2[0]))
	#else:
		#print("skip mating")
	return ind1, ind2
	
#-----------------------------------------------------------------------------------
#Evolutionary algorithm
#-----------------------------------------------------------------------------------
# Evolution
def evolution(Original,POP_SIZE,CXPB,MUTPB,NGEN,checkpoint):

	# Creator
	creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0,-1.0))
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
	toolbox.register("mutate", mutFunc, addRolePB=0.25, removeRolePB=0.25, removeUserPB=0.25, removePermissionPB=0.25, addUserPB=0.25, addPermissionPB=0.25)
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
	#pop, log = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, halloffame=hof, stats=stats, verbose=False)
	#cp = dict(population=pop, generation=300, rndstate=random.getstate(), Original=Original)
	#pickle.dump(cp, open("..\\Output\\checkpoint.pkl", "wb"), 2)
	freq = NGEN / 4
	pickleFreq = 5
	for g in range(NGEN):
		print("=======================================================")
		print("GENERATION: "+str(g))
		if g % freq == 0:
			addPopulationToPlot(pop,g)
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
	addPopulationToPlot(pop,g)

#-----------------------------------------------------------------------------------
#MAIN
#-----------------------------------------------------------------------------------
# GLOBAL PARAMETERS
results = []
users = 5
permissions = 10
Original = generateGoalMatrix(4)

# EVOLUTION PARAMETERS
POP_SIZE = 8
CXPB=0.25
MUTPB=0.25
NGEN=1000

evolution(Original,POP_SIZE,CXPB,MUTPB,NGEN,False)
showResults(POP_SIZE)