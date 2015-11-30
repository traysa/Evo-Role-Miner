__author__ = 'Theresa Brandt von Fackh'

import MatrixOperators as matrixOps

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