import random
import numpy
from deap import creator, base, tools, algorithms
import matplotlib.pyplot as plt
import networkx
import pickle

def createRandomMatrix(x, y):
    maxVal = 1
    matrix = []
    for i in range(x):
        matrix.append([random.randint(0,maxVal) for el in range(y)])
    return matrix

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
    A = numpy.matrix(A, dtype=bool)
    B = numpy.matrix(B, dtype=bool)
    C = A - B
    return C

def showMatrices(matrices):
	fig,plots= plt.subplots(divmod(len(matrices),4)[0],4)
	i = 0
	for ay in plots:
		for ax in ay:
			matrix = numpy.array(matrices[i])
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
			i = i+1	
		ay[0].set_ylabel('User')
		ay[0].set_xlabel('Role')
		ay[1].set_ylabel('Role')
		ay[1].set_xlabel('Permission')
		ay[2].set_ylabel('User')
		ay[2].set_xlabel('Permission')
	fig.tight_layout()
	plt.show()

def addPopulationToPlot(pop,C,matrices):
	for i in pop:
		A,B = resolveIndividual(i)
		matrices.append(A)
		matrices.append(B)
		matrices.append(multiplyMatrix(A,B))
		matrices.append(C)
	return matrices

def generateGoalMatrix():
	A = createRandomMatrix(users,roles)
	B = createRandomMatrix(roles,permissions)
	C = multiplyMatrix(A,B)
	printMatrix(C)
	#showMatrices([matrixA,matrixB,matrixC])
	return C

def resolveIndividual(individual):
	urlist = numpy.array(individual[:roles*users])
	shape = (users,roles)
	URMatrix = numpy.matrix(urlist.reshape(shape),dtype=bool)
	prlist = numpy.array(individual[:roles*permissions])
	shape = (roles,permissions)
	PRMatrix = numpy.matrix(prlist.reshape(shape),dtype=bool)
	return URMatrix, PRMatrix

## Evaluation Function
def evalFunc(individual):	
	URMatrix, PRMatrix = resolveIndividual(individual)
	return evalMatrices(URMatrix, PRMatrix),

def evalMatrices(URMatrix, PRMatrix):	
	UPMatrix = multiplyMatrix(URMatrix,PRMatrix)
	diffMatrix = subtractMatrix(UPMatrix,C)
	diff = diffMatrix.sum(dtype=int)
	#print("eval: " + str(diff))
	return diff

def mutFunc(individual, indpbUR, indpbUP):
	URMatrix, PRMatrix = resolveIndividual(individual)
	URArray = numpy.array(URMatrix).flatten()	
	for i in range(len(URArray)):
		if random.random() < indpbUR:
			individual[i] = type(individual[i])(not individual[i])
	for i in range(len(URArray),len(individual)):
		if random.random() < indpbUP:
			individual[i] = type(individual[i])(not individual[i])
	return individual,

def evolution(checkpoint):
	## Creator
	creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
	creator.create("Individual", list, fitness=creator.FitnessMin)

	## Toolbox
	toolbox = base.Toolbox()
	# Attribute generator
	toolbox.register("attr_bool", random.randint, 0, 1)
	# Structure initializers
	toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, roles*users+permissions*roles)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)

	## Genetic Operators
	toolbox.register("evaluate", evalFunc)
	toolbox.register("mate", tools.cxTwoPoint)
	toolbox.register("mutate", mutFunc, indpbUR=0.05, indpbUP=0.01)
	toolbox.register("select", tools.selTournament, tournsize=3)

	## History, tracks the genealogy of the individuals in a population
	history = tools.History()
	toolbox.decorate("mate", history.decorator)
	toolbox.decorate("mutate", history.decorator)

	## Evolving the Population

	## Creating the Population
	pop = toolbox.population(n=4)
	if (checkpoint):
		cp = pickle.load(open("..\\Output\\checkpoint.pkl", "rb"))
		pop = cp["population"]
		g = cp["generation"]
		C = cp["C"]
		random.setstate(cp["rndstate"])

	addPopulationToPlot(pop,C,matrices)

	# Evaluate the entire population
	fitnesses = list(map(toolbox.evaluate, pop))
	for ind, fit in zip(pop, fitnesses):
		ind.fitness.values = fit

	# The Appeal of Evolution
	# Begin the evolution
	CXPB=0.5
	MUTPB=0.2
	NGEN=400
	hof = tools.HallOfFame(maxsize=1)
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	stats.register("avg", numpy.mean)
	stats.register("std", numpy.std)
	stats.register("min", numpy.min)
	stats.register("max", numpy.max)
	pop, log = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, halloffame=hof, stats=stats, verbose=True)
	cp = dict(population=pop, generation=300, rndstate=random.getstate(), C=C)
	pickle.dump(cp, open("..\\Output\\checkpoint.pkl", "wb"), 2)
	
	'''for g in range(NGEN):
		pop = toolbox.select(pop, k=len(pop))
		pop = algorithms.varAnd(pop, toolbox, cxpb=CXPB, mutpb=MUTPB)
		invalids = [ind for ind in pop if not ind.fitness.valid]
		fitnesses = toolbox.map(toolbox.evaluate, invalids)
		for ind, fit in zip(invalids, fitnesses):
			ind.fitness.values = fit
		# Checkpoint
		freq = 5
		g = 0
		if g % freq == 0:
			cp = dict(population=pop, generation=g, rndstate=random.getstate(), C=C)
			pickle.dump(cp, open("checkpoint.pkl", "wb"), 2)'''

	# Show history of the best
	'''h = history.getGenealogy(hof[0], max_depth=5)
	graph = networkx.DiGraph(h)
	graph = graph.reverse()     # Make the grah top-down
	colors = [toolbox.evaluate(history.genealogy_history[i])[0] for i in graph]
	#pos = networkx.graphviz_layout(graph, prog="dot")
	#networkx.draw(graph, pos, node_color=colors)
	networkx.draw(graph, node_color=colors)
	plt.show()'''

	addPopulationToPlot(pop,C,matrices)

users = 5
permissions = 10
roles = 4
C = generateGoalMatrix()

'''A = createRandomMatrix(users,roles)
B = createRandomMatrix(roles,permissions)
print("A")
printMatrix(A)
print("B")
printMatrix(B)
print("C")
printMatrix(multiplyMatrix(A,B))
print(evalMatrices(A,B))'''

matrices = []
evolution(True)
showMatrices(matrices)