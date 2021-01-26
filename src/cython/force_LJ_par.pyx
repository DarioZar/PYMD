cimport cython

from cython.parallel import parallel, prange

cimport openmp

import numpy as np

cimport numpy as np


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
        int i,j
        int N = r.shape[0]
        double rc2 = rc*rc
        double r3,r6i, modf,dx,dy,dz,r2
        double e=0,vir=0
        np.ndarray[double,ndim=2] f = np.zeros((N,3), dtype=np.float64)
    
    # Pair interaction loop, parallelized over i using parallel range
    # attenzione ad aggiornare valori dentro prange!
    # stackoverflow.com/questions/42281886/cython-make-prange-parallelization-thread-safe
    num_threads = openmp.omp_get_max_threads()
    cdef:
        int tid
        int N_padded = (((N-1)//8)+1)*8
        double[:] fx_local  = np.zeros(N_padded*num_threads, dtype=np.float64)
        double[:] fy_local  = np.zeros(N_padded*num_threads, dtype=np.float64)
        double[:] fz_local  = np.zeros(N_padded*num_threads, dtype=np.float64)
        double[:] e_local   = np.zeros(num_threads, dtype=np.float64)
        double[:] vir_local = np.zeros(num_threads, dtype=np.float64)
    
    with nogil, parallel(num_threads=num_threads):
        for i in prange(0, N-1, schedule="static", chunksize=50):
            tid = openmp.omp_get_thread_num()
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
                    e_local[tid] += 4 * (r6i * r6i - r6i) - ecut
                    modf = 48 * (r6i * r6i - 0.5 * r6i)
                    fx_local[tid*N_padded + i] += modf*dx/r2
                    fx_local[tid*N_padded + j] -= modf*dx/r2
                    fy_local[tid*N_padded + i] += modf*dy/r2
                    fy_local[tid*N_padded + j] -= modf*dy/r2
                    fz_local[tid*N_padded + i] += modf*dz/r2
                    fz_local[tid*N_padded + j] -= modf*dz/r2
                    vir_local[tid] += modf
    for tid in range(num_threads):
        e   += e_local[tid]
        vir += vir_local[tid]
        for i in range(0,N):
            f[i,0] += fx_local[tid*N_padded+i]
            f[i,1] += fy_local[tid*N_padded+i]
            f[i,2] += fz_local[tid*N_padded+i]

    return f, e+N*ecor, vir