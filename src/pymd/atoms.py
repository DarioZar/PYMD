import numpy as np

from pymd.element import Element, gen_element
from pymd.util import gen_cubic_grid, xyz_in, xyz_out


# TODO Element to Array of Element, then pass parameters to forcepoly
class Atoms:
    """
    Atoms object, contains informations about number of atoms, density,
    element, positions, velocities

    Attributes:
        N (int): number of atoms
        rho (float): density of atoms
        elem (Element): Element object of atoms
        L (float): box length
        r (np.ndarray): positions array
        v (np.ndarray): velocities array
        i (np.ndarray): box crossing counter array
    """

    def __init__(
        self,
        N: int,
        rho: float,
        elem: Element,
        r: np.ndarray = None,
        v: np.ndarray = None,
        removedrift: bool = True,
    ):
        """
        Initialize Atoms object. If positions are not given, defaults to
        the smallest cubic grid; if velocities are not given, generates
        random velocities from a normalized exponential distribution;
        if removedrift is set to False, does not put the velocity of the
        center of mass to zero.

        Args:
            N (int): number of atoms
            rho (float): density of atoms
            elem (Element): Element object of atoms
            r (np.ndarray, optional): array of positions. Defaults to None.
            v (np.ndarray, optional): array of velocities. Defaults to None.
            removedrift (bool, optional): if True, puts to zero the velocity of
                the center of mass. Defaults to True.
        """
        self.N = N
        self.rho = rho
        self.L = np.cbrt(self.N / self.rho)
        self.elem = elem
        if not r:
            self.set_r_cubicgrid()
        else:
            self.r = r
        if not v:
            self.set_v_random()
        else:
            self.v = v
        if removedrift:
            self.remove_v_drift()
        self.i = np.zeros((self.N, 3), dtype=np.int16)

    def set_r_cubicgrid(self):
        """
        Assign particle positions on the smallest cubic grid
        """
        grid = gen_cubic_grid(self.N)
        self.r = np.array(grid[: self.N] * self.L, dtype=np.float64)

    def set_v_random(self):
        """
        Assign random velocities from a normalized exponential distribution
        """
        self.v = np.array(
            np.random.exponential(size=(self.N, 3)), dtype=np.float64
        )

    def remove_v_drift(self):
        """
        Take away any center-of-mass drift
        """
        self.v -= np.mean(self.v, axis=0)

    def write_xyz(
        self,
        filename: str,
        append: bool = False,
        put_vel: bool = True,
        unfold: bool = False,
    ):
        """
        Saves atoms informations on a .xyz file.

        Args:
            filename (str): filename of the .xyz file
            append (bool, optional): if True, appends to an existing file.
                Defaults to False.
            put_vel (bool, optional): if True, puts velocities into the file.
                Defaults to True.
            unfold (bool, optional): if True, unfolds the coordinates as r+i*L.
                Defaults to False.
        """
        with open(filename, "a" if append else "w") as f:
            xyz_out(
                f,
                self.r,
                self.v,
                self.i,
                self.L,
                elem=self.elem.name,
                put_vel=put_vel,
                unfold=unfold,
            )

    def gr(self) -> np.ndarray:
        pass


def fromfile(rho: float, init_cfg_file: str, **kwargs) -> Atoms:
    """
    Generates Atoms object from .xyz file.

    Args:
        rho (float): density of atoms
        init_cfg_file (str): filename of .xyz file

    Returns:
        Atoms: Atoms object
    """
    with open(init_cfg_file, "r") as f:
        next(f)
        next(f)
        elemstr = next(f).split()[0]
    elem = gen_element(elemstr)
    with open(init_cfg_file, "r") as f:
        N, r, v = xyz_in(f)
    return Atoms(N, rho, elem, r, v, **kwargs)
