__author__ = 'Theresa'

# -----------------------------------------------------------------------------------
# EvoRoleMiner
# -----------------------------------------------------------------------------------

import numpy
import rm_Visualization as visual
import rm_EvoAlg_SingleObj as ea_single
import rm_EvoAlg_MultiObj as ea_multi
import rm_EvoAlg_MultiObj_weighted as ea_multi_w
import os.path
import tkinter as tk
from tkinter import filedialog
import json
from deap import tools
import datetime

# ----------------------------------------------------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
useCheckpoint = False
saveInJSONFile = True
saveInCSVFile = True

evolutionAsPDF = False
evolutionAsSVG = False
evolutionAsPNG = True
showEvolutionPNG = True

roleModelsAsPDF = False
roleModelsAsSVG = False
roleModelsAsPNG = True
showRoleModelsPNG = True

logPlotAsPDF = False
logPlotAsSVG = False
logPlotAsPNG = True
showLogPlotPNG = False

saveLogFile = True

# ----------------------------------------------------------------------------------------------------------------------
# SINGLE EXPERIMENT
# ----------------------------------------------------------------------------------------------------------------------
def startExperiment(Name, Original, DATA, POP_SIZE, CXPB,
                    MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6,
                    NGEN, freq, evolutionType, evalFunc, OBJ1PB=1.0, OBJ2PB=1.0):
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

    fileExt = "_" + str(POP_SIZE) + "_" + str(NGEN) + "_" + str(CXPB) + "_" + str(MUTPB_All)
    if (evolutionType=="Multi_Weighted"):
        fileExt += "_" + str(OBJ1PB)+ "_" + str(OBJ2PB)
    pickleFile = directory+"\\Checkpoint"+fileExt+".pkl"

    # ------------------------------------------------------------------------------------------------------------------
    # EVOLUTION
    # ------------------------------------------------------------------------------------------------------------------
    logbook = tools.Logbook()
    if (evolutionType=="Single"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ea_single.evolution(Original, evalFunc, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5,
                         MUTPB_6, NGEN, freq, useCheckpoint, prevFiles, subdirectory, pickleFile)
    elif (evolutionType=="Multi" or evolutionType=="Multi_Fortin2013"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ea_multi.evolution_multi(Original, evalFunc, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4,
                                          MUTPB_5, MUTPB_6, NGEN, freq, useCheckpoint, prevFiles, subdirectory, pickleFile, (evolutionType=="Multi_Fortin2013"))
    elif (evolutionType=="Multi_Weighted" or evolutionType=="Multi_Fortin2013_Weighted"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ea_multi_w.evolution_multi_weighted(Original, evalFunc, POP_SIZE, OBJ1PB, OBJ2PB, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4,
                                          MUTPB_5, MUTPB_6, NGEN, freq, useCheckpoint, prevFiles, subdirectory, pickleFile, (evolutionType=="Multi_Fortin2013_Weighted"))
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
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    if not os.path.exists(subdirectory+"\\Logbook"):
        os.makedirs(subdirectory+ "\\Logbook")
    log_filename = subdirectory + "\\Logbook\\Logbook"+fileExt+"_"+timestamp
    class NumPyArangeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, numpy.ndarray):
                return obj.tolist() # or map(int, obj)
            return json.JSONEncoder.default(self, obj)
    if (saveLogFile):
        logfile = log_filename+".json"
        print("Save logfile into "+str(logfile)+"...")
        temp = logbook
        with open(logfile, "a") as outfile:
            if (evolutionType.startswith("Multi")):
                for i in range(0,len(logbook)):
                    temp = logbook[i]
                    temp['fitnessObj1'] = logbook.chapters["fitnessObj1"][i]
                    temp['fitnessObj2'] = logbook.chapters["fitnessObj2"][i]
            json.dump(temp, outfile, indent=4, cls=NumPyArangeEncoder)
            outfile.close()
        print("DONE.\n")
        logfile = log_filename+".csv"
        print("Save logfile into "+str(logfile)+"...")
        if (evolutionType.startswith("Multi")):
            with open(logfile, "a") as outfile:
                outfile.write("sep=;\n")
                outfile.write("gen;evals;Obj1_Min;Obj1_Max;Obj1_Avg;Obj1_Std;Obj2_Min;Obj2_Max;Obj2_Avg;Obj2_Std\n")
                for i in range(0,len(logbook)):
                    gen = logbook.select("gen")[i]
                    evals = logbook.select("evals")[i]
                    min = logbook.chapters["fitnessObj1"].select("min")[i]
                    max = logbook.chapters["fitnessObj1"].select("max")[i]
                    avg = logbook.chapters["fitnessObj1"].select("avg")[i]
                    std = logbook.chapters["fitnessObj1"].select("std")[i]
                    min2 = logbook.chapters["fitnessObj2"].select("min")[i]
                    max2 = logbook.chapters["fitnessObj2"].select("max")[i]
                    avg2 = logbook.chapters["fitnessObj2"].select("avg")[i]
                    std2 = logbook.chapters["fitnessObj2"].select("std")[i]
                    outfile.write(str(gen)+";"+str(evals)
                                  +";"+str(min)+";"+str(max)+";"+str(avg)+";"+str(std)
                                  +";"+str(min2)+";"+str(max2)+";"+str(avg2)+";"+str(std2)+"\n")
                outfile.close()
        else:
            with open(logfile, "a") as outfile:
                outfile.write("sep=;\n")
                outfile.write("gen;evals;Obj1_Min;Obj1_Max;Obj1_Avg;Obj1_Std\n")
                for i in range(0,len(logbook)):
                    gen = logbook.select("gen")[i]
                    evals = logbook.select("evals")[i]
                    min = logbook.select("min")[i]
                    max = logbook.select("max")[i]
                    avg = logbook.select("avg")[i]
                    std = logbook.select("std")[i]
                    outfile.write(str(gen)+";"+str(evals)
                                  +";"+str(min)+";"+str(max)+";"+str(avg)+";"+str(std)+"\n")
                outfile.close()


    # ------------------------------------------------------------------------------------------------------------------
    # VISUALIZE RESULTS
    # ------------------------------------------------------------------------------------------------------------------
    if (evolutionType=="Single"):
        visual.plotLogbook(logbook, log_filename+"_plot_"+timestamp, logPlotAsPDF, logPlotAsSVG, logPlotAsPNG, showLogPlotPNG)
        visual.showFitnessInPlot(results, generation, freq, evolution_filename+"_"+timestamp, info, evolutionAsPDF, evolutionAsSVG,
                                 evolutionAsPNG, showEvolutionPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename+"_"+timestamp, roleModelsAsPDF, roleModelsAsSVG,
                              roleModelsAsPNG, showRoleModelsPNG)
    elif (evolutionType=="Multi" or evolutionType=="Multi_Fortin2013"):
        visual.plotLogbookForMultiObjective(logbook, log_filename+"_plot_"+timestamp, logPlotAsPDF, logPlotAsSVG, logPlotAsPNG,
                                            showLogPlotPNG)
        visual.showFitnessInPlotForMultiObjective(results, generation, freq, evolution_filename+"_"+timestamp, info, evolutionAsPDF,
                                                  evolutionAsSVG, evolutionAsPNG, showEvolutionPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename+"_"+timestamp, roleModelsAsPDF, roleModelsAsSVG,
                              roleModelsAsPNG, showRoleModelsPNG)
    elif (evolutionType=="Multi_Weighted" or evolutionType=="Multi_Fortin2013_Weighted"):
        visual.plotLogbookForMultiObjective(logbook, log_filename+"_plot_"+timestamp, logPlotAsPDF, logPlotAsSVG, logPlotAsPNG,
                                            showLogPlotPNG)
        index = info.find('\nFrequency')
        info = info[:index] + "; OBJ1PB=" + str(OBJ1PB)+ "; OBJ2PB=" + str(OBJ2PB) + info[index:]
        evolution_filename += "_" + str(OBJ1PB)+ "_" + str(OBJ2PB)
        visual.showFitnessInPlotForMultiObjective(results, generation, freq, evolution_filename+"_"+timestamp, info, evolutionAsPDF,
                                                  evolutionAsSVG, evolutionAsPNG, showEvolutionPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename+"_"+timestamp, roleModelsAsPDF, roleModelsAsSVG,
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
                       'POP_SIZE':str(len(population)), 'NGEN':str(generation),'OBJ1PB':str(OBJ1PB),'OBJ2PB':str(OBJ2PB),'CXPB':str(CXPB),'MUTPB':str(MUTPB_All),
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
                outfile.write("Experiment;userCount;permissionCount;EvoType;EvalFunc;POP_SIZE;NGEN;OBJ1PB;OBJ2PBCXPB;MUTPB;"
                              "Frequency;Runtime;Runtime_Sum;Continued;prevFile;Result_files\n")
                outfile.close()
        with open(resultCSVfile, "a") as outfile:
            outfile.write(Name+";"+str(userCount)+";"+str(permissionCount)+";"+evolutionType+";"+evalFunc+";"+str(len(population))
                          +";"+str(generation)+";"+str(OBJ1PB)+";"+str(OBJ2PB)+";"+str(CXPB)+";"+str(MUTPB_All)+";"+str(freq)+";"+str(time)+";"
                          +str(timeSum)+";"+str(useCheckpoint)+";"+prevFile+";"+subdirectory[10:]+"\n")
            outfile.close()
        print("DONE.\n")
