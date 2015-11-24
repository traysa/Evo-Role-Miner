__author__ = 'Theresa'
import os, json
import numpy
import rm_Visualization as visual
import logging
logger = logging.getLogger('root')

# -----------------------------------------------------------------------------------
# Summarize logbook for single objective EA
# -----------------------------------------------------------------------------------
def summarizeLogbooks(logbookfolder,freq):
    json_files = [pos_json for pos_json in os.listdir(logbookfolder) if pos_json.endswith('.json')]
    cnt_jsonFiles = len(json_files)
    logger.debug("json_files: "+str(cnt_jsonFiles))
    logger.debug(json_files)
    results_summedUp = []
    generations = 0
    for js in json_files:
        with open(os.path.join(logbookfolder, js)) as json_file:
            data = json.load(json_file)
            generations = len(data)
            logger.debug("Generations: "+str(generations))
            if (results_summedUp==[]):
                results_summedUp = [[] for gen in range(0,generations)]
            for item in data:
                gen_Data = results_summedUp[int(int(item['gen'])/freq)]
                if (gen_Data==[]):
                    gen_Data = [0.0 for gen in range(0,9)]
                    results_summedUp[int(int(item['gen'])/freq)] = gen_Data
                gen_Data[0] += int(item['evals'])
                gen_Data[1] += float(item['Fitness']['min'])
                gen_Data[2] += float(item['Conf']['min'])
                gen_Data[3] += float(item['Accs']['min'])
                gen_Data[4] += float(item['RoleCnt']['min'])
                gen_Data[5] += float(item['URCnt']['min'])
                gen_Data[6] += float(item['RPCnt']['min'])
                gen_Data[7] += float(item['Interp']['max'])
                gen_Data[8] += float(item['RoleCnt']['std'])
            json_file.close()
    #print(results_summedUp)
    for gen in results_summedUp:
        for i,item in enumerate(gen):
            gen[i] = item/cnt_jsonFiles
    #for i in results_summedUp:
    #    print(i)
    return results_summedUp, json_files

# -----------------------------------------------------------------------------------
# Summarize logbook for multi objective EA
# -----------------------------------------------------------------------------------
def summarizeLogbooks_Multi(logbookfolder,freq, evalFunc):
    json_files = [pos_json for pos_json in os.listdir(logbookfolder) if pos_json.endswith('.json')]
    cnt_jsonFiles = len(json_files)
    logger.debug("json_files: "+str(cnt_jsonFiles))
    logger.debug(json_files)
    results_summedUp = []
    generations = 0
    for js in json_files:
        with open(os.path.join(logbookfolder, js)) as json_file:
            data = json.load(json_file)
            generations = len(data)
            logger.debug("Generations: "+str(generations))
            if (results_summedUp==[]):
                results_summedUp = [[] for gen in range(0,generations)]
            for item in data:
                gen_Data = results_summedUp[int(int(item['gen'])/freq)]
                if (gen_Data==[]):
                    gen_Data = [0.0 for gen in range(0,(8+len(evalFunc)))]
                    results_summedUp[int(int(item['gen'])/freq)] = gen_Data
                i = 0
                gen_Data[i] += int(item['evals'])
                i += 1
                for e in evalFunc:
                    gen_Data[i] += float(item["fitness_"+e]['min'])
                    i += 1
                gen_Data[i] += float(item['Conf']['min'])
                i += 1
                gen_Data[i] += float(item['Accs']['min'])
                i += 1
                gen_Data[i] += float(item['RoleCnt']['min'])
                i += 1
                gen_Data[i] += float(item['URCnt']['min'])
                i += 1
                gen_Data[i] += float(item['RPCnt']['min'])
                i += 1
                gen_Data[i] += float(item['Interp']['max'])
                i += 1
                gen_Data[i] += float(item['RoleCnt']['std'])
            json_file.close()
    #print(results_summedUp)
    for gen in results_summedUp:
        for i,item in enumerate(gen):
            gen[i] = item/cnt_jsonFiles
    #for i in results_summedUp:
    #    print(i)
    return results_summedUp, json_files

def execute(dirname,setupInfo,fileExt,freq,multi=False,evalFunc=[]):
    if (multi):
        data, json_files = summarizeLogbooks_Multi(dirname,freq,evalFunc)
        title = fileExt[1:]+"\n(AVG of "+str(len(json_files))+" experiments)"
        #visual.plotAllParetoFronts(data, dirname+"\\logbook_AVG", expCnt, title, setupInfo, True, False, True, False,freq)
    else:
        data, json_files = summarizeLogbooks(dirname,freq)
        title = fileExt[1:]+"\n(AVG of "+str(len(json_files))+" experiments)"
        visual.plotLogbookAVG(data, dirname+"\\logbook_AVG", ["Fitness"], title, setupInfo, True, False, True, False,freq)

    visual.plotLogbookAVG(data, dirname+"\\logbook_measures_AVG", ["Conf","Accs","RoleCnt","URCnt","RPCnt","Interp","RoleCnt_Std"], title, setupInfo, True, False, True, False,freq,multi=multi,evalFunc=evalFunc)