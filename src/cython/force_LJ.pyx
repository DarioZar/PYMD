cimport cython
import numpy as np
cimport numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
def force(double[:,:] r, double L, double rc, double ecor, double ecut):
    """
    N^2 algorithm for computing forces, potential energy and virial.

    Args:
        r (double[N,3]): array of vector positions
        L (double): dimension of box
        rc (double): cutoff distance
        ecor (double): energy correction
        ecut (double): energy after cutoff
    """
    cdef:
        size_t i,j
        int N = r.shape[0]
        double rc2 = rc*rc
        double r3,r6i,modf,dx,dy,dz,r2
        double e=0,vir=0
        np.ndarray[double,ndim=2] f = np.zeros((N,3), dtype=np.float64)

    # Pair interaction loop
    for i in range(0,N-1):
        for j in range(i+1,N):
            # Calc dr
            dx = (r[i,0]-r[j,0])
            dy = (r[i,1]-r[j,1])
            dz = (r[i,2]-r[j,2])

            # Periodic boundary conditions
            if dx>L/2:
                dx-=L
            elif dx<-L/2:
                dx+=L
            if dy>L/2:
                dy-=L
            elif dy<-L/2:
                dy+=L
            if dz>L/2:
                dz-=L
            elif dz<-L/2:
                dz+=L

            r2 = dx*dx + dy*dy + dz*dz

            # Consider interaction only if r^2<r_{cutoff}^2 
            if r2<rc2:
                r6i = 1/(r2*r2*r2)
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