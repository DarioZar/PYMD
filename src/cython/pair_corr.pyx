cimport cython
import numpy as np
cimport numpy as np
from libc.math cimport sqrt


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def calc_hist(double[:,:] r, double L, double rc, double dr):
    """
    N^2 algorithm for computing interparticle separations
    and updating the radial distribution function histogram.

    Args:
        r (double[N,3]): array of vector positions
        L (double): dimension of box
        rc (double): cutoff distance
        dr (double): length of bin
    """
    cdef:
        size_t i,j
        int N = r.shape[0]
        int nbins = <int>(rc/dr) + 1
        double dx,dy,dz,modr
        np.ndarray[int, ndim=1] H = np.zeros(nbins, dtype=np.int)

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
            modr = sqrt(dx*dx + dy*dy + dz*dz)
            # Consider interaction only if r<r_{cutoff}
            if modr<rc:
                bin = <int>(modr/dr)
                H[bin]+=2
    return H


