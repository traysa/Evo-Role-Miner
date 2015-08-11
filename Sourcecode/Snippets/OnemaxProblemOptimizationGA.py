import random
import numpy
from deap import creator, base, tools, algorithms

## Creator
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

## Toolbox
toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_bool", random.randint, 0, 1)
# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 3)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

## Evaluation Function
def evalOneMax(individual):
    return sum(individual),

## Genetic Operators
toolbox.register("evaluate", evalOneMax)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)


## Evolving the Population

## Creating the Population
pop = toolbox.population(n=3)

# Evaluate the entire population
fitnesses = list(map(toolbox.evaluate, pop))
for ind, fit in zip(pop, fitnesses):
	ind.fitness.values = fit

# The Appeal of Evolution
# Begin the evolution
CXPB=0.5
MUTPB=0.1
hof = tools.HallOfFame(1)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", numpy.mean)
stats.register("std", numpy.std)
stats.register("min", numpy.min)
stats.register("max", numpy.max)
pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, stats=stats, verbose=True)
'''NGEN=40
for gen in range(NGEN):
	print("-- Generation %i --" % gen)

	for i in pop:
		print(i)
	# Gather all the fitnesses in one list and print the stats
	fits = [ind.fitness.values[0] for ind in pop]

	length = len(pop)
	mean = sum(fits) / length
	sum2 = sum(x*x for x in fits)
	std = abs(sum2 / length - mean**2)**0.5

	print("  Min %s" % min(fits))
	print("  Max %s" % max(fits))
	print("  Avg %s" % mean)
	print("  Std %s" % std)

	offspring = algorithms.varAnd(pop, toolbox, cxpb=CXPB, mutpb=MUTPB)###
	# Select the next generation individuals
	offspring = toolbox.select(pop, len(pop))
	# Clone the selected individuals
	offspring = list(map(toolbox.clone, offspring))

	# Apply crossover and mutation on the offspring
	for child1, child2 in zip(offspring[::2], offspring[1::2]):
		if random.random() < CXPB:
			toolbox.mate(child1, child2)
			del child1.fitness.values
			del child2.fitness.values

	for mutant in offspring:
		if random.random() < MUTPB:
			toolbox.mutate(mutant)
			del mutant.fitness.values###
	# Evaluate the individuals with an invalid fitness
	invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
	fitnesses = map(toolbox.evaluate, invalid_ind)
	for ind, fit in zip(invalid_ind, fitnesses):
		ind.fitness.values = fit

	pop[:] = offspring'''
