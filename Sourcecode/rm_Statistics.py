__author__ = 'Theresa Brandt von Fackh'

import MatrixOperators as matrixOps
import rm_EADecoder as decoder
import numpy
import copy
import rm_Utils as utils

def Conf(rolemodel, Original):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(rolemodel, Original.shape[0], Original.shape[1])
    conf, accs = matrixOps.compareMatrices(array,Original)
    return int(conf)

def Accs(rolemodel, Original):
    array = decoder.resolveRoleModelChromosomeIntoBoolArray(rolemodel, Original.shape[0], Original.shape[1])
    conf, accs = matrixOps.compareMatrices(array,Original)
    return int(accs)

def RoleCnt(rolemodel):
    return len(rolemodel)

def URCnt(rolemodel):
    numberOfUR = 0
    for userlists in numpy.array(rolemodel)[:,0]:
        numberOfUR += len(userlists)
    return int(numberOfUR)

def RPCnt(rolemodel):
    numberOfRP = 0
    for permissionlists in numpy.array(rolemodel)[:,1]:
        numberOfRP += len(permissionlists)
    return int(numberOfRP)

def Interp(rolemodel, userAttributeValues):
    interp = 0
    if (userAttributeValues):
        userAttributeValuesWithClass = copy.deepcopy(userAttributeValues)
        for user in userAttributeValuesWithClass:
            user.append(False)
        interp = utils.measureInterpretability(rolemodel, userAttributeValuesWithClass)
    return float(interp)