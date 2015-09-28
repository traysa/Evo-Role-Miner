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
    return Original

# ----------------------------------------------------------------------------------------------------------------------
# DEFAULT EXPERIMENT PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
Name = timestamp+"_"+"Default_Experiment"
DATA="testdata"
Original = getDataSet(DATA)
POP_SIZE = 100
CXPB = 0.25
MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6 = 0.25,0.25,0.25,0.25,0.25,0.25,0.25
NGEN = 10
freq = 1
evolutionType = "Multi_Weighted"
evalFunc = "Normal"
OBJ1PB = 1.0
OBJ2PB = 1.0

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
    rm.startExperiment(Name,Original,DATA,POP_SIZE,CXPB,MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6,
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
        if ("MUTPB_1" in experiment.keys()):
            MUTPB_1 = float(experiment["MUTPB_1"])
        if ("MUTPB_2" in experiment.keys()):
            MUTPB_2 = float(experiment["MUTPB_2"])
        if ("MUTPB_3" in experiment.keys()):
            MUTPB_3 = float(experiment["MUTPB_3"])
        if ("MUTPB_4" in experiment.keys()):
            MUTPB_4 = float(experiment["MUTPB_4"])
        if ("MUTPB_5" in experiment.keys()):
            MUTPB_5 = float(experiment["MUTPB_5"])
        if ("MUTPB_6" in experiment.keys()):
            MUTPB_6 = float(experiment["MUTPB_6"])
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

        rm.startExperiment(Name,Original,DATA,POP_SIZE,CXPB,MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6,
                       NGEN,freq,evolutionType,evalFunc,OBJ1PB=OBJ1PB,OBJ2PB=OBJ2PB)