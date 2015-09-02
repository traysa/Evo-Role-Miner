__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# Visualizations for Role Miner
# -----------------------------------------------------------------------------------

import numpy
import matplotlib.pyplot as plt
import rm_Utils as utils


def showFitness(generationSize,populationSize,results):
    # Find lowest values for cost and highest for savings
    # p_front = pareto_frontier(Xs, Ys, maxX = False, maxY = False)
    # Plot a scatter graph of all results
    colors = plt.cm.rainbow(numpy.linspace(0, 1, generationSize))
    generation = 1
    for c in colors:
        genFitness = [row for row in results if generation == row[0]]
        genFitnessArray = numpy.array(genFitness, dtype=object)
        size = len(genFitnessArray)
        if (size > 0):
            fitnessValues = [row[1] for row in genFitnessArray]
            objective = [row[0] for row in fitnessValues]
            plt.scatter([generation] * size, objective, color=c)
        generation += 1
    plt.xlim(0,generationSize+0.5)
    plt.ylim(0)
    plt.xlabel('Generations')
    plt.ylabel('Objective')
    #plt.scatter(Xs[:9], Ys[:9], c='b')
    #plt.scatter(Xs[10:19], Ys[10:19], c='g')
    #plt.scatter(Xs[20:29], Ys[20:29], c='r')
    # Then plot the Pareto frontier on top
    #plt.plot(p_front[0], p_front[1], c='r')
    plt.show()

def showFitnessForMultiObjectives(generationSize,populationSize,results):
    # Find lowest values for cost and highest for savings
    # p_front = pareto_frontier(Xs, Ys, maxX = False, maxY = False)
    # Plot a scatter graph of all results
    colors = plt.cm.rainbow(numpy.linspace(0, 1, generationSize))
    generation = 1
    for c in colors:
        genFitness = [row for row in results if generation == row[0]]
        genFitnessArray = numpy.array(genFitness, dtype=object)
        size = len(genFitnessArray)
        if (size > 0):
            fitnessValues = [row[1] for row in genFitnessArray]
            objective1 = [row[0] for row in fitnessValues]
            objective2 = [row[1] for row in fitnessValues]
            plt.scatter(objective1, objective2, color=c)
        generation += 1
    plt.xlim(0)
    plt.ylim(0)
    plt.xlabel('Objective1')
    plt.ylabel('Objective2')
    #plt.scatter(Xs[:9], Ys[:9], c='b')
    #plt.scatter(Xs[10:19], Ys[10:19], c='g')
    #plt.scatter(Xs[20:29], Ys[20:29], c='r')
    # Then plot the Pareto frontier on top
    #plt.plot(p_front[0], p_front[1], c='r')
    plt.show()

def showResults(populationSize, results):
    fig, plots = plt.subplots(divmod(len(results), populationSize + 1)[0], populationSize + 1)
    p = 0
    for ay in plots:
        individual = 1
        for ax in ay:
            matrix = numpy.array(results[p][1])
            x_length = matrix.shape[1]
            y_length = matrix.shape[0]
            ax.pcolor(matrix, cmap=plt.cm.Blues, edgecolors='#FFFFFF', linewidths=0.5)
            ax.set_xticks(numpy.arange(x_length) + 0.5)
            ax.set_yticks(numpy.arange(y_length) + 0.5)
            ax.xaxis.tick_top()
            ax.yaxis.tick_left()
            ax.set_xlim(0, x_length)
            ax.set_ylim(0, y_length)
            ax.invert_yaxis()
            ax.set_xticklabels(range(0, x_length), minor=False, fontsize=8)
            ax.set_yticklabels(range(0, y_length), minor=False, fontsize=8)
            ax.tick_params(width=0)
            if individual == len(ay):
                ax.set_ylabel('Original')
            else:
                ax.set_ylabel('Individual ' + str(individual))
                ax.set_xlabel('Gen=' + str(results[p][2])
                              + ';\n Eval=' + str(results[p][0][0])
                              #+ ',' + str(results[p][0][1])
                              #+ ';\n Roles=' + str(results[p][0][1])
                              )
            individual += 1
            p = p + 1
    fig.tight_layout()
    plt.show()

