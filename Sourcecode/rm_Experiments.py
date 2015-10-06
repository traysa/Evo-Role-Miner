__author__ = 'Theresa'

import rm_EvoRoleMiner as rm
import numpy
import rm_FileParser as parser
import rm_Utils as utils
import datetime
import json
import tkinter as tk
from tkinter import filedialog

# ----------------------------------------------------------------------------------------------------------------------
# DATA SETS
# ----------------------------------------------------------------------------------------------------------------------
def getDataSet(DATA):
    Original = []
    if (DATA=="healthcare"):
        Original = numpy.matrix(parser.read("..\\TestData\\healthcare.rbac"))
    elif (DATA=="testdata"):
        testdata = [[1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 1, 1], [1, 0, 0, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 1, 1], [1, 0, 0, 1, 1]]
        testdata2 = [[3, 3, 0, 0, 0], [2, 0, 0, 2, 2], [1, 0, 1, 1, 1], [2, 0, 0, 2, 2], [2, 0, 0, 2, 2], [4, 3, 0, 2, 2], [2, 0, 0, 2, 2]]
        Original = numpy.matrix(testdata2)
    elif (DATA=="random"):
        Original = utils.generateGoalMatrix(4, 10, 10)
    elif (DATA=="GeneratedData"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151004-191825\\testdata.rbac"))
    elif (DATA=="GeneratedData_small"):
        Original = numpy.matrix(parser.read("..\\TestData\\Data_20151005-194203\\testdata.rbac"))
    return Original

# ----------------------------------------------------------------------------------------------------------------------
# DEFAULT EXPERIMENT PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
Name = timestamp+"_"+"Default_Experiment"
DATA="GeneratedData"
Original = getDataSet(DATA)
POP_SIZE = 100
CXPB = 0.5
MUTPB_All = 0.5
addRolePB = 0.5
removeRolePB = 0.5
removeUserPB = 0.5
removePermissionPB = 0.5
addUserPB = 0.5
addPermissionPB = 0.5
NGEN = 1000
freq = 1
evolutionType = "Single"
evalFunc = "Saenko"
OBJ1PB = 1.0
OBJ2PB = 0.01
#OBJ3PB = 1.0

# ----------------------------------------------------------------------------------------------------------------------
# IMPORT EXPERIMENTS SEQUENCE FILE
# ----------------------------------------------------------------------------------------------------------------------
root = tk.Tk()
root.withdraw()
selectedFile = filedialog.askopenfilename(initialdir = "..\\Input")
if (selectedFile != ''):
    jsonText = ""
    with open(selectedFile) as f:
        for line in f:
            jsonText += (line)
        f.close()
    experiments = json.loads(jsonText)

# ----------------------------------------------------------------------------------------------------------------------
# START EXPERIMENT
# ----------------------------------------------------------------------------------------------------------------------
if (selectedFile == ''):
    rm.startExperiment(Name,Original,DATA,POP_SIZE,CXPB,MUTPB_All, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB,
                   NGEN,freq,evolutionType,evalFunc,OBJ1PB=OBJ1PB,OBJ2PB=OBJ2PB)
else:
    print("Experiment Settings: ")
    for experiment in experiments:
        if ("Experiment" in experiment.keys()):
            Name = timestamp+"_"+experiment["Experiment"]
            print("Name: "+Name)
        if ("DATA" in experiment.keys()):
            DATA = experiment["DATA"]
            Original = getDataSet(DATA)
        if ("POP_SIZE" in experiment.keys()):
            POP_SIZE = int(experiment["POP_SIZE"])
            print("POP_SIZE: "+str(POP_SIZE))
        if ("OBJ1PB" in experiment.keys()):
            OBJ1PB = float(experiment["OBJ1PB"])
            print("OBJ1PB: "+str(OBJ1PB))
        if ("OBJ2PB" in experiment.keys()):
            OBJ2PB = float(experiment["OBJ2PB"])
            print("OBJ2PB: "+str(OBJ2PB))
        if ("CXPB" in experiment.keys()):
            CXPB = float(experiment["CXPB"])
            print("CXPB: "+str(CXPB))
        if ("MUTPB_All" in experiment.keys()):
            MUTPB_All = float(experiment["MUTPB_All"])
            print("MUTPB_All: "+str(MUTPB_All))
        if ("addRolePB" in experiment.keys()):
            addRolePB = float(experiment["addRolePB"])
        if ("removeRolePB" in experiment.keys()):
            removeRolePB = float(experiment["removeRolePB"])
        if ("removeUserPB" in experiment.keys()):
            removeUserPB = float(experiment["removeUserPB"])
        if ("removePermissionPB" in experiment.keys()):
            removePermissionPB = float(experiment["removePermissionPB"])
        if ("addUserPB" in experiment.keys()):
            addUserPB = float(experiment["addUserPB"])
        if ("addPermissionPB" in experiment.keys()):
            addPermissionPB = float(experiment["addPermissionPB"])
        if ("NGEN" in experiment.keys()):
            NGEN = int(experiment["NGEN"])
            print("NGEN: "+str(NGEN))
        if ("freq" in experiment.keys()):
            freq = int(experiment["freq"])
            print("freq: "+str(freq))
        if ("evolutionType" in experiment.keys()):
            evolutionType = experiment["evolutionType"]
            print("evolutionType: "+evolutionType)
        if ("evalFunc" in experiment.keys()):
            evalFunc = experiment["evalFunc"]
            print("evalFunc: "+evalFunc)

        print("Start Experiment...")

        rm.startExperiment(Name,Original,DATA,POP_SIZE,CXPB,MUTPB_All, addRolePB, removeRolePB, removeUserPB, removePermissionPB, addUserPB, addPermissionPB,
                       NGEN,freq,evolutionType,evalFunc,OBJ1PB=OBJ1PB,OBJ2PB=OBJ2PB)