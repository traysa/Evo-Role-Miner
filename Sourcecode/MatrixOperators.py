__author__ = 'Theresa Brandt von Fackh'

# -----------------------------------------------------------------------------------
# Matrix operations for RoleMiner
# -----------------------------------------------------------------------------------

import numpy
import random

def createRandomMatrix(x, y):
    matrix = []
    for i in range(x):
        matrix.append([random.randint(0, 1) for el in range(y)])
    return matrix

def createEmptyMatrix(x, y):
    matrix = []
    for i in range(x):
        matrix.append([0 for el in range(y)])
    return matrix

def createEmptyMatrix2(x, y):
    matrix = []
    for i in range(x):
        matrix.append([[] for el in range(y)])
    return matrix

def printMatrix(matrix):
    matrix = numpy.array(matrix, dtype=int)
    for line in matrix:
        print("\t".join(map(str, line)))

def multiplyBoolMatrix(A, B):
    A = numpy.matrix(A, dtype=bool)
    B = numpy.matrix(B, dtype=bool)
    C = A * B
    return numpy.matrix(C, dtype=int)

def subtractIntMatrix(A, B):
    A = numpy.matrix(A, dtype=int)
    B = numpy.matrix(B, dtype=int)
    C = A - B
    return C

def countDiffs(matrix):
    diff1 = (matrix == 1).sum()
    diff2 = (matrix == -1).sum()
    return diff1, diff2

def compareMatrices(MatrixA,MatrixB):
    diffMatrix = subtractIntMatrix(A=numpy.matrix(MatrixA,dtype=bool), B=numpy.matrix(MatrixB,dtype=bool))
    'Violation of confidentiality and data availability'
    conf, accs = countDiffs(diffMatrix)
    return conf, accs

# -----------------------------------------------------------------------------------
# Data Generation for RoleMiner
# -----------------------------------------------------------------------------------
def generateGoalMatrix(k, n, m):
    A = createRandomMatrix(n, k)
    B = createRandomMatrix(k, m)
    C = multiplyBoolMatrix(A, B)
    return C