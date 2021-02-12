from typing import TextIO, Tuple

import numpy as np


def xyz_in(file: TextIO) -> Tuple[int, np.ndarray, np.ndarray, np.ndarray]:
    """
    Read and parse .xyz file to array of position and velocity vectors.

    Args:
        file (TextIO): file stream

    Returns:
        Tuple[int, np.ndarray, np.ndarray, np.ndarray]: N of atoms, r, v arrays
    """
    # Read first row for N and has_vel
    N, has_vel = [int(i) for i in next(file).split()]
    # If has velocities, read, else generate random
    if has_vel:
        dtypeERV = {
            "names": ("elemstr", "rx", "ry", "rz", "vx", "vy", "vz"),
            "formats": (
                "|U2",
                np.float64,
                np.float64,
                np.float64,
                np.float64,
                np.float64,
                np.float64,
            ),
        }
        data = np.loadtxt(
            file,
            usecols=(0, 1, 2, 3, 4, 5, 6),
            max_rows=N,
            dtype=dtypeERV,
            unpack=True,
        )
        elems = data[0]
        r = np.array(data[1:4]).T
        v = np.array(data[4:]).T
    else:
        dtypeER = {
            "names": ("elemstr", "rx", "ry", "rz"),
            "formats": ("|U2", np.float64, np.float64, np.float64),
        }
        data = np.loadtxt(
            file, usecols=(0, 1, 2, 3), max_rows=N, dtype=dtypeER, unpack=True
        )
        elems = data[0]
        r = np.array(data[1:4]).T
        v = np.random.exponential(size=(N, 3), dtype=np.float64)
    # Return positions and velocities
    return N, elems, r, v


def xyz_out(
    datafile: TextIO,
    r: np.ndarray,
    v: np.ndarray,
    i: np.ndarray,
    L: float,
    elem: str = "Ar",
    put_vel: bool = True,
    unfold: bool = False,
):
    """
    Outputs array of position and velocity vectors to file in .xyz format

    Args:
        datafile (TextIO): file stream
        r (np.ndarray): array of position vectors
        v (np.ndarray): array of velocity vectors
        i (np.ndarray): array of periodic boundary crossing vectors
        L (float): box dimension
        elem (str, optional): atomic specie. Defaults to "Ar".
        put_vel (bool, optional): choice if put velocities in .xyz file.
                                  Defaults to True.
        unfold (bool, optional): choice to unfold the coordinates, the unfolded
                                 coordinate is r[i]+i[i]*L. Defaults to False.
    """
    # Get N of particles
    N = r.shape[0]
    # Unfold positions
    data = r + i * L if unfold else r
    # Put velocities
    data = np.hstack([data, v]) if put_vel else data
    # Save the file using numpy fast function
    formatstr = elem + data.shape[1] * " %.8f"
    np.savetxt(
        datafile,
        data,
        fmt=formatstr,
        header="{} {}\n".format(N, int(put_vel)),
        comments="",
    )


def gen_cubic_grid(N: int) -> np.ndarray:
    """
    Generate the smallest cubic grid housing N particles,
    unitary length of the cube

    Args:
        N (int): number of points

    Returns:
        np.ndarray: cubic grid
    """
    # Find the lowest perfect cube, n3, greater than or equal to the
    # number of particles
    n3 = int(np.ceil(N ** (1 / 3)))
    # Create the cubic grid
    x, y, z = np.mgrid[0:n3, 0:n3, 0:n3]
    # Return the grid as n3**3 vectors, center points of grid elements
    # N.B USO ORDINE INVERSO, PER ORA, PER COMPATIBILITA
    grid = np.array([z, y, x]).reshape(3, n3 ** 3).T
    return (grid + 0.5) / n3
