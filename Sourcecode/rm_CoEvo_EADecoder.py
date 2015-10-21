__author__ = 'Theresa'

import rm_MatrixOperators as matrixOps

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

# -----------------------------------------------------------------------------------
# For SANE: Resolves several individuals (roles) into an boolean UP-matrix
# -----------------------------------------------------------------------------------
def resolveRoleChromosomesIntoBoolArray(individuals, userSize, permissionSize):
    matrix = matrixOps.createEmptyMatrix(userSize, permissionSize)
    for ind in individuals:
        user_list = ind[0][0]
        permission_list = ind[0][1]
        for user in user_list:
            for permission in permission_list:
                try:
                    matrix[user][permission] = 1
                except IndexError:
                    print("An error occured: ind="+str(ind))
                    raise
    return matrix
    # -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# For SANE: Resolves several individuals (roles) into an integer UP-matrix
# -----------------------------------------------------------------------------------
def resolveRoleChromosomesIntoIntArray(individuals, userSize, permissionSize):
    matrix = matrixOps.createEmptyMatrix(userSize, permissionSize)
    for ind in individuals:
        user_list = ind[0][0]
        permission_list = ind[0][1]
        for user in user_list:
            for permission in permission_list:
                try:
                    matrix[user][permission]+= 1
                except IndexError:
                    print("An error occured: ind="+str(ind))
                    raise
    return matrix

# -----------------------------------------------------------------------------------
# For SANE: Resolves several individuals (roles) into an UR-matrix, RP-matrix and UP-matrix
# -----------------------------------------------------------------------------------
def resolveRoleChromosomesIntoIntArrays(individuals, userSize, permissionSize):

    UMatrix = matrixOps.createEmptyMatrix(userSize, len(individuals))
    for i,ind in enumerate(individuals):
        user_list = ind[0][0]
        for user in user_list:
            UMatrix[user][i] = 1

    PMatrix = matrixOps.createEmptyMatrix(len(individuals),permissionSize)
    for i,ind in enumerate(individuals):
        permission_list = ind[0][1]
        for permission in permission_list:
            PMatrix[i][permission] = 1

    UPMatrix = resolveRoleChromosomesIntoIntArray(individuals, userSize, permissionSize)

    return UMatrix, PMatrix, UPMatrix