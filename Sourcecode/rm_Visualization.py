__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# Visualizations for Role Miner
# -----------------------------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')
import numpy
import matplotlib.pyplot as plt
import rm_Utils as utils
from matplotlib.backends.backend_pdf import PdfPages
from collections import defaultdict
import os

# -----------------------------------------------------------------------------------
# Print Logbook into graph
# -----------------------------------------------------------------------------------
def plotLogbook(logbook, logbook_filename, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    gen = logbook.select("gen")
    fit_maxs = logbook.select("max")
    fit_mins = logbook.select("min")
    fit_avgs = logbook.select("avg")

    # Plot graphs
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlabel("Generation", fontsize=16)
    ax.set_ylabel("Fitness", fontsize=16)
    line1 = ax.plot(gen, fit_mins, "b-", label="Minimum Fitness")
    line2 = ax.plot(gen, fit_maxs, "r-", label="Maximum Fitness")
    line3 = ax.plot(gen, fit_avgs, "g-", label="Average Fitness")

    # Build legend
    lns = line1 + line2 + line3
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc="center right")

    if (saveAsPDF):
        print("Save logbook plot as PDF...")
        pp = PdfPages(logbook_filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        print("Save logbook plot as SVG...")
        plt.savefig(logbook_filename+".svg")

    if (saveAsPNG):
        print("Save logbook plot as PNG...")
        plt.savefig(logbook_filename+".png")
        if (showPNG):
            print("Show plot...")
            #plt.show()
            os.startfile(logbook_filename+".png")

    plt.close('all')

def plotLogbookForMultiObjective(logbook, logbook_filename, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    gen = logbook.select("gen")
    # Plot graphs
    fig, plots = plt.subplots(2,1,figsize=(12, 8))
    i = 1
    for ax in plots:

        # Get stats of objective
        fit_mins = logbook.chapters["fitnessObj"+str(i)].select("min")
        fit_maxs = logbook.chapters["fitnessObj"+str(i)].select("max")
        fit_avgs = logbook.chapters["fitnessObj"+str(i)].select("avg")

        # Create graphs
        ax.set_xlabel("Generation", fontsize=16)
        ax.set_ylabel("Fitness Objective "+str(i), fontsize=16)

        line1 = ax.plot(gen, fit_mins, "b-", label="Minimum Fitness")
        line2 = ax.plot(gen, fit_maxs, "r-", label="Maximum Fitness")
        line3 = ax.plot(gen, fit_avgs, "g-", label="Average Fitness")

        # Build legend
        lns = line1 + line2 + line3
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc="center right")
        i += 1

    if (saveAsPDF):
        print("Save logbook plot as PDF...")
        pp = PdfPages(logbook_filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        print("Save logbook plot as SVG...")
        plt.savefig(logbook_filename+".svg")

    if (saveAsPNG):
        print("Save logbook plot as PNG...")
        plt.savefig(logbook_filename+".png")
        if (showPNG):
            print("Show plot...")
            #plt.show()
            os.startfile(logbook_filename+".png")

    plt.close('all')

# -----------------------------------------------------------------------------------------
# Visualize evaluation values of population in a plot over generations (Single Objective)
# -----------------------------------------------------------------------------------------
def showFitnessInPlot(results, generations, freq, evolution_filename, info, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    print("\nCreate plot...")
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    # Plot a scatter graph of all results
    size = len(results)
    colors = plt.cm.rainbow(numpy.linspace(0, 1, size))

    generation = freq
    i = 0
    while ((i < size) and (generation <= generations)):
        c = colors[i]
        generationResults = numpy.array(results[generation], dtype=object)
        pop_size = len(generationResults)
        if (pop_size > 0):
            objective = [row[0] for row in generationResults]
            ax.scatter([generation] * pop_size, objective, color=c)
            #ax.scatter([generation] * pop_size, objective, color=c, cmap=colors)
            i += 1
        generation += freq
    ax.set_xlim(0,generation - freq + 0.5)
    ax.set_ylim(0)
    ax.set_xlabel('Generation', fontsize=16)
    ax.set_ylabel('Objective', fontsize=16)
    ax.tick_params(labelsize=14)
    ax.set_position((.1, .25, .8, .7)) # [pos from left, pos from bottom, width, height]

    Z = [[0,0],[0,0]]
    levels = range(0,generation - freq + 1,freq)
    data = ax.contourf(Z, levels, cmap=plt.cm.rainbow)
    cbar_axes=fig.add_axes([0.92,.25,.02,.7])  # [pos from left, pos from bottom, width, height]
    cbar = plt.colorbar(data, cax=cbar_axes)
    cbar.set_label('Generations', fontsize=16)
    cbar.ax.tick_params(labelsize=14)

    if (saveAsPDF or saveAsPNG):
       fig.text(0.1,0.01,"File: "+evolution_filename+"\n"+info, fontsize=14)
    else:
       fig.text(0.1,0.01,info, fontsize=14)
    print("DONE.\n")

    if (saveAsPDF):
        print("Save plot as PDF...")
        pp = PdfPages(evolution_filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        print("Save plot as SVG...")
        plt.savefig(evolution_filename+".svg")

    if (saveAsPNG):
        print("Save plot as PNG...")
        plt.savefig(evolution_filename+".png")
        if (showPNG):
            print("Show plot...")
            os.startfile(evolution_filename+".png")

    #plt.show(block=False)
    plt.close('all')

# -----------------------------------------------------------------------------------------
# Visualize evaluation values of population in a plot (Multi Objective)
# -----------------------------------------------------------------------------------------
def showFitnessInPlotForMultiObjective(results, generations, freq, evolution_filename, info, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    print("\nCreate plot...")
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    # Plot a scatter graph of all results
    size = len(results)
    colors = plt.cm.rainbow(numpy.linspace(start=0, stop=1, num=size))
    generation = freq
    i = 0
    while ((i < size) and (generation <= generations)):
        c = colors[i]
        generationResults = numpy.array(results[generation], dtype=object)
        pop_size = len(generationResults)
        if (pop_size > 0):
            objective1 = generationResults[:,0]
            objective2 = generationResults[:,1]
            ax.scatter(objective1, objective2, color=c)
            #ax.scatter([generation] * pop_size, objective, color=c, cmap=colors)
            # Find lowest values for cost and highest for savings
            p_front = pareto_frontier(objective1, objective2, maxX = False, maxY = False)
            ax.plot(p_front[0], p_front[1],color=c)
            i += 1
        generation += freq
    ax.set_xlim(0)
    ax.set_ylim(0)
    ax.set_xlabel('Objective1', fontsize=16)
    ax.set_ylabel('Objective2', fontsize=16)
    ax.tick_params(labelsize=14)
    ax.set_position((.1, .25, .76, .7)) # [pos from left, pos from bottom, width, height]

    Z = [[0,0],[0,0]]
    levels = range(0,generation - freq+1,freq)
    data = ax.contourf(Z, levels, cmap=plt.cm.rainbow)
    cbar_axes=fig.add_axes([0.88,.25,.02,.7])  # [pos from left, pos from bottom, width, height]
    cbar = plt.colorbar(data, cax=cbar_axes)
    cbar.set_label('Generations', fontsize=16)
    cbar.ax.tick_params(labelsize=14)

    if (saveAsPDF or saveAsPNG):
       fig.text(0.1,0.01,"File: "+evolution_filename+"\n"+info, fontsize=14)
    else:
       fig.text(0.1,0.01,info, fontsize=14)
    print("DONE.\n")

    if (saveAsPDF):
        print("Save plot as PDF...")
        pp = PdfPages(evolution_filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        print("Save plot as SVG...")
        plt.savefig(evolution_filename+".svg")

    if (saveAsPNG):
        print("Save plot as PNG...")
        plt.savefig(evolution_filename+".png")
        if (showPNG):
            print("Show plot...")
            os.startfile(evolution_filename+".png")

    plt.close('all')

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
    plt.close('all')

def showBestResult(top_pop, generation, Original, evolution_filename, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    #Find best in population
    #results = []
    #bestInd = []
    #bestFit = (1000000,)
    i = 1
    for ind in top_pop:
        results = []
        #fit = ind.fitness.values
        #if (bestFit > fit):
        #    bestFit = fit
        #    bestInd = ind
    #if (bestInd != []):
        UMatrix, PMatrix, UPMatrix = utils.resolveChromosomeIntoArrays(ind[0], Original.shape[0], Original.shape[1])
        results.append(UMatrix)
        results.append(PMatrix)
        results.append(UPMatrix)
        results.append(Original)

        fig, plots = plt.subplots(2, 2,figsize=(16,12))
        p = 0
        for ay in plots:
            for ax in ay:
                matrix = numpy.array(results[p])
                x_length = matrix.shape[1]
                y_length = matrix.shape[0]
                ax.pcolor(matrix, cmap=plt.cm.Blues, edgecolors='#FFFFFF', linewidths=0.5)
                ax.set_xticks(numpy.arange(x_length) + 0.5)
                ax.set_yticks(numpy.arange(y_length) + 0.5)
                #ax.xaxis.tick_top()
                #ax.yaxis.tick_left()
                ax.set_xlim(0, x_length)
                ax.set_ylim(0, y_length)
                ax.invert_yaxis()
                ax.set_xticklabels(range(1, x_length+1), minor=False, fontsize=8)
                ax.set_yticklabels(range(1, y_length+1), minor=False, fontsize=8)
                ax.tick_params(width=0)
                p = p + 1
        plots[0][0].set_ylabel('User-Role Matrix',fontsize=14)
        plots[0][1].set_ylabel('Role-Permission Matrix',fontsize=14)
        plots[1][0].set_ylabel('User-Permission Matrix',fontsize=14)
        plots[1][0].set_xlabel('Gen=' + str(generation) + '; Eval=' + str(ind.fitness.values),fontsize=14)
        plots[1][1].set_ylabel('Original',fontsize=14)
        #fig.tight_layout()
        fig.set_tight_layout(True)

        if (saveAsPDF):
            print("Save plot for Top "+str(i)+" as PDF...")
            pp = PdfPages(evolution_filename+"_"+str(i)+".pdf")
            pp.savefig(fig)
            pp.close()

        if (saveAsSVG):
            print("Save plot for Top "+str(i)+" as SVG...")
            plt.savefig(evolution_filename+"_"+str(i)+".svg")

        if (saveAsPNG):
            print("Save plot for Top "+str(i)+" as PNG...")
            plt.savefig(evolution_filename+"_"+str(i)+".png")
            if (showPNG):
                print("Show plot...")
                #plt.show()
                os.startfile(evolution_filename+"_"+str(i)+".png")

        i += 1
    plt.close('all')

def showAllRoles(top_pop, generation, Original, evolution_filename, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    i = len(top_pop)
    results = []

    UMatrix, PMatrix, UPMatrix = utils.resolveIndividualsIntoArrays(top_pop, Original.shape[0], Original.shape[1])
    results.append(UMatrix)
    results.append(PMatrix)
    results.append(UPMatrix)
    results.append(Original)

    fig, plots = plt.subplots(2, 2,figsize=(16,12))
    p = 0
    for ay in plots:
        for ax in ay:
            matrix = numpy.array(results[p])
            x_length = matrix.shape[1]
            y_length = matrix.shape[0]
            ax.pcolor(matrix, cmap=plt.cm.Blues, edgecolors='#FFFFFF', linewidths=0.5)
            ax.set_xticks(numpy.arange(x_length) + 0.5)
            ax.set_yticks(numpy.arange(y_length) + 0.5)
            #ax.xaxis.tick_top()
            #ax.yaxis.tick_left()
            ax.set_xlim(0, x_length)
            ax.set_ylim(0, y_length)
            ax.invert_yaxis()
            ax.set_xticklabels(range(1, x_length+1), minor=False, fontsize=8)
            ax.set_yticklabels(range(1, y_length+1), minor=False, fontsize=8)
            ax.tick_params(width=0)
            p = p + 1
    plots[0][0].set_ylabel('User-Role Matrix',fontsize=14)
    plots[0][1].set_ylabel('Role-Permission Matrix',fontsize=14)
    plots[1][0].set_ylabel('User-Permission Matrix',fontsize=14)
    plots[1][0].set_xlabel('Gen=' + str(generation),fontsize=14)
    plots[1][1].set_ylabel('Original',fontsize=14)
    #fig.tight_layout()
    fig.set_tight_layout(True)

    if (saveAsPDF):
        print("Save plot for Top "+str(i)+" as PDF...")
        pp = PdfPages(evolution_filename+"_"+str(i)+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        print("Save plot for Top "+str(i)+" as SVG...")
        plt.savefig(evolution_filename+"_"+str(i)+".svg")

    if (saveAsPNG):
        print("Save plot for Top "+str(i)+" as PNG...")
        plt.savefig(evolution_filename+"_"+str(i)+".png")
        if (showPNG):
            print("Show plot...")
            #plt.show()
            os.startfile(evolution_filename+"_"+str(i)+".png")

    plt.close('all')

# -----------------------------------------------------------------------------------------
# Visualize the URMatrix, PRMatrix and UPMatrix
# -----------------------------------------------------------------------------------------
def showRoleModel(UMatrix, PMatrix, UPMatrix, filename, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    results = []
    results.append(UMatrix)
    results.append(PMatrix)
    results.append(UPMatrix)
    results.append(UPMatrix)

    fig, plots = plt.subplots(2, 2,figsize=(16,12))
    p = 0
    for ay in plots:
        for ax in ay:
            matrix = numpy.array(results[p])
            x_length = matrix.shape[1]
            y_length = matrix.shape[0]
            ax.pcolor(matrix, cmap=plt.cm.Blues, edgecolors='#FFFFFF', linewidths=0.5)
            ax.set_xticks(numpy.arange(x_length) + 0.5)
            ax.set_yticks(numpy.arange(y_length) + 0.5)
            #ax.xaxis.tick_top()
            #ax.yaxis.tick_left()
            ax.set_xlim(0, x_length)
            ax.set_ylim(0, y_length)
            ax.invert_yaxis()
            ax.set_xticklabels(range(1, x_length+1), minor=False, fontsize=8)
            ax.set_yticklabels(range(1, y_length+1), minor=False, fontsize=8)
            ax.tick_params(width=0)
            p = p + 1
    plots[0][0].set_ylabel('User-Role Matrix',fontsize=14)
    plots[0][1].set_ylabel('Role-Permission Matrix',fontsize=14)
    plots[1][0].set_ylabel('User-Permission Matrix',fontsize=14)
    plots[1][1].set_ylabel('User-Permission Matrix',fontsize=14)
    #fig.tight_layout()
    fig.set_tight_layout(True)

    if (saveAsPDF):
        print("Save plot as PDF...")
        pp = PdfPages(filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        print("Save plot as SVG...")
        plt.savefig(filename+".svg")

    if (saveAsPNG):
        print("Save plot as PNG...")
        plt.savefig(filename+".png")
        if (showPNG):
            print("Show plot...")
            #plt.show()
            os.startfile(filename+".png")

    plt.close('all')

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
    plt.close('all')

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
