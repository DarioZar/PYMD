cimport cython

import numpy as np

from cython.parallel import parallel, prange

cimport numpy as np
from libc.math cimport sqrt


cdef double bc(double dx, double bound) nogil:
    """
    Applies periodic boundary condition.

    Args:
        dx (double): val to apply the boundary
        bound (double): boundary

    Returns:
        double: val after applying the boundary condition
    """
    if dx>bound/2:
        dx-=bound
    elif dx<-bound/2:
        dx+=bound
    return dx

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def calc_hist(double[:,:] r, double L, double rc, double dr):
    """
    N^2 algorithm for computing interparticle separations in parallel
    and updating the radial distribution function histogram.

    Args:
        r (double[N,3]): array of vector positions
        L (double): dimension of box
        rc (double): cutoff distance
        dr (double): length of bin
    """
    cdef:
        int i,j
        int N = r.shape[0]
        int nbins = <int>(rc/dr) + 1
        double dx,dy,dz,modr
        np.ndarray[int, ndim=1] H = np.zeros(nbins, dtype=np.int)

    # Now, thread safe by separation of memory
    cdef:
        int num_threads = openmp.omp_get_max_threads()
        int tid
        int[:,:] H_local = np.zeros((num_threads,nbins), dtype=np.int)


    with nogil, parallel(num_threads=num_threads):
        # Pair interaction loop
        for i in prange(0,N-1, schedule="static", chunksize=50):
            tid = openmp.omp_get_thread_num()
            for j in range(i+1,N):
                # Calc dr
                dx = (r[i,0]-r[j,0])
                dy = (r[i,1]-r[j,1])
                dz = (r[i,2]-r[j,2])
                # Periodic boundary conditions
                dx=bc(dx,L)
                dy=bc(dy,L)
                dz=bc(dz,L)
                modr = sqrt(dx*dx + dy*dy + dz*dz)
                # Consider interaction only if r<r_{cutoff}
                if modr<rc
                    bin = <int>(modr/dr)
                    H_local[tid,bin] += 2
    # Sum thread values to get total histogram
    for tid in range(num_threads):
        for i in range(0,nbins):
            H[i] += H_local[i,tid]
    return H