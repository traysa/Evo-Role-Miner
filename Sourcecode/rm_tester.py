__author__ = 'Theresa'

import rm_Utils as utils
import rm_FileParser as parser
import datetime
import numpy
import rm_GeneticAlgorithms2 as ga2
import os.path
import json
import rm_Visualization as visual


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

'''
testdata = [[1, 1, 0], [1, 1,0], [1,1,0]]
testdata2 = [[0, 0, 0], [0, 0, 0], [0,0,0]]
A = numpy.matrix(testdata)
B = numpy.matrix(testdata2)
dist = numpy.linalg.norm(A-B)
print("Euclidean distance: "+str(dist))
diffMatrix = matrixOps.subtractIntMatrix(A=A, B=B)
print("diffMatrix: "+str(diffMatrix))
conf, accs = matrixOps.countDiffs(diffMatrix)
print("conf: "+str(conf))
print("accs: "+str(accs))
'''

#parser.read2("..\TestData\Data_with_Semantics.csv")

#permissions = {1,2,3,4,5}
#attributes = {"color":{"red","blue","green"},"size":{1,2,3}}

#utils.generateGene2(permissions, attributes)


DATA="testdata"
Original = getDataSet(DATA)
POP_SIZE = 100
CXPB = 0.25
MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5, MUTPB_6 = 0.25,0.25,0.25,0.25,0.25,0.25,0.25
NGEN = 100
freq = 10
subdirectory = "..\\Output\\EvoMiner2"
population, results, generation, timeArray, top_pop, logbook = \
    ga2.evolution(Original, POP_SIZE, CXPB, MUTPB_All, MUTPB_1, MUTPB_2, MUTPB_3, MUTPB_4, MUTPB_5,
                         MUTPB_6, NGEN, freq)


# ------------------------------------------------------------------------------------------------------------------
# SAVE LOGBOOK IN FILE
# ------------------------------------------------------------------------------------------------------------------
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
if not os.path.exists(subdirectory+"\\Logbook"):
    os.makedirs(subdirectory+ "\\Logbook")
log_filename = subdirectory + "\\Logbook\\Logbook"+"_"+timestamp
class NumPyArangeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist() # or map(int, obj)
        return json.JSONEncoder.default(self, obj)
if (True):
    logfile = log_filename+".json"
    print("Save logfile into "+str(logfile)+"...")
    temp = logbook
    with open(logfile, "a") as outfile:
        json.dump(temp, outfile, indent=4, cls=NumPyArangeEncoder)
        outfile.close()
    print("DONE.\n")
    logfile = log_filename+".csv"
    print("Save logfile into "+str(logfile)+"...")
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
visual.plotLogbook(logbook, log_filename+"_plot_"+timestamp, True, True, True, False)
evolution_filename = subdirectory + "\\evolution"
roleModel_filename = subdirectory + "\\rolemodel"
visual.showFitnessInPlot(results, generation, freq, evolution_filename+"_"+timestamp, "Info", True, True, True, False)
visual.showBestResult(top_pop,generation,Original, roleModel_filename+"_"+timestamp, True, True, True, False)