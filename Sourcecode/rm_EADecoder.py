__author__ = 'Theresa'

import MatrixOperators as matrixOps

# -----------------------------------------------------------------------------------
# Resolves an individual (chromosome) into an boolean UP-matrix
# -----------------------------------------------------------------------------------
def resolveRoleModelChromosomeIntoBoolArray(chromosome, userSize, permissionSize):
    matrix = matrixOps.createEmptyMatrix(userSize, permissionSize)
    # Iterate through all genes of a chromosome
    for gene in range(0, len(chromosome)):
        # print("Gene: " +str(gene))
        # print(chromosome[gene])
        user_list = chromosome[gene][0]
        permission_list = chromosome[gene][1]
        for user in user_list:
            for permission in permission_list:
                matrix[user][permission] = 1
    return matrix

# -----------------------------------------------------------------------------------
# Resolves a chromosome into an UR-matrix, RP-matrix and integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveRoleModelChromosomeIntoBoolArrays(chromosome, userSize, permissionSize):

    UMatrix = matrixOps.createEmptyMatrix(userSize, len(chromosome))
    for gene in range(0, len(chromosome)):
        user_set = chromosome[gene][0]
        for user in user_set:
            UMatrix[user][gene] = 1
    #print("\nUMatrix")
    #print(UMatrix)

    PMatrix = matrixOps.createEmptyMatrix(len(chromosome),permissionSize)
    for gene in range(0, len(chromosome)):
        permission_list = chromosome[gene][1]
        for permission in permission_list:
            PMatrix[gene][permission] = 1
    #print("\nPMatrix")
    #print(PMatrix)

    UPMatrix = resolveRoleModelChromosomeIntoBoolArray(chromosome, userSize, permissionSize)
    #print("\nUPMatrix")
    #print(UPMatrix)

    return UMatrix, PMatrix, UPMatrix

# -----------------------------------------------------------------------------------
# Resolves an individual (chromosome) into an integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveRoleModelChromosomeIntoIntArray(chromosome, userSize, permissionSize):
    matrix = matrixOps.createEmptyMatrix(userSize, permissionSize)
    # Iterate through all genes of a chromosome
    for gene in range(0, len(chromosome)):
        # print("Gene: " +str(gene))
        # print(chromosome[gene])
        user_list = chromosome[gene][0]
        permission_list = chromosome[gene][1]
        for user in user_list:
            for permission in permission_list:
                matrix[user][permission] += 1
                #if (matrix[user][permission] == 0):
                #    matrix[user][permission] += 1 #gene+1
                #else:
                #    matrix[user][permission] += 1 #len(chromosome)+1
    return matrix

# -----------------------------------------------------------------------------------
# Resolves a chromosome into an UR-matrix, RP-matrix and integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveRoleModelChromosomeIntoIntArrays(chromosome, userSize, permissionSize):

    UMatrix = matrixOps.createEmptyMatrix(userSize, len(chromosome))
    for gene in range(0, len(chromosome)):
        user_set = chromosome[gene][0]
        for user in user_set:
            UMatrix[user][gene] = 1
    #print("\nUMatrix")
    #print(UMatrix)

    PMatrix = matrixOps.createEmptyMatrix(len(chromosome),permissionSize)
    for gene in range(0, len(chromosome)):
        permission_list = chromosome[gene][1]
        for permission in permission_list:
            PMatrix[gene][permission] = 1
    #print("\nPMatrix")
    #print(PMatrix)

    UPMatrix = resolveRoleModelChromosomeIntoIntArray(chromosome, userSize, permissionSize)
    #print("\nUPMatrix")
    #print(UPMatrix)

    return UMatrix, PMatrix, UPMatrix
