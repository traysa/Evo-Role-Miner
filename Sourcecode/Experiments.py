__author__ = 'Theresa'

import logging

import rm_EvoRoleMinerBuilder as rm_builder
import numpy
import MatrixOperators as matrixOps
import rm_FileParser as parser
import rm_EvoAlg_SANE as sane
import datetime
import json
import tkinter as tk
from tkinter import filedialog
import configparser
import ntpath
import os
import shutil
import Experiments_Evaluator as exp_eval
import rm_Utils as utils
import logging
import rm_EAEvaluations as eval

# ----------------------------------------------------------------------------------------------------------------------
# DATA SETS
# ----------------------------------------------------------------------------------------------------------------------
def getDataSet(DATA):
    Original = []
    userAttributes = []
    userAttributeValues = []
    constraints = []
    if (DATA=="healthcare"):
        Original = numpy.matrix(parser.read("..\\TestData\\healthcare.rbac"))
        userAttributeValues = parser.readUserAttributes2("..\\TestData\\healthcare_5_cust.attr",Original.shape[0])
    elif (DATA=="domino"):
        Original = numpy.matrix(parser.read("..\\TestData\\domino.rbac"))
    elif (DATA=="emea"):
        Original = numpy.matrix(parser.read("..\\TestData\\emea.rbac"))
    elif (DATA=="apj"):
        Original = numpy.matrix(parser.read("..\\TestData\\apj.rbac"))
    elif (DATA=="firewall1"):
        Original = numpy.matrix(parser.read("..\\TestData\\firewall1.rbac"))
    elif (DATA=="firewall2"):
        Original = numpy.matrix(parser.read("..\\TestData\\firewall2.rbac"))
    elif (DATA=="americas_small"):
        Original = numpy.matrix(parser.read("..\\TestData\\americas_small.rbac"))
    elif (DATA=="americas_large"):
        Original = numpy.matrix(parser.read("..\\TestData\\americas_large.rbac"))
    elif (DATA=="testdata"):
        testdata = [[1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 1, 1], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 1, 1], [1, 0, 0, 1, 1]]
        testdata2 = [[3, 3, 0, 0, 0], [2, 0, 0, 2, 2], [1, 0, 1, 1, 1], [2, 0, 0, 2, 2], [2, 0, 0, 2, 2], [4, 3, 0, 2, 2], [2, 0, 0, 2, 2]]
        Original = numpy.matrix(testdata2)
    elif (DATA=="random"):
        Original = matrixOps.generateGoalMatrix(4, 10, 10)
    elif (DATA=="GeneratedData"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151004-191825\\testdata.rbac"))
        userAttributeValues, userAttributes = parser.readUserAttributes("..\\TestData\\Data_20151004-191825\\users.csv")
        #constraints = parser.readConstraints("..\\TestData\\Data_20151004-191825\\constraints.csv")
    elif (DATA=="GeneratedData_small"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151005-194203\\testdata.rbac"))
        userAttributeValues, userAttributes = parser.readUserAttributes("..\\TestData\\Data_20151005-194203\\users.csv")
        #constraints = parser.readConstraints("..\\TestData\\Data_20151005-194203\\constraints.csv")
        URMatrix = parser.readURAssignments("..\\TestData\\Data_20151005-194203\\UsersToRoles.csv")
        RPMatrix = parser.readRPAssignments("..\\TestData\\Data_20151005-194203\\Roles.csv")
    elif (DATA=="GeneratedData_Set1"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151116-150651_10x10\\testdata.rbac"))
        userAttributeValues, userAttributes = parser.readUserAttributes("..\\TestData\\Data_20151116-150651_10x10\\users.csv")
        #constraints = parser.readConstraints("..\\TestData\\Data_20151116-150651_10x10\\constraints.csv")
        URMatrix = parser.readURMatrix("..\\TestData\\Data_20151116-150651_10x10\\URMatrix.csv")
        RPMatrix = parser.readRPMatrix("..\\TestData\\Data_20151116-150651_10x10\\RPMatrix.csv")
        individual = utils.buildIndividual(URMatrix,RPMatrix)
        fitness = eval.evalFunc_WSC_INT([individual], Original.shape[0], Original.shape[1], Original, [0,1,1,0.5,0.5,0.8], userAttributeValues, constraints=[])
        logger.info("VALIDATION OF DATASET")
        logger.info("Fitness of solution of dataset: "+str(fitness))
    return Original, userAttributeValues, userAttributes, constraints

#-----------------------------------------------------------------------------------------------------------------------
# Helpmethod: Extract filename from filepath
#-----------------------------------------------------------------------------------------------------------------------
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#-----------------------------------------------------------------------------------------------------------------------
# Loads configurations for several experiments from file
#-----------------------------------------------------------------------------------------------------------------------
def executeExperimentFromFile():
    # ------------------------------------------------------------------------------------------------------------------
    # Select Experiment File
    # ------------------------------------------------------------------------------------------------------------------
    root = tk.Tk()
    root.withdraw()
    selectedFile = filedialog.askopenfilename(initialdir = "..\\Input")
    if (selectedFile == ''):
        logger.info('Program stopped')
    else:
        jsonText = ""
        with open(selectedFile) as f:
            for line in f:
                jsonText += (line)
            f.close()
        experiments = json.loads(jsonText)
        # --------------------------------------------------------------------------------------------------------------
        # Parse Experiment File and execute experiments
        # --------------------------------------------------------------------------------------------------------------
        logger.info("Experiment Settings: ")
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")

        directory = "..\\Output\\"+timestamp+"_EXP_"+path_leaf(selectedFile).split(".")[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        shutil.copyfile(selectedFile, directory+"\\"+path_leaf(selectedFile)) #copy input file in output directory

        eval_weights = []
        obj_weights = []

        experimentNumber = 0
        for experiment in experiments:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            experimentNumber += 1
            if ("Experiment" in experiment.keys()):
                customName = experiment["Experiment"]
                logger.info("Name: "+customName)
                #Name = timestamp+"_"+customName
                Name = customName
            if ("DATA" in experiment.keys()):
                DATA = experiment["DATA"]
                Original, userAttributeValues, userAttributes, constraints = getDataSet(DATA)
            if ("POP_SIZE" in experiment.keys()):
                POP_SIZE = int(experiment["POP_SIZE"])
                logger.info("POP_SIZE: "+str(POP_SIZE))
            if ("tournsize" in experiment.keys()):
                tournsize = int(experiment["tournsize"])
                logger.info("tournsize: "+str(tournsize))
            if ("CXPB" in experiment.keys()):
                CXPB = float(experiment["CXPB"])
                logger.info("CXPB: "+str(CXPB))
            if ("MUTPB_All" in experiment.keys()):
                MUTPB_All = float(experiment["MUTPB_All"])
                logger.info("MUTPB_All: "+str(MUTPB_All))
            if ("addRolePB" in experiment.keys()):
                addRolePB = float(experiment["addRolePB"])
                logger.info("addRolePB: "+str(addRolePB))
            if ("removeRolePB" in experiment.keys()):
                removeRolePB = float(experiment["removeRolePB"])
                logger.info("removeRolePB: "+str(removeRolePB))
            if ("removeUserPB" in experiment.keys()):
                removeUserPB = float(experiment["removeUserPB"])
                logger.info("removeUserPB: "+str(removeUserPB))
            if ("removePermissionPB" in experiment.keys()):
                removePermissionPB = float(experiment["removePermissionPB"])
                logger.info("removePermissionPB: "+str(removePermissionPB))
            if ("addUserPB" in experiment.keys()):
                addUserPB = float(experiment["addUserPB"])
                logger.info("addUserPB: "+str(addUserPB))
            if ("addPermissionPB" in experiment.keys()):
                addPermissionPB = float(experiment["addPermissionPB"])
                logger.info("addPermissionPB: "+str(addPermissionPB))
            if ("NGEN" in experiment.keys()):
                NGEN = int(experiment["NGEN"])
                logger.info("NGEN: "+str(NGEN))
            if ("freq" in experiment.keys()):
                freq = int(experiment["freq"])
                logger.info("freq: "+str(freq))
            if ("evolutionType" in experiment.keys()):
                evolutionType = experiment["evolutionType"]
                logger.info("evolutionType: "+evolutionType)
            if ("evalFunc" in experiment.keys()):
                evalFunc = [o for o in experiment["evalFunc"].split(',')]
                logger.info("evalFunc: "+str(evalFunc))

            if ("eval_weights" in experiment.keys()):
                eval_weights = [float(w) for w in experiment["eval_weights"].split(',')]
                logger.info("eval_weights: "+str(eval_weights))
            if (evalFunc == "Saenko" or evalFunc == "Saenko_Euclidean" or evalFunc == "WSC" or evalFunc == "WSC_Star"):
                if ((not eval_weights
                    or evalFunc == "Saenko" and  len(eval_weights)!=3)
                    or(evalFunc == "Saenko_Euclidean" and  len(eval_weights)!=2)
                    or(evalFunc == "WSC" and  len(eval_weights)!=4)
                    or(evalFunc == "WSC_Star" and  len(eval_weights)!=5)):
                    raise ValueError("Number of weights is incorrect for evaluation function")

            if ("obj_weights" in experiment.keys()):
                obj_weights = [float(w) for w in experiment["obj_weights"].split(',')]
                logger.info("obj_weights: "+str(obj_weights))
            if (evolutionType == "Multi_Weighted" or evolutionType == "Multi_Fortin2013_Weighted"):
                if (not obj_weights or len(obj_weights)!=2):
                    raise ValueError("Number of weights is incorrect for evolution Type")

            if ("numberOfTrialItems" in experiment.keys()):
                if (evolutionType == "SANE"):
                    numberOfTrialItems = int(experiment["numberOfTrialItems"])
                    logger.info("numberOfTrialItems: "+str(numberOfTrialItems))
                else:
                    numberOfTrialItems = 0
            if ("repeat" in experiment.keys()):
                repeat = int(experiment["repeat"])
                logger.info("repeat: "+str(repeat))
            if ("untilSolutionFound" in experiment.keys()):
                untilSolutionFound = experiment["untilSolutionFound"] == "True"
                logger.info("untilSolutionFound: "+str(untilSolutionFound))
            if ("optimization" in experiment.keys()):
                optimization = experiment["optimization"] == "True"
                logger.info("optimization: "+str(optimization))
            logger.info("===================================================================================================")
            logger.info("Start "+str(repeat)+" experiments of "+str(experimentNumber)+". experiment in experiment sequence named '"+customName+"'...")
            logger.info("===================================================================================================")

            for experimentCnt in range(1,repeat+1):
                logger.info("Experiment "+str(experimentCnt)+" of "+str(repeat))
                logger.info("---------------------------------------------------------------------------------------------------")
                if (evolutionType == "SANE"):
                    sane.execute(Original, POP_SIZE, removeUserPB, removePermissionPB, addUserPB, addPermissionPB,
                     NGEN, numberOfTrialItems, freq)
                else:
                    logbooksSubsubdirectory,setupInfo,fileExt = rm_builder.startExperiment(directory, Name, experimentNumber,
                                                        experimentCnt, Original, DATA, POP_SIZE, tournsize, CXPB,
                                                        MUTPB_All, addRolePB, removeRolePB, removeUserPB,
                                                        removePermissionPB, addUserPB, addPermissionPB, NGEN, freq,
                                                        evolutionType, evalFunc, untilSolutionFound, optimization,
                                                        obj_weights=obj_weights,
                                                        eval_weights=eval_weights,
                                                        userAttributeValues=userAttributeValues,
                                                        constraints=constraints)
            exp_eval.execute(logbooksSubsubdirectory,setupInfo,fileExt,freq)

#-----------------------------------------------------------------------------------------------------------------------
# Asks user for configuration for the experiment
#-----------------------------------------------------------------------------------------------------------------------
def executeCustomExperiment():
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    customName = input('Name of the experiment (press enter to skip):\n')
    if (customName==''):
        customName = "Default_Experiment"
    Name = timestamp+"_"+customName

    DATA="GeneratedData"
    DATAinput = input('Select dataset:\n'
                      '(1) GeneratedData\n'
                      '(2) GeneratedData (small)\n'
                      '(3) healthcare\n'
                      '(4) testdata\n')
    if (DATAinput=="1"):
        DATA="GeneratedData"
    elif (DATAinput=="2"):
        DATA="GeneratedData_small"
    elif (DATAinput=="3"):
        DATA="healthcare"
    elif (DATAinput=="4"):
        DATA="testdata"
    else:
        raise ValueError('Input not valid')
    Original = getDataSet(DATA)

    POP_SIZE = int(input('Population size?\n'))
    NGEN = int(input('How many generations?\n'))
    freq = int(input('Frequence of logging information (every x generations)?\n'))
    evolutionType = 'Single'
    evolutionTypeInput = input('Choose evolution type:\n'
                               '(1) Single Objective\n'
                               '(2) Multi Objective\n'
                               '(3) Multi Objective with Fortin2013 optimization\n'
                               '(4) Multi Objective with weights\n'
                               '(5) Multi Objective with weights and Fortin2013 optimization\n'
                               '(6) SANE\n')
    if (evolutionTypeInput=="1"):
        evolutionType="Single"
    elif (evolutionTypeInput=="2"):
        evolutionType="Multi"
    elif (evolutionTypeInput=="3"):
        evolutionType="Multi_Fortin2013"
    elif (evolutionTypeInput=="4"):
        evolutionType="Multi_Weighted"
    elif (evolutionTypeInput=="5"):
        evolutionType="Multi_Fortin2013_Weighted"
    elif (evolutionTypeInput=="6"):
        evolutionType="SANE"
    else:
        raise ValueError('Input not valid')

    if (evolutionType!="SANE"):
        tournsize = int(input('Tournsize?\n'))
        CXPB = float(input('Crossover probability?\n'))
        if ( not evolutionType.startswith("Multi")):
            MUTPB_All = float(input('Mutation probability?\n'))
        addRolePB = float(input('Mutation: Add role probability?\n'))
        removeRolePB = float(input('Mutation: Remove role probability?\n'))
    removeUserPB = float(input('Mutation: Remove user probability?\n'))
    removePermissionPB = float(input('Mutation: Remove permission probability?\n'))
    addUserPB = float(input('Mutation: Add user probability?\n'))
    addPermissionPB = float(input('Mutation: Add permission probability?\n'))

    if (evolutionType=="SANE"):
        numberOfTrialItems = int( input('Number of roles in each trial?\n'))
        sane.execute(Original, POP_SIZE, removeUserPB, removePermissionPB, addUserPB, addPermissionPB,
                     NGEN, numberOfTrialItems, freq)
    else:
        evalFunc = None
        obj_weights = None
        eval_weights = None

        if (evolutionType == 'Single'):
            evalFuncInput = input('Choose evolution type:\n'
                                  '(1) Confidentiality\n'
                                  '(2) Availability\n'
                                  '(3) Role Count\n'
                                  '(4) Confidentiality + Availability (normalized)\n'
                                  '(5) Saenko (normalized)\n'
                                  '(6) Saenko with euclidean distance (normalized)\n'
                                  '(7) WSC (normalized)\n'
                                  '(8) WSC* (normalized)\n')
            if (evalFuncInput=="1"):
                evalFunc="Confidentiality"
            elif (evalFuncInput=="2"):
                evalFunc="Availability"
            elif (evalFuncInput=="3"):
                evalFunc="RoleCnt"
            elif (evalFuncInput=="4"):
                evalFunc="Violations"
            elif (evalFuncInput=="5"):
                evalFunc="Saenko"
                eval_weights = [float(w) for w in input('Type in 3 weights separated by comma\n').split(',')]
                if (len(eval_weights)!=3):
                    raise ValueError("Not correct amount of weights")
            elif (evalFuncInput=="6"):
                evalFunc="Saenko_Euclidean"
                eval_weights = [float(w) for w in input('Type in 2 weights separated by comma\n').split(',')]
                if (len(eval_weights)!=2):
                    raise ValueError("Not correct amount of weights")
            elif (evalFuncInput=="7"):
                evalFunc="WSC"
                eval_weights = [float(w) for w in input('Type in 4 weights separated by comma\n').split(',')]
                if (len(eval_weights)!=4):
                    raise ValueError("Not correct amount of weights")
            elif (evalFuncInput=="8"):
                evalFunc="WSC_Star"
                eval_weights = [float(w) for w in input('Type in 5 weights separated by comma\n').split(',')]
                if (len(eval_weights)!=5):
                    raise ValueError("Not correct amount of weights")
            else:
                raise ValueError('Input not valid')

        if (evolutionType == 'Multi' or evolutionType == 'Multi_Fortin2013'):
            objCnt = int(input('Do you want to choose 2 or 3 objectives?\n'))
            if (objCnt < 2 or objCnt > 3):
                raise ValueError("Objective count is not valid")
            evalFunc = ()
            for o in range(0,objCnt):
                print("Current objectives: "+str(evalFunc))
                objective = input('Choose an objective:\n'
                                  '(1) Confidentiality\n'
                                  '(2) Availability\n'
                                  '(3) Role Count\n'
                                  '(4) Confidentiality + Availability (normalized)\n')
                if (objective=="1"):
                     evalFunc+= ("Confidentiality",)
                elif (objective=="2"):
                    evalFunc+= ("Availability",)
                elif (objective=="3"):
                    evalFunc+= ("RoleCnt",)
                elif (objective=="4"):
                    evalFunc+= ("Violations",)
            print("Chosen objectives: "+str(evalFunc))
        if (evolutionType == 'Multi_Weighted' or evolutionType == 'Multi_Fortin2013_Weighted'):
            evalFuncInput = input('Choose evolution type:\n'
                                  '(1) Normal\n'
                                  '(2) Euclidean\n')
            if (evalFuncInput=="1"):
                evalFunc="Normal"
            elif (evalFuncInput=="2"):
                evalFunc="Euclidean"
            else:
                raise ValueError('Input not valid')
            obj_weights = [float(w) for w in input('Type in 2 weights separated by comma\n').split(',')]
            if (len(obj_weights)!=2):
                    raise ValueError("Not correct amount of weights")

        repeat = int(input('How often shall the experiment be repeated\n'))
        untilSolutionFound = bool(input('Run until solution found? (True/False)\n'))
        optimization = bool(input('Use local optimization after mutation/mating? (True/False)\n'))
        directory = "..\\Output"
        for experimentCnt in range(1,repeat+1):
            rm_builder.startExperiment(directory,Name,1,experimentCnt,Original,DATA,POP_SIZE,tournsize,CXPB,MUTPB_All, addRolePB, removeRolePB, removeUserPB,
                           removePermissionPB, addUserPB, addPermissionPB, NGEN,freq,evolutionType,evalFunc,untilSolutionFound, optimization,
                           obj_weights=obj_weights,eval_weights=eval_weights)

#-----------------------------------------------------------------------------------------------------------------------
# Loads configuration for experiment from configfile
#-----------------------------------------------------------------------------------------------------------------------
def executeDefaultExperiment():
    experimentName = "Default_Experiment"
    DATA="GeneratedData"
    POP_SIZE = 100
    tournsize = 5
    CXPB = 0.25
    MUTPB_All = 0.25
    addRolePB = 0.25
    removeRolePB = 0.25
    removeUserPB = 0.25
    removePermissionPB = 0.25
    addUserPB = 0.25
    addPermissionPB = 0.25
    NGEN = 100
    freq = 1
    evolutionType = 'Single'
    evalFunc = 'Obj1'
    eval_weights = [1.0,1.0]
    obj_weights = [1.0,1.0]
    numberOfTrialItems = 3
    untilSolutionFound = False
    optimization = True
    repeat = 1

    config = configparser.ConfigParser()
    config.read('Experiments_config.ini')
    if (len(config.sections()) == 0):
        logger.info("Create new config file...")
        config['Dataset'] = {'DATA': DATA}
        config['General'] = {'experiment_Name': experimentName, 'POP_SIZE': POP_SIZE,'tournsize': tournsize, 'CXPB': CXPB, 'MUTPB_All': MUTPB_All,'addRolePB': addRolePB,
                             'removeRolePB': removeRolePB,'removeUserPB': removeUserPB,
                             'removePermissionPB': removePermissionPB, 'addUserPB': addUserPB,
                             'addPermissionPB': addPermissionPB, 'NGEN': NGEN, 'freq': freq}
        config['Algorithm'] = {'evolutionType': evolutionType, 'evalFunc': evalFunc, 'eval_weights': eval_weights, 'obj_weights': obj_weights,
                               'until_Solution_Found': untilSolutionFound, 'optimization': optimization}
        config['Experiment'] = {'repeat': repeat}
        with open('Experiments_config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        DATA = config['Dataset']['DATA']
        experimentName = config['General']['experiment_Name']
        POP_SIZE = config['General'].getint('POP_SIZE')
        tournsize = config['General'].getint('tournsize')
        CXPB = config['General'].getfloat('CXPB')
        MUTPB_All = config['General'].getfloat('MUTPB_All')
        addRolePB = config['General'].getfloat('addRolePB')
        removeRolePB = config['General'].getfloat('removeRolePB')
        removeUserPB = config['General'].getfloat('removeUserPB')
        removePermissionPB = config['General'].getfloat('removePermissionPB')
        addUserPB = config['General'].getfloat('addUserPB')
        addPermissionPB = config['General'].getfloat('addPermissionPB')
        NGEN = config['General'].getint('NGEN')
        freq = config['General'].getint('freq')
        evolutionType = config['Algorithm']['evolutionType']
        evalFunc = [o for o in config['Algorithm']['evalFunc'].split(',')]
        if (evolutionType == 'Multi_Weighted' or evolutionType == 'Multi_Fortin2013_Weighted'):
            obj_weights = [float(w) for w in config['Algorithm']['obj_weights'].split(',')]
        if (evalFunc[0] == 'Saenko' or evalFunc[0] == 'Saenko_Euclidean' or evalFunc[0] == 'WSC'
            or evalFunc[0] == 'WSC_Star' or evalFunc[0] =='WSC_Star_RoleDis' or evalFunc[0] == "WSC_INT"):
            eval_weights = [float(w) for w in config['Algorithm']['eval_weights'].split(',')]
        if (evolutionType == "SANE"):
            numberOfTrialItems = config['Algorithm'].getint('numberOfTrialItems')
        untilSolutionFound = config['Algorithm'].getboolean('until_Solution_Found')
        optimization = config['Algorithm'].getboolean('optimization')
        repeat = config['Experiment'].getint('repeat')
        if (DATA == None or experimentName == None or POP_SIZE == None or tournsize == None or CXPB == None or MUTPB_All == None
            or addRolePB == None or removeRolePB == None or removeUserPB == None or removePermissionPB == None
            or addUserPB == None or addPermissionPB == None or NGEN == None or freq == None
            or evolutionType == None or evalFunc == None or obj_weights == None or eval_weights == None
            or numberOfTrialItems == None or repeat == None):
            raise ValueError("Config file 'Experiments_config.ini' is corrupt. Create new one by deleting the old one.")
        if (evalFunc[0] == "Saenko" or evalFunc[0] == "Saenko_Euclidean" or evalFunc[0] == "WSC" or evalFunc[0] == "WSC_Star"
            or evalFunc[0] == "WSC_Star_RoleDis" or evalFunc[0] == "WSC_INT"):
            numberOfWeights = len(eval_weights)
            if ((evalFunc == "Saenko" and numberOfWeights!=3)
                or(evalFunc == "Saenko_Euclidean" and numberOfWeights!=2)
                or(evalFunc == "WSC" and numberOfWeights!=4)
                or(evalFunc == "WSC_Star" and numberOfWeights!=5)
                or(evalFunc == "WSC_Star_RoleDis" and numberOfWeights!=6)
                or(evalFunc == "WSC_INT" and numberOfWeights!=6)):
                raise ValueError("Number of weights is incorrect for evaluation function")
        if (evolutionType == "Multi_Weighted" or evolutionType == "Multi_Fortin2013_Weighted"):
            numberOfWeights = len(obj_weights)
            if (numberOfWeights!=2):
                raise ValueError("Number of weights is incorrect for evolution Type")

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    Name = timestamp+"_"+experimentName
    Original, userAttributeValues, userAttributes, constraints = getDataSet(DATA)

    directory = "..\\Output"
    for experimentCnt in range(1,repeat+1):
        if (evolutionType == "SANE"):
            sane.execute(Original, POP_SIZE, removeUserPB, removePermissionPB, addUserPB, addPermissionPB, NGEN,
                         numberOfTrialItems, freq)
        else:
            logbooksSubsubdirectory,setupInfo,fileExt = rm_builder.startExperiment(directory, Name, 1, experimentCnt,
                                                        Original, DATA, POP_SIZE, tournsize, CXPB, MUTPB_All,
                                                        addRolePB, removeRolePB, removeUserPB, removePermissionPB,
                                                        addUserPB, addPermissionPB, NGEN, freq, evolutionType, evalFunc,
                                                        untilSolutionFound, optimization,
                                                        obj_weights=obj_weights,
                                                        eval_weights=eval_weights,
                                                        userAttributeValues=userAttributeValues,
                                                        constraints=constraints)
    exp_eval.execute(logbooksSubsubdirectory,setupInfo,fileExt,freq)

# create logger with 'spam_application'
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('logging.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatterFile = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s: %(message)s')
formatterScreen = logging.Formatter('%(message)s')
fh.setFormatter(formatterFile)
ch.setFormatter(formatterScreen)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

loadExperiment = input('Load experiment from file? (y/n)\n')
if (loadExperiment=='y'):
    executeExperimentFromFile()
elif (loadExperiment=='n'):
    customExperiment = input('Create custom experiment? (y/n)\n')
    if (customExperiment=='y'):
        executeCustomExperiment()
    elif (customExperiment=='n'):
        executeDefaultExperiment()
    else:
        raise ValueError('Input not valid')
else:
    raise ValueError('Input not valid')
