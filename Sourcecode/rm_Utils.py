__author__ = 'Theresa'

import json
import pickle
import os
import rm_Visualization as visual
import logging
logger = logging.getLogger('root')

# -----------------------------------------------------------------------------------
# Save role count diversity in JSON file
# -----------------------------------------------------------------------------------
def saveDiversity(gen,population,filename):
    individualBuckets = dict()
    for ind in population:
        roleCnt = ind.fitness.values[3]
        if roleCnt not in individualBuckets:
            individualBuckets[roleCnt] = [ind]
        else:
            individualBuckets[roleCnt].append(ind)
    entryList = dict()
    entryList["gen"] = gen
    for roleCnt in individualBuckets:
        entryList[roleCnt] = len(individualBuckets[roleCnt])
        logger.debug("RoleCnt="+str(roleCnt)+" Individuals: "+str(len(individualBuckets[roleCnt])))
    with open(filename, "w") as outfile:
        json.dump(entryList, outfile, indent=4)
        outfile.close()

# -----------------------------------------------------------------------------------
# Save all individuals of a population in a pickle file
# -----------------------------------------------------------------------------------
def savePopulation(gen,population,filename):
    cp = dict(population=population)
    pickle.dump(cp, open(filename, "wb"), 2)

# -----------------------------------------------------------------------------------
# Plot role count diversity for a generation in a boxplot
# -----------------------------------------------------------------------------------
def printDiversity(pop_folder):
    json_files = [pos_json for pos_json in os.listdir(pop_folder) if pos_json.endswith('_diversity.json')]
    cnt_jsonFiles = len(json_files)
    logger.debug("json_files: "+str(cnt_jsonFiles))
    logger.debug(json_files)
    data = [[] for g in range(0,cnt_jsonFiles)]
    gen_labels = [str(g) for g in range(0,cnt_jsonFiles)]
    for js in json_files:
        with open(os.path.join(pop_folder, js)) as json_file:
            gen_data = json.load(json_file)
            generation = int(gen_data.pop('gen'))
            data_list = []
            for item in gen_data:
                for cnt in range(0,int(gen_data[item])):
                    data_list.append(float(item))
            data[generation]=data_list
            json_file.close()

    freq = int(cnt_jsonFiles / 10)
    visual.diversityBoxplot(gen_labels[0::freq],data[0::freq],pop_folder+"\\diversity_boxplot")

# -----------------------------------------------------------------------------------
# Build individual out of URMatrix and RPMatrix
# -----------------------------------------------------------------------------------
def buildIndividual(URMatrix,RPMatrix):
    roleCnt = len(RPMatrix)
    rolemodel = [[set(),set()] for role in range(0,roleCnt)]
    for u,user in enumerate(URMatrix):
        for r,role in enumerate(user):
            if (role==1):
                rolemodel[r][0].update({u})
    for r,role in enumerate(RPMatrix):
        for p,permission in enumerate(role):
            if (permission==1):
                rolemodel[r][1].update({p})
    return rolemodel
