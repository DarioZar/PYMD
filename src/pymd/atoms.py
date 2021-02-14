from __future__ import annotations

from copy import deepcopy
from typing import Any, List

import numpy as np
from nptyping import NDArray

from pymd.element import Element, gen_element
from pymd.pair_corr import calc_hist
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
        r (NDArray): positions array
        v (NDArray): velocities array
        i (NDArray): box crossing counter array
    """

    def __init__(
        self,
        N: int,
        rho: float,
        elem: Element,
        r: NDArray = None,
        v: NDArray = None,
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
            r (NDArray, optional): array of positions. Defaults to None.
            v (NDArray, optional): array of velocities. Defaults to None.
            removedrift (bool, optional): if True, puts to zero the velocity of
                the center of mass. Defaults to True.
        """
        self.N = N
        self.rho = rho
        self.L = np.cbrt(self.N / self.rho)
        self.elem = elem
        if r is None:
            self.set_r_cubicgrid()
        else:
            self.r = r
        if v is None:
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

    def copy(self) -> Atoms:
        return deepcopy(self)


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
        N, elems, r, v = xyz_in(f)
    elem = gen_element(elems[0])
    return Atoms(N, rho, elem, r, v, **kwargs)


def atomslist_fromfile(
    rho: float, init_cfg_file: str, **kwargs
) -> List[Atoms]:
    """
    Generates list of Atoms object from .xyz file.

    Args:
        rho (float): density of atoms
        init_cfg_file (str): filename of .xyz file

    Returns:
        List[Atoms]: List of Atoms objects
    """
    atomslist = []
    with open(init_cfg_file, "r") as f:
        N = int(next(f).split()[0])
        lines = sum(1 for line in f) + 1
    steps = lines // (N + 2)
    with open(init_cfg_file, "r") as f:
        for s in range(steps):
            N, elems, r, v = xyz_in(f)
            elem = gen_element(elems[0])
            atomslist.append(Atoms(N, rho, elem, r, v, **kwargs))
    return atomslist


def pair_correlation(
    atomslist: List[Atoms], rc: float, dr: float
) -> NDArray[(2, Any), float]:
    """
    Calculate pair correlation function from a list of Atoms
    objects.

    Args:
        atomslist (List[Atoms]): list of atoms objects to use as sample
        rc (float): cutoff radius for pair interaction
        dr (float): size of bin

    Returns:
        NDArray[(2, Any), float]: pair correlation function as (r, g(r)) array
    """
    # Calc number of bins and create histogram
    nbins = int(rc / dr) + 1
    hist = np.zeros(nbins, dtype=int)
    # Update histogram using a cython method
    for atoms in atomslist:
        hist += calc_hist(atoms.r, atoms.L, rc, dr)
    # Normalize the histogram
    ngr = len(atomslist)
    N = atomslist[0].N
    rho = atomslist[0].rho
    bins = np.arange(nbins)
    vb = ((bins + 1) ** 3 - bins ** 3) * (dr ** 3)
    g = hist / ((4 / 3) * np.pi * vb * rho * N * ngr)
    # Calc positions of bins
    r = dr * (bins + 0.5)
    # Return array (r,g(r))
    return np.array([r, g])
