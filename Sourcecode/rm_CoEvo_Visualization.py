__author__ = 'Theresa Brandt von Fackh'

# -----------------------------------------------------------------------------------
# Visualizations for Role Miner
# -----------------------------------------------------------------------------------
import matplotlib
matplotlib.use('Agg')
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import rm_CoEvo_EADecoder as decoder
import rm_Visualization as base
import os

# -----------------------------------------------------------------------------------------
# Visualize evaluation values of population in a plot over generations (Single Objective)
# -----------------------------------------------------------------------------------------
def showFitnessInPlot(results, generations, freq, filename, title, info, evalFunc, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    base.showFitnessInPlot(results, generations, freq, filename, title, info, evalFunc, saveAsPDF, saveAsSVG, saveAsPNG, showPNG)

# -----------------------------------------------------------------------------------------
# For SANE: Combines a selection of roles to a rolemodel
# -----------------------------------------------------------------------------------------
def showAllRoles(top_pop, generation, Original, evolution_filename, saveAsPDF, saveAsSVG, saveAsPNG, showPNG):
    i = len(top_pop)
    results = []

    UMatrix, PMatrix, UPMatrix = decoder.resolveRoleChromosomesIntoIntArrays(top_pop, Original.shape[0], Original.shape[1])
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

