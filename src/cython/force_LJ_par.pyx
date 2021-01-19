#setuptools:  extra_compile_args=-fopenmp
#setuptools:  extra_link_args=-fopenmp
cimport cython
from cython.parallel import prange
import numpy as np
cimport numpy as np

cdef float bc(float dx, float bound) nogil:
    if dx>bound/2:
        dx-=bound
    elif dx<-bound/2:
        dx+=bound
    return dx


@cython.boundscheck(False)
@cython.wraparound(False)
def force_LJ_par(np.float_t[:,:] r, double L, double rc2, double ecor, double ecut):
    """
    N^2 algorithm for computing forces, potential energy and virial.

    :param double[N,3] r: array of vector positions
    :param double L: dimension of box
    :param double rc2: cutoff distance squared
    :param double ecor: energy correction
    :param double ecut: energy after cutoff
    """
    cdef:
        int i,j
        int N = r.shape[0]
        double r3,r6i, modf,dx,dy,dz,r2
        double e=0,vir=0
        np.ndarray[np.float_t,ndim=2] f = np.zeros((N,3), dtype=np.float)
    
    # Pair interaction loop, parallelized over i using parallel range
    for i in prange(0,N-1, nogil=True):
        for j in range(i+1,N):
            dx = (r[i,0]-r[j,0])
            dy = (r[i,1]-r[j,1])
            dz = (r[i,2]-r[j,2])

            # Periodic boundary conditions
            dx=bc(dx,L)
            dy=bc(dy,L)
            dz=bc(dz,L)
            
            r2 = dx*dx + dy*dy + dz*dz
            # Consider interaction only if r^2<r_{cutoff}^2 
            if r2<rc2:
                r6i = 1./(r2*r2*r2)
                e += 4 * (r6i * r6i - r6i) - ecut
                modf = 48 * (r6i * r6i - 0.5 * r6i)
                f[i,0] += modf*dx/r2
                f[j,0] -= modf*dx/r2
                f[i,1] += modf*dy/r2
                f[j,1] -= modf*dy/r2
                f[i,2] += modf*dz/r2
                f[j,2] -= modf*dz/r2
                vir += modf
    return f, e+N*ecor, vir