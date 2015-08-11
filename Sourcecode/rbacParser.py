'''
Parsing of TestData and Visualization
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy
import re
import matplotlib.pyplot as plt

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-i", dest="filename", default="..\\TestData\\healthcare.rbac",
     help="input file with UxP information", metavar="FILE")
(options, args) = parser.parse_args()

def read(filename):
    data = open(filename, 'r').read()
    lines = data.splitlines()

    # Count users
    userCount = max(list(map(int, re.findall('u_U(.+?) ', data))))+1
    print(userCount)

    # Count permissions
    permCount = max(list(map(int, re.findall('p_P(.+?) ', data))))+1
    print(permCount)

    # Create UP Matrix
    UPmatrix = [[0 for i in range(permCount)] for j in range(userCount)]
    for line in lines:
        if line.startswith("u_"):
            parts = line.split(" ")
            user = parts[0]
            userId = int(user[3:])
            for i in range(len(parts)-1):
                perm = parts[i+1]
                permId = int(perm[3:])
                #print(str(userId)+" , "+str(permId))
                UPmatrix[userId][permId] = 1
    return UPmatrix

UPmatrix = numpy.matrix(read(options.filename))
print(UPmatrix)

# Visualization
fig,(ax) = plt.subplots()
# using the ax subplot object, we use the same
# syntax as above, but it allows us a little
# bit more advanced control

#Split matrix
#split = int(UPmatrix.shape[1]/2)
#print(split)
#UPmatrix1 = UPmatrix[:,:int(split)]
#UPmatrix2 = UPmatrix[:,int(split):]

ax.pcolor(numpy.array(UPmatrix),cmap=plt.cm.Blues,edgecolors='#FFFFFF',linewidths=0.5)
ax.set_xticks(numpy.arange(UPmatrix.shape[1])+0.5)
ax.set_yticks(numpy.arange(UPmatrix.shape[0])+0.5)
#ax2.pcolor(numpy.array(UPmatrix2),cmap=plt.cm.Blues,edgecolors='#FFFFFF',linewidths=0.5)
#ax2.set_xticks(numpy.arange(UPmatrix2.shape[1])+0.5)
#ax2.set_yticks(numpy.arange(UPmatrix2.shape[0])+0.5)

# Here we put the x-axis tick labels
# on the top of the plot. The y-axis
# command is redundant, but inocuous.
ax.xaxis.tick_top()
ax.yaxis.tick_left()
#ax.axis('tight')
ax.set_xlim(0, UPmatrix.shape[1])
ax.set_ylim(0, UPmatrix.shape[0])
ax.invert_yaxis()
#ax2.xaxis.tick_top()
#ax2.yaxis.tick_left()
#ax2.axis('tight')
#ax2.set_xlim(0, UPmatrix2.shape[1])
#ax2.set_ylim(0, UPmatrix2.shape[0])
#ax2.invert_yaxis()

# similar syntax as previous examples
ax.set_xticklabels(range(0,UPmatrix.shape[1]),minor=False,rotation='vertical',fontsize=8)
ax.set_yticklabels(range(0,UPmatrix.shape[0]),minor=False,fontsize=8)
ax.tick_params(width=0)
#ax2.set_xticklabels(range(int(split),int(split)+UPmatrix2.shape[1]),minor=False,rotation='vertical',fontsize=8)
#ax2.set_yticklabels(range(0,UPmatrix2.shape[0]),minor=False,fontsize=8)
#ax2.tick_params(width=0)

# Here we use a text command instead of the title
# to avoid collision between the x-axis tick labels
# and the normal title position
plt.text(0.5,1.08,'User-Permission Matrix',horizontalalignment='center',transform=ax.transAxes)

# standard axis elements
plt.ylabel('Users')
plt.xlabel('Permissions')
plt.show()