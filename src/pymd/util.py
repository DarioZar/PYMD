import numpy as np
from typing import TextIO


def xyz_in(file: TextIO) -> (np.ndarray, np.ndarray):
    """
    Read and parse .xyz file to array of position and velocity vectors.

    :param TextIO file: file stream
    :return (np.ndarray, np.ndarray): r, v arrays
    """
    # Read first row for N and has_vel
    N, has_vel = [int(i) for i in next(file).split()]
    # If has velocities, read, else generate random
    if(has_vel):
        data = np.loadtxt(f, usecols=(1, 2, 3, 4, 5, 6),
                          max_rows=N, dtype=np.float64)
        r = data[:, :3]
        v = data[:, 3:]
    else:
        data = np.loadtxt(f, usecols=(1, 2, 3), max_rows=N, dtype=np.float64)
        r = data
        v = np.random.exponential(size=(N, 3), dtype=np.float64)
    # Return positions and velocities
    return r, v


def xyz_out(datafile: TextIO, r: np.ndarray, v: np.ndarray, i: np.ndarray,
            L: float, elem: str ='Ar', put_vel: bool = True, unfold: bool = False):
    """
    Outputs array of position and velocity vectors to file in .xyz format

    :param TextIO file: file stream
    :param np.ndarray r: array of position vectors
    :param np.ndarray v: array of velocity vectors
    :param np.ndarray i: array of periodic boundary crossing vectors
    :param double L: box dimension
    :param double z: atomic number of specie
    :param bool put_vel: choice if put velocities in .xyz file
    :param bool unfold: choice to unfold the coordinates, the unfolded coordinate is
                        r[i]+i[i]*L
    """
    # Get N of particles
    N = r.shape[0]
    # Unfold positions
    data = r+i*L if unfold else r
    # Put velocities
    data = np.hstack([data, v]) if put_vel else data
    # Save the file using numpy fast function
    formatstr = elem + data.shape[1]*" %.8f"
    np.savetxt(datafile, data, fmt=formatstr,
               header="{} {}\n".format(N, int(put_vel)), comments="", footer="\n")


def gen_cubic_grid(N: int) -> np.ndarray:
    """
    Generate the smallest cubic grid housing N particles,
    unitary length of the cube

    :param int N: number of points
    :returns np.ndarray: cubic grid
    """
    # Find the lowest perfect cube, n3, greater than or equal to the
    # number of particles
    n3 = int(np.ceil(np.cbrt(N)))
    # Create the cubic grid
    x, y, z = np.mgrid[0:n3, 0:n3, 0:n3]
    # Return the grid as n3**3 vectors, center points of grid elements
    # N.B USO ORDINE INVERSO, PER ORA, PER COMPATIBILITA
    grid = np.array([z, y, x]).reshape(3, n3**3).T
    return (grid+0.5)/n3
