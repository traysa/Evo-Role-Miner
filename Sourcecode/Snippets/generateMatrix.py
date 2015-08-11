#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
random.seed(1234)

def createRandomMatrix(x, y):
    maxVal = 1 # I don't want to get Java / C++ into trouble
    matrix = []
    for i in range(x):
        matrix.append([random.randint(0,maxVal) for el in range(y)])
    return matrix

def saveMatrix(matrixA, matrixB, filename):
    f = open(filename, 'w')
    for i, matrix in enumerate([matrixA, matrixB]):
        if i != 0:
            f.write("\n")
        for line in matrix:
            f.write("\t".join(map(str, line)) + "\n")
            
x = 2
y = 3
z = 4
matrixA = createRandomMatrix(x,y)
matrixB = createRandomMatrix(y,z)
saveMatrix(matrixA, matrixB, "..\\..\\Output\\2000.in")