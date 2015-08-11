#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import matplotlib.pyplot as plt

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-i", dest="filename", default="..\\..\\Output\\2000.in",
     help="input file with two matrices", metavar="FILE")
(options, args) = parser.parse_args()

def read(filename):
    lines = open(filename, 'r').read().splitlines()
    A = []
    B = []
    matrix = A
    for line in lines:
        if line != "":
            matrix.append(list(map(int, line.split("\t"))))
            #matrix.append(line.split("\t"))
        else:
            matrix = B
    return A, B

def printMatrix(matrix):
    matrix = numpy.array(matrix)
    for line in matrix:
        print("\t".join(map(str,line)))

A, B = read(options.filename)
A = numpy.matrix(A)
B = numpy.matrix(B)
C = A * B # easy and intuitive, isn't it?
printMatrix(A)
print("")
printMatrix(B)
print("")
printMatrix(C)


#plt.imshow(B, interpolation='nearest')
fig, ax = plt.subplots()

#ax.pcolor(B,cmap=plt.cm.Reds,edgecolors='k')

# put the major ticks at the middle of each cell
ax.set_xticks(numpy.arange(B.shape[1])+0.5, minor=False)
ax.set_yticks(numpy.arange(B.shape[0])+0.5, minor=False)

# want a more natural, table-like display
#ax.invert_yaxis()
ax.xaxis.tick_top()
ax.yaxis.tick_left()

ax.set_xticklabels(['P1', 'P2', 'P3', 'P4'], minor=False)
ax.set_yticklabels(['U1', 'U2', 'U3'], minor=False)

# Here we use a text command instead of the title
# to avoid collision between the x-axis tick labels
# and the normal title position
plt.text(0.5,1.08,'Main Plot Title',horizontalalignment='center',transform=ax.transAxes)

# standard axis elements
plt.ylabel('Y Axis Label')
plt.xlabel('X Axis Label')

ax.imshow(B, interpolation='nearest')
ax.grid(True,color='white', linestyle='-', linewidth=1, which='both')

plt.show()