import numpy as np
from pymd.molecule import Molecule
from pymd.util import xyz_in, gen_cubic_grid, xyz_out


#TODO Molecule to Array of Molecule, then pass parameters to forcepoly

class Atoms:

    def __init__(self, N: int, rho: float, mol: Molecule,
                 init_cfg_file: str = None):
        self.N = N
        self.rho = rho
        self.L = np.cbrt(self.N/self.rho)
        self.mol = mol
        if(init_cfg_file):
            self.set_r_v_fromfile(init_cfg_file)
        else:
            self.set_r_v_cubicgrid()
        self.remove_v_drift()
        self.i = np.zeros((self.N, 3), dtype=np.int16)

    def set_r_v_cubicgrid(self):
        # Assign particle positions on the grid
        grid = gen_cubic_grid(self.N)
        self.r = np.array(grid[:self.N]*self.L, dtype=np.float64)
        # Assign random velocities
        self.v = np.array(np.random.exponential(size=(self.N, 3)), dtype=np.float64)

    def set_r_v_fromfile(self, init_cfg_file: str):
        with open(init_cfg_file, 'r') as f:
            self.r, self.v = xyz_in(f)

    def remove_v_drift(self):
        # Take away any center-of-mass drift; compute initial KE
        self.v -= np.mean(self.v, axis=0)
    
    def write_xyz(self, filename, append=False, put_vel=True, unfold=False):
        mode = "ab" if append else "w"
        with open(filename, mode) as f:
            xyz_out(f, self.r, self.v, self.i, self.L, elem=self.mol.name,
                    put_vel=put_vel, unfold=unfold)
