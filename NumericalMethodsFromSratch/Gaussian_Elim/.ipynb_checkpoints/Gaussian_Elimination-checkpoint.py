import numpy as np



def find_pivot(a, k):
    matrix = np.abs(a[k:, k:])
    max_idx_flat = matrix.argmax()
    max_idx = np.unravel_index(max_idx_flat, matrix.shape)
    return max_idx[0]+k, max_idx[1]+k

def gauss(A, B):
    
    #Creating variables
    a = A.astype(float).copy()
    b = B.astype(float).copy()
    n = len(a)
    logdet = np.longdouble(0.)
    sign = 1
    col_order = list(range(n))
    x = np.zeros(n, dtype=float)
    
    # Main pivoting algorythm
    for k in range(n):
        row, col = find_pivot(a, k)     #look for max value in matrix
        if row != k:
            sign *= -1
            a[[k, row]] = a[[row, k]]       # Swap rows
            b[k], b[row] = b[row], b[k]     # Swap rows
        if col != k:
            sign *= -1
            a[:, [k, col]] = a[:, [col, k]]                             # Swap cols
            col_order[k], col_order[col] = col_order[col], col_order[k] # Remember order
            
        if a[k][k] == 0: raise np.linalg.LinAlgError("Матриця вироджена")  

        #A loop for making zeros
        for i in range(k+1, n):
            koef = a[i][k] / a[k][k]
            b[i] -= koef*b[k]
            a[i][k:n] = a[i][k:n] - koef * a[k][k:n]      
            
        # Determinant calculating
        if a[k][k] < 0:
            sign *= -1
            logdet += np.log(abs(a[k][k]))
        else:
            logdet += np.log(a[k][k])
    
    # Substitution
    for i in range(n-1, -1, -1):
        if a[i][i] == 0: raise np.linalg.LinAlgError("Матриця вироджена")
        x[i] = (b[i] - np.dot(a[i][i+1:n], x[i+1:n]))/a[i][i]
        
    # Reordering the result
    result = np.empty_like(x)
    for i in range(n):
        result[col_order[i]] = x[i]
    return result, (sign , logdet)
        





