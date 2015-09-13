__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# EvoRoleMiner
# -----------------------------------------------------------------------------------

import numpy
import rm_Visualization as visual
import rm_GeneticAlgorithms as ga
import os.path
import tkinter as tk
from tkinter import filedialog
import json
from deap import tools

# ----------------------------------------------------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
useCheckpoint = False
saveInJSONFile = True
saveInCSVFile = True

evolutionAsPDF = True
evolutionAsSVG = True
evolutionAsPNG = True
showEvolutionPNG = False

roleModelsAsPDF = True
roleModelsAsSVG = True
roleModelsAsPNG = True
showRoleModelsPNG = False

logPlotAsPDF = True
logPlotAsSVG = True
logPlotAsPNG = True
showLogPlotPNG = False

saveLogFile = True

# ----------------------------------------------------------------------------------------------------------------------
# SINGLE EXPERIMENT
# ----------------------------------------------------------------------------------------------------------------------
def startExperiment(Name, Original, DATA, POP_SIZE, CXPB,
                    MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6,
                    NGEN, freq, evolutionType, evalFunc):
    global useCheckpoint
    # ------------------------------------------------------------------------------------------------------------------
    # CHECKPOINT INFO
    # ------------------------------------------------------------------------------------------------------------------
    prevFiles = []
    if (useCheckpoint):
        print("Use checkpoint: True")
        root = tk.Tk()
        root.withdraw()
        selected = filedialog.askopenfilename(initialdir = "..\\Output")
        if (selected != ''):
            prevFiles.append(selected)

    # ------------------------------------------------------------------------------------------------------------------
    # FILENAME INFO
    # ------------------------------------------------------------------------------------------------------------------
    directory = "..\\Output\\"+Name
    if not os.path.exists(directory):
        os.makedirs(directory)
    subdirectory = directory+"\\"+DATA+"_"+evolutionType
    if (evolutionType=="Single"):
        subdirectory += "_"+evalFunc
    else:
        evalFunc = ""

    fileExt = "_" + str(POP_SIZE) + "_" + str(NGEN) + "_" + str(CXPB) + "_" + str(MUTPB_All)
    pickleFile = "Checkpoint"+fileExt+".pkl"

    # ------------------------------------------------------------------------------------------------------------------
    # EVOLUTION
    # ------------------------------------------------------------------------------------------------------------------
    logbook = tools.Logbook()
    if (evolutionType=="Single"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ga.evolution(Original, evalFunc, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5,
                         MUTPB_6, NGEN, freq, useCheckpoint, prevFiles, subdirectory, pickleFile)
    elif (evolutionType=="Multi"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ga.evolution_multi(Original, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5,
                               MUTPB_6, NGEN, freq, useCheckpoint, prevFiles, subdirectory, pickleFile)
    elif (evolutionType=="Multi_Fortin2013"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ga.evolution_multi_fortin2013(Original, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4,
                                          MUTPB_5, MUTPB_6, NGEN, freq, useCheckpoint, prevFiles, subdirectory, pickleFile)
    else:
        raise ValueError('Evolution type not known')

    # ------------------------------------------------------------------------------------------------------------------
    # POST PROCESSSING
    # ------------------------------------------------------------------------------------------------------------------
    timeSum = sum(timeArray)
    time = timeArray.pop()
    print("Total in seconds: "+str(timeSum))
    minutes = int(timeSum/60)
    if (minutes > 0):
        print("Minutes: "+str(minutes))
        print("Seconds: "+str(timeSum-(minutes*60)))

    prevFile = ""
    if (len(prevFiles)!=0):
        prevFile = str(prevFiles.pop()[60:])
    elif (useCheckpoint):
        useCheckpoint = False

    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)

    if not os.path.exists(subdirectory+ "\\Evolution"):
        os.makedirs(subdirectory+ "\\Evolution")
    evolution_filename = subdirectory + "\\Evolution\\Evolution"+fileExt
    if not os.path.exists(subdirectory+ "\\RoleModel"):
        os.makedirs(subdirectory+ "\\RoleModel")
    roleModel_filename = subdirectory + "\\RoleModel\\RoleModel"+fileExt
    userCount = Original.shape[0]
    permissionCount = Original.shape[1]
    info = "Data: "+DATA+"; userCount: "+str(userCount)+"; permissionCount: "+str(permissionCount)\
           +"\nEvoType: "+evolutionType+"; evalFunc: "+evalFunc\
           +"\nGenerations: "+str(generation)+"; Population: "+str(POP_SIZE)+"; CXPB: "+str(CXPB)\
           +"; MUTPB: "+str(MUTPB_All)\
           +"\nFrequency: "+str(freq)\
           +"\nPrevious Checkpoint: "+prevFile

    # ------------------------------------------------------------------------------------------------------------------
    # SAVE LOGBOOK IN FILE
    # ------------------------------------------------------------------------------------------------------------------
    if not os.path.exists(subdirectory+"\\Logbook"):
        os.makedirs(subdirectory+ "\\Logbook")
    log_filename = subdirectory + "\\Logbook\\Logbook"+fileExt
    class NumPyArangeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, numpy.ndarray):
                return obj.tolist() # or map(int, obj)
            return json.JSONEncoder.default(self, obj)
    if (saveLogFile):
        logfile = log_filename+".log"
        print("Save logfile into "+str(logfile)+"...")
        temp = logbook
        with open(logfile, "a") as outfile:
            if (evolutionType=="Multi" or evolutionType=="Multi_Fortin2013"):
                for i in range(0,len(logbook)):
                    temp = logbook[i]
                    temp['fitnessObj1'] = logbook.chapters["fitnessObj1"][i]
                    temp['fitnessObj2'] = logbook.chapters["fitnessObj2"][i]
            json.dump(temp, outfile, indent=4, cls=NumPyArangeEncoder)
            outfile.close()
        print("DONE.\n")

    # ------------------------------------------------------------------------------------------------------------------
    # VISUALIZE RESULTS
    # ------------------------------------------------------------------------------------------------------------------
    if (evolutionType=="Single"):
        visual.plotLogbook(logbook, log_filename+"_plot", logPlotAsPDF, logPlotAsSVG, logPlotAsPNG, showLogPlotPNG)
        visual.showFitnessInPlot(results, generation, freq, evolution_filename, info, evolutionAsPDF, evolutionAsSVG,
                                 evolutionAsPNG, showEvolutionPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename, roleModelsAsPDF, roleModelsAsSVG,
                              roleModelsAsPNG, showRoleModelsPNG)
    elif (evolutionType=="Multi"):
        visual.plotLogbookForMultiObjective(logbook, log_filename+"_plot", logPlotAsPDF, logPlotAsSVG, logPlotAsPNG,
                                            showLogPlotPNG)
        visual.showFitnessInPlotForMultiObjective(results, generation, freq, evolution_filename, info, evolutionAsPDF,
                                                  evolutionAsSVG, evolutionAsPNG, showEvolutionPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename, roleModelsAsPDF, roleModelsAsSVG,
                              roleModelsAsPNG, showRoleModelsPNG)
    elif (evolutionType=="Multi_Fortin2013"):
        visual.plotLogbookForMultiObjective(logbook, log_filename+"_plot", logPlotAsPDF, logPlotAsSVG, logPlotAsPNG,
                                            showLogPlotPNG)
        visual.showFitnessInPlotForMultiObjective(results, generation, freq, evolution_filename, info, evolutionAsPDF,
                                                  evolutionAsSVG, evolutionAsPNG, showEvolutionPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename, roleModelsAsPDF, roleModelsAsSVG,
                              roleModelsAsPNG, showRoleModelsPNG)
    else:
        raise ValueError('Evolution type not known')

    #visual.printPopulation(population)

    # ------------------------------------------------------------------------------------------------------------------
    # SAVE RESULTS in FILES
    # ------------------------------------------------------------------------------------------------------------------
    if (saveInJSONFile):
        resultJSONfile = directory+"\\Results.json"
        print("Write into JSON file "+str(resultJSONfile)+"...")
        with open(resultJSONfile, "a") as outfile:
            json.dump({'Experiment':Name, 'userCount':str(userCount), 'permissionCount':str(permissionCount),
                       'EvoType':evolutionType,'evalFunc':evalFunc,
                       'POP_SIZE':str(len(population)), 'NGEN':str(generation),'CXPB':str(CXPB),'MUTPB':str(MUTPB_All),
                       'Frequency':str(freq),'Runtime':str(time), 'Runtime_Sum':str(timeSum),
                       'Continued':str(useCheckpoint),'PreviousCheckpoint':prevFile,
                       'ResultFiles':str(subdirectory[10:])}, outfile, indent=4)
            outfile.close()
        print("DONE.\n")

    if (saveInCSVFile):
        resultCSVfile = directory+"\\Results.csv"
        print("Write into CSV file "+str(resultCSVfile)+"...")
        if not os.path.exists(resultCSVfile):
            with open(resultCSVfile, "a") as outfile:
                outfile.write("sep=;\n")
                outfile.write("Experiment;userCount;permissionCount;EvoType;EvalFunc;POP_SIZE;NGEN;CXPB;MUTPB;"
                              "Frequency;Runtime;Runtime_Sum;Continued;prevFile;Result_files\n")
                outfile.close()
        with open(resultCSVfile, "a") as outfile:
            outfile.write(Name+";"+str(userCount)+";"+str(permissionCount)+";"+evolutionType+";"+evalFunc+";"+str(len(population))
                          +";"+str(generation)+";"+str(CXPB)+";"+str(MUTPB_All)+";"+str(freq)+";"+str(time)+";"
                          +str(timeSum)+";"+str(useCheckpoint)+";"+prevFile+";"+subdirectory[10:]+"\n")
            outfile.close()
        print("DONE.\n")
