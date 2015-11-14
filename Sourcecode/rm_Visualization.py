__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# Visualizations for Role Miner
# -----------------------------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from collections import defaultdict
import rm_EADecoder as decoder
import os
import logging
logger = logging.getLogger('root')

# -----------------------------------------------------------------------------------
# Plot Logbook chapter into graph for single objective EAs
# -----------------------------------------------------------------------------------
def plotLogbookChapter(stat, logbook, ax):
    gen = logbook.select("gen")
    ax.set_xlabel("Generation", fontsize=16)
    ax.set_ylabel(stat, fontsize=16)
    #ax.set_position((.1, .18, .8, .72)) # [pos from left, pos from bottom, width, height]

    fit_maxs = logbook.chapters[stat].select("max")
    fit_mins = logbook.chapters[stat].select("min")
    fit_avgs = logbook.chapters[stat].select("avg")
    line1 = ax.plot(gen, fit_mins, "b-", label="Minimum "+stat)
    line2 = ax.plot(gen, fit_maxs, "r-", label="Maximum "+stat)
    line3 = ax.plot(gen, fit_avgs, "g-", label="Average "+stat)
    lns = line1 + line2 + line3

    # Build legend
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc="center right")
    return ax

# -----------------------------------------------------------------------------------
# Print Logbook into graph for single objective EAs
# -----------------------------------------------------------------------------------
def plotLogbook(logbook, logbook_filename, stats, title, info, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):

    # Plot graphs
    #fig, ax = plt.subplots(figsize=(12, 8))
    #fig = plt.figure(figsize=(12, 8))
    #ax = fig.add_subplot(111)

    if (len(stats)==1):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax = plotLogbookChapter(stats[0], logbook, ax)
        min = ax.get_ylim()[0]
        if (min > 0):
            min = 0
        max = ax.get_ylim()[1]
        ax.set_ylim(min,max)
        ax.set_position((.1, .18, .8, .72)) # [pos from left, pos from bottom, width, height]
        pre_title = "Fitness for: "
    else:
        fig, plots = plt.subplots(3, 2,figsize=(18,16))
        s = 0
        for ay in plots:
            for ax in ay:
                if (s < len(stats)):
                    stat = stats[s]
                    ax = plotLogbookChapter(stat, logbook, ax)
                    min = ax.get_ylim()[0]
                    if (min > 0):
                        min = 0
                    max = ax.get_ylim()[1]
                    ax.set_ylim(min,max)
                    s += 1
        pre_title = "Measures for: "
    fig.text(0.1,0.01,info, fontsize=10)
    plt.suptitle(pre_title+title, fontsize=20)
    logger.debug("DONE.\n")

    if (saveAsPDF):
        logger.debug("Save logbook plot as PDF...")
        pp = PdfPages(logbook_filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        logger.debug("Save logbook plot as SVG...")
        plt.savefig(logbook_filename+".svg")

    if (saveAsPNG):
        logger.debug("Save logbook plot as PNG...")
        plt.savefig(logbook_filename+".png")
        if (showPNG):
            logger.debug("Show plot...")
            #plt.show()
            os.startfile(logbook_filename+".png")
    plt.close('all')

# -----------------------------------------------------------------------------------
# Print Logbook into graph for multi objective EAs
# -----------------------------------------------------------------------------------
def plotLogbookForMultiObjective(logbook, logbook_filename, title, info, evalFunc, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    gen = logbook.select("gen")
    # Plot graphs
    fig, plots = plt.subplots(2,1,figsize=(12, 8))
    i = 0
    for ax in plots:

        # Get stats of objective
        fit_mins = logbook.chapters["fitnessObj"+str(i+1)].select("min")
        fit_maxs = logbook.chapters["fitnessObj"+str(i+1)].select("max")
        fit_avgs = logbook.chapters["fitnessObj"+str(i+1)].select("avg")

        # Create graphs
        ax.set_xlabel("Generation", fontsize=16)
        ax.set_ylabel("Objective: "+evalFunc[i], fontsize=16)

        line1 = ax.plot(gen, fit_mins, "b-", label="Minimum Fitness")
        line2 = ax.plot(gen, fit_maxs, "r-", label="Maximum Fitness")
        line3 = ax.plot(gen, fit_avgs, "g-", label="Average Fitness")

        # Build legend
        lns = line1 + line2 + line3
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc="center right")

        i+= 1

    fig.text(0.1,0.01,info, fontsize=10)
    plt.suptitle("Fitness for: "+title, fontsize=20)

    if (saveAsPDF):
        logger.debug("Save logbook plot as PDF...")
        pp = PdfPages(logbook_filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        logger.debug("Save logbook plot as SVG...")
        plt.savefig(logbook_filename+".svg")

    if (saveAsPNG):
        logger.debug("Save logbook plot as PNG...")
        plt.savefig(logbook_filename+".png")
        if (showPNG):
            logger.debug("Show plot...")
            #plt.show()
            os.startfile(logbook_filename+".png")

    plt.close('all')

# -----------------------------------------------------------------------------------
# Print Logbook AVG of several experiments into graph for single objective EAs
# -----------------------------------------------------------------------------------
def plotLogbookAVG(data, logbook_filename, stats, title, info, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):

    # Plot graphs
    #fig, ax = plt.subplots(figsize=(12, 8))
    #fig = plt.figure(figsize=(12, 8))
    #ax = fig.add_subplot(111)

    if (len(stats)==1):
        fig, ax = plt.subplots(figsize=(12, 8))
        temp = list(numpy.array(data)[:,1])
        ax = plotLogbookAVGData(stats[0], temp, ax)
        min = ax.get_ylim()[0]
        if (min > 0):
            min = 0
        max = ax.get_ylim()[1]
        ax.set_ylim(min,max)
        ax.set_position((.1, .18, .8, .72)) # [pos from left, pos from bottom, width, height]
        pre_title = "Fitness for: "
    else:
        fig, plots = plt.subplots(3, 2,figsize=(18,16))
        s = 0
        for ay in plots:
            for ax in ay:
                if (s < len(stats)):
                    stat = stats[s]
                    temp = list(numpy.array(data)[:,s+2])
                    ax = plotLogbookAVGData(stat, temp, ax)
                    min = ax.get_ylim()[0]
                    if (min > 0):
                        min = 0
                    max = ax.get_ylim()[1]
                    ax.set_ylim(min,max)
                    s += 1
        pre_title = "Measures for: "
    fig.text(0.1,0.01,info, fontsize=10)
    plt.suptitle(pre_title+title, fontsize=20)
    logger.debug("DONE.\n")

    if (saveAsPDF):
        logger.debug("Save logbook plot as PDF...")
        pp = PdfPages(logbook_filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        logger.debug("Save logbook plot as SVG...")
        plt.savefig(logbook_filename+".svg")

    if (saveAsPNG):
        logger.debug("Save logbook plot as PNG...")
        plt.savefig(logbook_filename+".png")
        if (showPNG):
            logger.debug("Show plot...")
            #plt.show()
            os.startfile(logbook_filename+".png")
    plt.close('all')
# -----------------------------------------------------------------------------------
# Plot data into graph for single objective EAs
# -----------------------------------------------------------------------------------
def plotLogbookAVGData(data_name,data, ax):
    gen = [i for i in range(0,len(data))]
    ax.set_xlabel("Generation", fontsize=16)
    ax.set_ylabel(data_name, fontsize=16)
    #ax.set_position((.1, .18, .8, .72)) # [pos from left, pos from bottom, width, height]
    line = ax.plot(gen, data, "r-")
    lns = line
    return ax

# -----------------------------------------------------------------------------------------
# Visualize evaluation values of population in a plot over generations (Single Objective)
# -----------------------------------------------------------------------------------------
def showFitnessInPlot(results, generations, freq, filename, title, info, evalFunc, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    logger.debug("\nCreate plot...")
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
    ax.set_ylabel('Objective: '+evalFunc, fontsize=16)
    ax.tick_params(labelsize=14)
    ax.set_position((.1, .18, .8, .72)) # [pos from left, pos from bottom, width, height]

    Z = [[-1,-1],[-1,-1]]
    #Z = [[0,0],[0,0]]
    levels = range(0,generation - freq + 1,freq)
    data = ax.contourf(Z, levels, cmap=plt.cm.rainbow)
    cbar_axes=fig.add_axes([0.92,.18,.02,.72])  # [pos from left, pos from bottom, width, height]
    cbar = plt.colorbar(data, cax=cbar_axes)
    cbar.set_label('Generations', fontsize=16)
    cbar.ax.tick_params(labelsize=14)

    fig.text(0.1,0.01,info, fontsize=10)
    plt.suptitle("Fitness for: "+title, fontsize=20)
    logger.debug("DONE.\n")

    if (saveAsPDF):
        logger.debug("Save plot as PDF...")
        pp = PdfPages(filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        logger.debug("Save plot as SVG...")
        plt.savefig(filename+".svg")

    if (saveAsPNG):
        logger.debug("Save plot as PNG...")
        plt.savefig(filename+".png")
        if (showPNG):
            logger.debug("Show plot...")
            os.startfile(filename+".png")

    #plt.show(block=False)
    plt.close('all')

# -----------------------------------------------------------------------------------------
# Visualize evaluation values of population in a plot (Multi Objective)
# -----------------------------------------------------------------------------------------
def showFitnessInPlotForMultiObjective(results, generations, freq, filename, title, info, evalFunc, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    logger.debug("\nCreate plot...")
    if (len(evalFunc)==2):
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
        ax.set_xlabel('Objective: '+evalFunc[0], fontsize=16)
        ax.set_ylabel('Objective: '+evalFunc[1], fontsize=16)
        ax.tick_params(labelsize=14)
        ax.set_position((.1, .18, .76, .72)) # [pos from left, pos from bottom, width, height]

        Z = [[-1,-1],[-1,-1]]
        #Z = [[0,0],[0,0]]
        levels = range(0,generation - freq+1,freq)
        data = ax.contourf(Z, levels, cmap=plt.cm.rainbow)
        cbar_axes=fig.add_axes([0.88,.18,.02,.72])  # [pos from left, pos from bottom, width, height]
        cbar = plt.colorbar(data, cax=cbar_axes)
        cbar.set_label('Generations', fontsize=16)
        cbar.ax.tick_params(labelsize=14)

        fig.text(0.1,0.01, info, fontsize=10)
        plt.suptitle("Fitness for: "+title, fontsize=20)
        logger.debug("DONE.\n")

        if (saveAsPDF):
            logger.debug("Save plot as PDF...")
            pp = PdfPages(filename+".pdf")
            pp.savefig(fig)
            pp.close()

        if (saveAsSVG):
            logger.debug("Save plot as SVG...")
            plt.savefig(filename+".svg")

        if (saveAsPNG):
            logger.debug("Save plot as PNG...")
            plt.savefig(filename+".png")
            if (showPNG):
                logger.debug("Show plot...")
                os.startfile(filename+".png")

        plt.close('all')
    else:
        logger.debug("Number of objectives not supported")

# -----------------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------------
def showBestResult(top_pop, generation, Original, filename, title, info, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
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
        UMatrix, PMatrix, UPMatrix = decoder.resolveRoleModelChromosomeIntoIntArrays(ind[0], Original.shape[0], Original.shape[1])

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
                cmap = plt.cm.Blues
                cmap.set_under('white') # Color for values less than vmin
                eps = numpy.spacing(0.0) # Very small float such that 0.0 != 0 + eps
                ax.pcolor(matrix, cmap=cmap, vmin=eps, edgecolors='#FFFFFF', linewidths=0.5)
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
        #info = info.replace("\n","; ")[:275]
        fig.text(0.1,0.01,info, fontsize=10)
        #fig.set_tight_layout(True)
        plt.suptitle("RoleModel for: "+title, fontsize=20)

        if (saveAsPDF):
            logger.debug("Save plot for Top "+str(i)+" as PDF...")
            pp = PdfPages(filename+"_"+str(i)+".pdf")
            pp.savefig(fig)
            pp.close()

        if (saveAsSVG):
            logger.debug("Save plot for Top "+str(i)+" as SVG...")
            plt.savefig(filename+"_"+str(i)+".svg")

        if (saveAsPNG):
            logger.debug("Save plot for Top "+str(i)+" as PNG...")
            plt.savefig(filename+"_"+str(i)+".png")
            if (showPNG):
                logger.debug("Show plot...")
                #plt.show()
                os.startfile(filename+"_"+str(i)+".png")

        i += 1
    plt.close('all')

# -----------------------------------------------------------------------------------------
# Visualize UPMatrix
# -----------------------------------------------------------------------------------------
def visualizeUPMatrix(UPmatrix):
    fig,ax = plt.subplots()

    ax.pcolor(numpy.array(UPmatrix),cmap=plt.cm.Blues,edgecolors='#FFFFFF',linewidths=0.5)
    ax.set_xticks(numpy.arange(UPmatrix.shape[1])+0.5)
    ax.set_yticks(numpy.arange(UPmatrix.shape[0])+0.5)

    ax.xaxis.tick_top()
    ax.yaxis.tick_left()
    ax.set_xlim(0, UPmatrix.shape[1])
    ax.set_ylim(0, UPmatrix.shape[0])
    ax.invert_yaxis()

    ax.set_xticklabels(range(0,UPmatrix.shape[1]),minor=False,rotation='vertical',fontsize=8)
    ax.set_yticklabels(range(0,UPmatrix.shape[0]),minor=False,fontsize=8)
    ax.tick_params(width=0)

    plt.text(0.5,1.08,'User-Permission Matrix',horizontalalignment='center',transform=ax.transAxes)

    plt.ylabel('Users')
    plt.xlabel('Permissions')
    plt.show()

# -----------------------------------------------------------------------------------------
# Visualize the URMatrix, PRMatrix and UPMatrix
# -----------------------------------------------------------------------------------------
def showRoleModel(UMatrix, PMatrix, UPMatrix, UPMatrixWithNoise, filename, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    results = []
    results.append(UMatrix)
    results.append(PMatrix)
    results.append(UPMatrix)
    results.append(UPMatrixWithNoise)

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
    plots[1][1].set_ylabel('User-Permission Matrix With Noise',fontsize=14)
    #fig.tight_layout()
    fig.set_tight_layout(True)

    if (saveAsPDF):
        logger.debug("Save plot as PDF...")
        pp = PdfPages(filename+".pdf")
        pp.savefig(fig)
        pp.close()

    if (saveAsSVG):
        logger.debug("Save plot as SVG...")
        plt.savefig(filename+".svg")

    if (saveAsPNG):
        logger.debug("Save plot as PNG...")
        plt.savefig(filename+".png")
        if (showPNG):
            logger.debug("Show plot...")
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
        matrix = decoder.resolveRoleModelChromosomeIntoIntArray(ind[0], Original.shape[0], Original.shape[1])
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
        matrix = decoder.resolveRoleModelChromosomeIntoIntArray(bestInd[0], Original.shape[0], Original.shape[1])
        results.append([bestFit, matrix, generation])
    results.append([0, Original])
    return results

# -----------------------------------------------------------------------------------------
# Print population as string
# -----------------------------------------------------------------------------------------
def printPopulation(pop):
    i = 1
    for ind in pop:
        logger.debug(str(i) + " -- " + str(ind.fitness.values) + " -- " + str(ind[0]))
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
