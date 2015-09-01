__author__ = 'Theresa'

import datetime
import rm_Utils as utils
import rm_Visualization as visual

chromosome = [[[3],[1,3,4,5]],[[2,4,5,6,7],[1,4,5]],[[1,6],[1,2]]]
matrix = utils.resolveChromosomeIntoArray2(chromosome, 7, 5)
print(matrix)
visual.showMatrix(matrix)

