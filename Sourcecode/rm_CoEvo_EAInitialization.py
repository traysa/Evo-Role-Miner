__author__ = 'Theresa'

import rm_EAInitialization as base

# -----------------------------------------------------------------------------------
# Initialization of Population (Chromosomes)
# Role
# -----------------------------------------------------------------------------------
def generateChromosome(userSize, permissionSize):
    chromosome = []
    # Create a role as chromosome
    chromosome = base.generateGene_simple(userSize, permissionSize)
    return chromosome