def showBestResult(pop, generation, Original):
    #Find best in population
    results = []
    bestInd = []
    bestFit = (1000000,)
    for ind in pop:
        fit = ind.fitness.values
        if (bestFit > fit):
            bestFit = fit
            bestInd = ind
    if (bestInd != []):
        UMatrix, PMatrix, UPMatrix = utils.resolveChromosomeIntoArrays(bestInd[0], Original.shape[0], Original.shape[1])
        results.append(UMatrix)
        results.append(PMatrix)
        results.append(UPMatrix)
        results.append(Original)

    fig, plots = plt.subplots(2, 2)
    p = 0
    for ay in plots:
        for ax in ay:
            matrix = numpy.array(results[p])
            x_length = matrix.shape[1]
            y_length = matrix.shape[0]
            ax.pcolor(matrix, cmap=plt.cm.Blues, edgecolors='#FFFFFF', linewidths=0.5)
            ax.set_xticks(numpy.arange(x_length) + 0.5)
            ax.set_yticks(numpy.arange(y_length) + 0.5)
            ax.xaxis.tick_top()
            ax.yaxis.tick_left()
            ax.set_xlim(0, x_length)
            ax.set_ylim(0, y_length)
            ax.invert_yaxis()
            ax.set_xticklabels(range(1, x_length+1), minor=False, fontsize=8)
            ax.set_yticklabels(range(1, y_length+1), minor=False, fontsize=8)
            ax.tick_params(width=0)
            p = p + 1
    plots[0][0].set_ylabel('User-Role Matrix')
    plots[0][1].set_ylabel('Role-Permission Matrix')
    plots[1][0].set_ylabel('User-Permission Matrix')
    plots[1][0].set_xlabel('Gen=' + str(generation)
                              + ';\n Eval=' + str(bestFit))
    plots[1][1].set_ylabel('Original')
    fig.tight_layout()
    plt.show()

def showMatrix(matrix):
    fig, ax = plt.subplots()
    matrix = numpy.array(matrix)
    x_length = matrix.shape[1]
    y_length = matrix.shape[0]
    ax.pcolor(matrix, cmap=plt.cm.Blues, edgecolors='#FFFFFF', linewidths=0.5)
    ax.set_xticks(numpy.arange(x_length) + 0.5)
    ax.set_yticks(numpy.arange(y_length) + 0.5)
    ax.xaxis.tick_top()
    ax.yaxis.tick_left()
    ax.set_xlim(0, x_length)
    ax.set_ylim(0, y_length)
    ax.invert_yaxis()
    ax.set_xticklabels(range(1, x_length+1), minor=False, fontsize=8)
    ax.set_yticklabels(range(1, y_length+1), minor=False, fontsize=8)
    ax.tick_params(width=0)
    fig.tight_layout()
    plt.show()

def addPopulationToPlot(pop, generation, Original, results):
    #printPopulation(pop)
    for ind in pop:
        #fit = evalFunc(ind)
        fit = ind.fitness.values
        matrix = utils.resolveChromosomeIntoArray(ind[0], Original.shape[0], Original.shape[1])
        results.append([fit, matrix, generation])
    results.append([0, Original])
    return results

def addBestIndividualToPlot(pop, generation, Original, results):
    #printPopulation(pop)
    bestInd = []
    bestFit = (1000,1000,1000)
    for ind in pop:
        #fit = evalFunc(ind)
        fit = ind.fitness.values
        if (bestFit > fit):
            bestFit = fit
            bestInd = ind
    if (bestInd != []):
        matrix = utils.resolveChromosomeIntoArray(bestInd[0], Original.shape[0], Original.shape[1])
        results.append([bestFit, matrix, generation])
    results.append([0, Original])
    return results

def printPopulation(pop):
    i = 1
    for ind in pop:
        print(str(i) + " -- " + str(ind.fitness.values) + " -- " + str(ind[0]))
        i += 1

'''
Method to take two equally-sized lists and return just the elements which lie
on the Pareto frontier, sorted into order.
Default behaviour is to find the maximum for both X and Y, but the option is
available to specify maxX = False or maxY = False to find the minimum for either
or both of the parameters.
'''
def pareto_frontier(Xs, Ys, maxX = True, maxY = True):
    # Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
    # Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]: # Look for higher values of Y ...
                p_front.append(pair) # ... and add them to the Pareto frontier
        else:
            if pair[1] <= p_front[-1][1]: # Look for lower values of Y ...
                p_front.append(pair) # ... and add them to the Pareto frontier
    #  Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY
