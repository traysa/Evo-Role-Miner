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
import configparser

# ----------------------------------------------------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
useCheckpoint = False
saveInJSONFile = True
saveInCSVFile = True

fitnessAsPDF = False
fitnessAsSVG = False
fitnessAsPNG = True
showFitnessPNG = False

numberTopRoleModels = 5
roleModelsAsPDF = False
roleModelsAsSVG = False
roleModelsAsPNG = True
showRoleModelsPNG = False

logPlotAsPDF = False
logPlotAsSVG = False
logPlotAsPNG = True
showLogPlotPNG = False

saveLogFile = True

config = configparser.ConfigParser()
config.read('EvoRoleMiner_config.ini')
if (len(config.sections()) == 0):
    print("Create new config file...")
    config['Checkpoint'] = {'use_Checkpoint': useCheckpoint}
    config['Results'] = {'save_In_JSON_File': saveInJSONFile,'save_In_CSV_File': saveInCSVFile}
    config['Fitness Plot'] = {'fitness_As_PDF': fitnessAsPDF,'fitness_As_SVG': fitnessAsSVG,
                              'fitness_As_PNG': fitnessAsPNG,'show_Fitness_PNG': showFitnessPNG}
    config['Best Phenotypes'] = {'role_Models_As_PDF': roleModelsAsPDF,'role_Models_As_SVG': roleModelsAsSVG,
                                 'role_Models_As_PNG': roleModelsAsPNG,'show_Role_Models_PNG': showRoleModelsPNG,
                                 'number_Top_Role_Models': numberTopRoleModels}
    config['Log Plot'] = {'log_Plot_As_PDF': logPlotAsPDF,'log_Plot_As_SVG': logPlotAsSVG,
                          'log_Plot_As_PNG': logPlotAsPNG,'show_Log_Plot_PNG': showLogPlotPNG}
    config['Log File'] = {'save_Log_File': saveLogFile}
    with open('EvoRoleMiner_config.ini', 'w') as configfile:
        config.write(configfile)
else:
    useCheckpoint = config['Checkpoint'].getboolean('use_Checkpoint')
    saveInJSONFile = config['Results'].getboolean('save_In_JSON_File')
    saveInCSVFile = config['Results'].getboolean('save_In_CSV_File')
    fitnessAsPDF = config['Fitness Plot'].getboolean('fitness_As_PDF')
    fitnessAsSVG = config['Fitness Plot'].getboolean('fitness_As_SVG')
    fitnessAsPNG = config['Fitness Plot'].getboolean('fitness_As_PNG')
    showFitnessPNG = config['Fitness Plot'].getboolean('show_Fitness_PNG')
    numberTopRoleModels = config['Best Phenotypes'].getint('number_Top_Role_Models')
    roleModelsAsPDF = config['Best Phenotypes'].getboolean('role_Models_As_PDF')
    roleModelsAsSVG = config['Best Phenotypes'].getboolean('role_Models_As_SVG')
    roleModelsAsPNG = config['Best Phenotypes'].getboolean('role_Models_As_PNG')
    showRoleModelsPNG = config['Best Phenotypes'].getboolean('show_Role_Models_PNG')
    logPlotAsPDF = config['Log Plot'].getboolean('log_Plot_As_PDF')
    logPlotAsSVG = config['Log Plot'].getboolean('log_Plot_As_SVG')
    logPlotAsPNG = config['Log Plot'].getboolean('log_Plot_As_PNG')
    showLogPlotPNG = config['Log Plot'].getboolean('show_Log_Plot_PNG')
    saveLogFile = config['Log File'].getboolean('save_Log_File')
    if (useCheckpoint == None or saveInJSONFile == None or saveInCSVFile == None or fitnessAsPDF == None
        or fitnessAsSVG == None or fitnessAsPNG == None or showFitnessPNG == None or numberTopRoleModels == None
        or roleModelsAsPDF == None or roleModelsAsSVG == None or roleModelsAsPNG == None or showRoleModelsPNG == None
        or logPlotAsPDF == None or logPlotAsSVG == None or logPlotAsPNG == None or showLogPlotPNG == None
        or saveLogFile == None):
        raise ValueError("Config file 'EvoRoleMiner_config.ini' is corrupt. Create new one by deleting the old one.")

# ----------------------------------------------------------------------------------------------------------------------
# SINGLE EXPERIMENT
# ----------------------------------------------------------------------------------------------------------------------
def startExperiment(directory, Name, experimentNumber, experimentCnt, Original, DATA, POP_SIZE, CXPB,
                    MUTPB_All, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB,
                    NGEN, freq, evolutionType, evalFunc, untilSolutionFound, obj_weights=[],eval_weights=[]):
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
    directory = directory+"\\"+Name
    if not os.path.exists(directory):
        os.makedirs(directory)
    subdirectory = directory#+"\\"+DATA+"_"+evolutionType
    #if (evolutionType=="Single"):
    #    subdirectory += "_"+evalFunc

    fileExt = "_" + evolutionType + "_" + str(evalFunc) + "_" + str(POP_SIZE) + "_" + str(NGEN) + "_" + str(CXPB) + "_" + str(MUTPB_All)
    if (evolutionType=="Multi_Weighted" or evolutionType=="Multi_Fortin2013_Weighted" ):
        fileExt += "_" + str(obj_weights)
    checkpointSubdirectory = subdirectory+"\\Checkpoints"
    if not os.path.exists(checkpointSubdirectory):
        os.makedirs(checkpointSubdirectory)
    pickleFile = checkpointSubdirectory+"\\"+str(experimentNumber)+"_"+str(experimentCnt)+"_Checkpoint"+fileExt+".pkl"

    # ------------------------------------------------------------------------------------------------------------------
    # EVOLUTION
    # ------------------------------------------------------------------------------------------------------------------
    logbook = tools.Logbook()
    if (evolutionType=="Single"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ea_single.evolution(Original, evalFunc[0], POP_SIZE, CXPB, MUTPB_All, addRolePB, removeRolePB, removeUserPB,
                                removePermissionPB, addUserPB, addPermissionPB, NGEN, freq, numberTopRoleModels,
                                untilSolutionFound=untilSolutionFound, eval_weights=eval_weights)
    elif (evolutionType=="Multi" or evolutionType=="Multi_Fortin2013"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ea_multi.evolution_multi(Original, evalFunc, POP_SIZE, CXPB, addRolePB, removeRolePB,
                                     removeUserPB, removePermissionPB, addUserPB, addPermissionPB, NGEN, freq,
                                     numberTopRoleModels,fortin=(evolutionType=="Multi_Fortin2013"))
    elif (evolutionType=="Multi_Weighted" or evolutionType=="Multi_Fortin2013_Weighted"):
        population, results, generation, timeArray, prevFiles, top_pop, logbook, fileExt = \
            ea_multi_w.evolution_multi_weighted(Original, evalFunc, POP_SIZE, obj_weights, CXPB,
                                                addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB,
                                                addPermissionPB, NGEN, freq, numberTopRoleModels,
                                                fortin=(evolutionType=="Multi_Fortin2013_Weighted"))
    else:
        raise ValueError('Evolution type not known')

    # ------------------------------------------------------------------------------------------------------------------
    # POST PROCESSSING
    # ------------------------------------------------------------------------------------------------------------------
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
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

    fitnessResultsSubdirectory = subdirectory+ "\\FitnessResults"
    if not os.path.exists(fitnessResultsSubdirectory):
        os.makedirs(fitnessResultsSubdirectory)
    fitness_filename = fitnessResultsSubdirectory+"\\"+str(experimentNumber)+"_"+str(experimentCnt)+"_Fitness"+fileExt

    roleModelsSubdirectory = subdirectory+ "\\RoleModels"
    if not os.path.exists(roleModelsSubdirectory):
        os.makedirs(roleModelsSubdirectory)
    roleModelsSubsubdirectory = roleModelsSubdirectory+"\\"+str(experimentNumber)+"_RM"+fileExt
    if not os.path.exists(roleModelsSubsubdirectory):
        os.makedirs(roleModelsSubsubdirectory)
    roleModelsSubsubsubdirectory = roleModelsSubsubdirectory+"\\"+str(experimentNumber)+"_"+str(experimentCnt)+"_RM"+fileExt
    if not os.path.exists(roleModelsSubsubsubdirectory):
        os.makedirs(roleModelsSubsubsubdirectory)
    roleModel_filename = roleModelsSubsubsubdirectory+"\\RoleModel"

    # ------------------------------------------------------------------------------------------------------------------
    # SAVE LOGBOOK IN FILE
    # ------------------------------------------------------------------------------------------------------------------
    resultInfo = ""
    Fitness_Min = 0
    Fitness_Max = 0
    Fitness_Avg = 0
    Conf_Min = 0
    Conf_Max = 0
    Conf_Avg = 0
    Accs_Min = 0
    Accs_Max = 0
    Accs_Avg = 0
    RoleCnt_Min = 0
    RoleCnt_Max = 0
    RoleCnt_Avg = 0
    logbooksSubdirectory = subdirectory+"\\Logbooks"
    if not os.path.exists(logbooksSubdirectory):
        os.makedirs(logbooksSubdirectory)
    logbooksSubsubdirectory = logbooksSubdirectory+"\\"+str(experimentNumber)+"_Log"+fileExt
    if not os.path.exists(logbooksSubsubdirectory):
        os.makedirs(logbooksSubsubdirectory)
    log_filename = logbooksSubsubdirectory+"\\"+str(experimentNumber)+"_"+str(experimentCnt)+"_Log"+fileExt
    class NumPyArangeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, numpy.ndarray):
                return obj.tolist() # or map(int, obj)
            return json.JSONEncoder.default(self, obj)
    if (saveLogFile):
        logfile = log_filename+".json"
        print("Save logfile into "+str(logfile)+"...")
        temp = logbook
        if (evolutionType.startswith("Multi")):
            for i in range(0,len(logbook)):
                temp = logbook[i]
                for o,obj in enumerate(evalFunc):
                    temp['fitness_'+obj] = logbook.chapters["fitnessObj"+str(o+1)][i]
        else:
            for i in range(0,len(logbook)):
                temp = logbook[i]
                temp['Fitness'] = logbook.chapters["Fitness"][i]
                temp['Conf'] = logbook.chapters["Conf"][i]
                temp['Accs'] = logbook.chapters["Accs"][i]
                temp['RoleCnt'] = logbook.chapters["RoleCnt"][i]
        with open(logfile, "a") as outfile:
            json.dump(temp, outfile, indent=4, cls=NumPyArangeEncoder)
            outfile.close()
        print("DONE.\n")

        logfile = log_filename+".csv"
        print("Save logfile into "+str(logfile)+"...")
        if (evolutionType.startswith("Multi")):
            with open(logfile, "a") as outfile:
                outfile.write("sep=;\n")
                headers = "gen;evals;"
                for obj in evalFunc:
                    headers += obj+"_Min;"+obj+"_Max;"+obj+"_Avg;"+obj+"_Std;"
                outfile.write(headers+"\n")
                for i in range(0,len(logbook)):
                    gen = logbook.select("gen")[i]
                    evals = logbook.select("evals")[i]
                    entry = str(gen)+";"+str(evals)
                    for o in range(1,len(evalFunc)+1):
                        min = logbook.chapters["fitnessObj"+str(o)].select("min")[i]
                        max = logbook.chapters["fitnessObj"+str(o)].select("max")[i]
                        avg = logbook.chapters["fitnessObj"+str(o)].select("avg")[i]
                        std = logbook.chapters["fitnessObj"+str(o)].select("std")[i]
                        entry+= ";"+str(min)+";"+str(max)+";"+str(avg)+";"+str(std)
                    outfile.write(entry+"\n")
                outfile.close()
        else:
            with open(logfile, "a") as outfile:
                outfile.write("sep=;\n")
                outfile.write("gen;evals;Fitness_Min;Fitness_Max;Fitness_Avg;Fitness_Std"\
                              ";Conf_Min;Conf_Max;Conf_Avg;Conf_Std"\
                              ";Accs_Min;Accs_Max;Accs_Avg;Accs_Std;RoleCnt_Min;RoleCnt_Max;RoleCnt_Avg;RoleCnt_Std"\
                              "\n")
                for i in range(0,len(logbook)):
                    gen = logbook.select("gen")[i]
                    evals = logbook.select("evals")[i]
                    Fitness_Min = logbook.chapters["Fitness"].select("min")[i]
                    Fitness_Max = logbook.chapters["Fitness"].select("max")[i]
                    Fitness_Avg = logbook.chapters["Fitness"].select("avg")[i]
                    Fitness_Std = logbook.chapters["Fitness"].select("std")[i]
                    Conf_Min = logbook.chapters["Conf"].select("min")[i]
                    Conf_Max = logbook.chapters["Conf"].select("max")[i]
                    Conf_Avg = logbook.chapters["Conf"].select("avg")[i]
                    Conf_Std = logbook.chapters["Conf"].select("std")[i]
                    Accs_Min = logbook.chapters["Accs"].select("min")[i]
                    Accs_Max = logbook.chapters["Accs"].select("max")[i]
                    Accs_Avg = logbook.chapters["Accs"].select("avg")[i]
                    Accs_Std = logbook.chapters["Accs"].select("std")[i]
                    RoleCnt_Min = logbook.chapters["RoleCnt"].select("min")[i]
                    RoleCnt_Max = logbook.chapters["RoleCnt"].select("max")[i]
                    RoleCnt_Avg = logbook.chapters["RoleCnt"].select("avg")[i]
                    RoleCnt_Std = logbook.chapters["RoleCnt"].select("std")[i]
                    outfile.write(str(gen)+";"+str(evals)
                                  +";"+str(Fitness_Min)+";"+str(Fitness_Max)+";"+str(Fitness_Avg)+";"+str(Fitness_Std)
                                  +";"+str(Conf_Min)+";"+str(Conf_Max)+";"+str(Conf_Avg)+";"+str(Conf_Std)
                                  +";"+str(Accs_Min)+";"+str(Accs_Max)+";"+str(Accs_Avg)+";"+str(Accs_Std)
                                  +";"+str(RoleCnt_Min)+";"+str(RoleCnt_Max)+";"+str(RoleCnt_Avg)+";"+str(RoleCnt_Std)
                                  +"\n")
                resultInfo = "Conf("+str(Conf_Min)+","+str(Conf_Avg)+","+str(Conf_Max)\
                             +"),Accs("+str(Accs_Min)+","+str(Accs_Avg)+","+str(Accs_Max)\
                             +"),RoleCnt("+str(RoleCnt_Min)+","+str(RoleCnt_Avg)+","+str(RoleCnt_Max)+")"
                outfile.close()


    # ------------------------------------------------------------------------------------------------------------------
    # VISUALIZE RESULTS
    # ------------------------------------------------------------------------------------------------------------------
    userCount = Original.shape[0]
    permissionCount = Original.shape[1]
    info = "Data: "+DATA+"; userCount: "+str(userCount)+"; permissionCount: "+str(permissionCount)\
           +"\nEvoType: "+evolutionType+"; evalFunc: "+str(evalFunc)+"; Generations: "+str(generation)+"; Population: "\
           +str(POP_SIZE)+"; Frequency: "+str(freq)\
           +"\nCXPB: "+str(CXPB)+"; MUTPB_All: "+str(MUTPB_All)+" ("+str(addRolePB)+";"+str(removeRolePB)+";"\
           +str(removeUserPB)+";"+str(removePermissionPB)+";"+str(addUserPB)+";"+str(addPermissionPB)+")"\
           +"\nRESULTS: "+resultInfo
           #+"\nPrevious Checkpoint: "+prevFile
    if(evolutionType=="Single" and (evalFunc[0].startswith("Saenko") or evalFunc[0].startswith("WSC"))):
        index = info.find(')\n')
        info = info[:index+1] + "; eval_weights=" + str(eval_weights)+ info[index+1:]
    if(evolutionType=="Multi_Weighted" or evolutionType=="Multi_Fortin2013_Weighted"):
        index = info.find(')\n')
        info = info[:index+1] + "; obj_weights=" + str(obj_weights)+ info[index+1:]
        fitness_filename += "_" + str(obj_weights)

    if (evolutionType=="Single"):
        stats = ["Fitness","RoleCnt","Conf","Accs"]
        visual.plotLogbook(logbook, log_filename+"_plot", stats, fileExt[1:], info, logPlotAsPDF, logPlotAsSVG, logPlotAsPNG, showLogPlotPNG)
        visual.showFitnessInPlot(results, generation, freq, fitness_filename, fileExt[1:], info, evalFunc[0], fitnessAsPDF, fitnessAsSVG,
                                 fitnessAsPNG, showFitnessPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename, fileExt[1:], info, roleModelsAsPDF, roleModelsAsSVG,
                              roleModelsAsPNG, showRoleModelsPNG)
    elif (evolutionType=="Multi" or evolutionType=="Multi_Fortin2013"):
        visual.plotLogbookForMultiObjective(logbook, log_filename+"_plot", fileExt[1:], info, evalFunc, logPlotAsPDF, logPlotAsSVG, logPlotAsPNG,
                                            showLogPlotPNG)
        visual.showFitnessInPlotForMultiObjective(results, generation, freq, fitness_filename, fileExt[1:], info, evalFunc, fitnessAsPDF,
                                                  fitnessAsSVG, fitnessAsPNG, showFitnessPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename, fileExt[1:], info, roleModelsAsPDF, roleModelsAsSVG,
                              roleModelsAsPNG, showRoleModelsPNG)
    elif (evolutionType=="Multi_Weighted" or evolutionType=="Multi_Fortin2013_Weighted"):
        visual.plotLogbookForMultiObjective(logbook, log_filename+"_plot", fileExt[1:], info, evalFunc, logPlotAsPDF, logPlotAsSVG, logPlotAsPNG,
                                            showLogPlotPNG)
        visual.showFitnessInPlotForMultiObjective(results, generation, freq, fitness_filename, fileExt[1:], info, evalFunc, fitnessAsPDF,
                                                  fitnessAsSVG, fitnessAsPNG, showFitnessPNG)
        visual.showBestResult(top_pop,generation,Original, roleModel_filename, fileExt[1:], info, roleModelsAsPDF, roleModelsAsSVG,
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
            json.dump({'ExperimentNumber':str(experimentNumber), 'ExperimentCount':str(experimentCnt), 'Experiment':Name,
                       'userCount':str(userCount), 'permissionCount':str(permissionCount),
                       'EvoType':evolutionType,'evalFunc':evalFunc,
                       'POP_SIZE':str(len(population)), 'NGEN':str(generation),'obj_weights':str(obj_weights),'eval_weights':str(eval_weights),'CXPB':str(CXPB),'MUTPB':str(MUTPB_All),
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
                outfile.write("ExperimentNumber;ExperimentCount;Experiment;userCount;permissionCount;EvoType;EvalFunc;POP_SIZE;NGEN;obj_weights;eval_weights;CXPB;MUTPB;"
                              "Frequency;Runtime;Runtime_Sum;Continued;prevFile;Result_files\n")
                outfile.close()
        with open(resultCSVfile, "a") as outfile:
            outfile.write(str(experimentNumber)+";"+str(experimentCnt)+";"+Name+";"+str(userCount)+";"+str(permissionCount)+";"
                          +evolutionType+";"+str(evalFunc)+";"+str(len(population))+";"+str(generation)+";"+str(obj_weights)+";"
                          +str(eval_weights)+";"+str(CXPB)+";"+str(MUTPB_All)+";"+str(freq)+";"+str(time)+";"
                          +str(timeSum)+";"+str(useCheckpoint)+";"+prevFile+";"+subdirectory[10:]+"\n")
            outfile.close()
        print("DONE.\n")
