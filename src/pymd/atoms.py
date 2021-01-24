import numpy as np

from pymd.element import Element, gen_element
from pymd.util import gen_cubic_grid, xyz_in, xyz_out

# TODO Element to Array of Element, then pass parameters to forcepoly


class Atoms:

    def __init__(self, N: int, rho: float, elem: Element, r: np.ndarray = None,
                 v: np.ndarray = None, removedrift: bool = True):
        self.N = N
        self.rho = rho
        self.L = np.cbrt(self.N/self.rho)
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
        # Assign particle positions on the grid
        grid = gen_cubic_grid(self.N)
        self.r = np.array(grid[:self.N]*self.L, dtype=np.float64)

    def set_v_random(self):
        # Assign random velocities
        self.v = np.array(np.random.exponential(size=(self.N, 3)),
                          dtype=np.float64)

    def remove_v_drift(self):
        # Take away any center-of-mass drift
        self.v -= np.mean(self.v, axis=0)

    def write_xyz(self, filename, append=False, put_vel=True, unfold=False):
        mode = "a" if append else "w"
        with open(filename, mode) as f:
            xyz_out(f, self.r, self.v, self.i, self.L, elem=self.elem.name,
                    put_vel=put_vel, unfold=unfold)


def fromfile(rho: float, init_cfg_file: str, **kwargs):
    with open(init_cfg_file, "r") as f:
        next(f)
        next(f)
        elemstr = next(f).split()[0]
    elem = gen_element(elemstr)
    with open(init_cfg_file, 'r') as f:
        N, r, v = xyz_in(f)
    return Atoms(N, rho, elem, r, v, **kwargs)
