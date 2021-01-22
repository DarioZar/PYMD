import numpy as np
import json
from typing import Union
from pymd.atoms import Atoms
from pymd.util import xyz_in, gen_cubic_grid
from pymd.force_LJ import force


class NVEState:

    def __init__(self, atoms: Atoms, T0: float, rc: float = 3.5,
                 use_e_corr: bool = False):
        self.time = 0
        self.atoms = atoms
        self.rc = rc
        # Calc forces, potential energy, virial term
        # using the chosen potential
        self.corr = {'ecut': 0, 'ecorr': 0, 'pcorr': 0}
        self.corr['ecut'], self.corr['ecorr'], self.corr['pcorr'] = self.corrections(
            self.rc, self.atoms.rho, use_e_corr)
        self.f, self.PE, vir = self.calc_force_PE()
        if T0 > 0:
            self.KE = 0.5*np.sum(self.atoms.v*self.atoms.v)
            self.T = self.KE*2/3./self.atoms.N
            self.atoms.v *= np.sqrt(T0/self.T)
        self.calc_vars(vir)

    def step(self, dt: float):
        self.time += dt
        # First integration half-step
        self.atoms.v += 0.5*dt*self.f
        self.atoms.r += self.atoms.v*dt
        # Apply periodic boundary conditions
        self.atoms.r[self.atoms.r > self.atoms.L] -= self.atoms.L
        self.atoms.i[self.atoms.r > self.atoms.L] += 1
        self.atoms.r[self.atoms.r < 0] += self.atoms.L
        self.atoms.i[self.atoms.r < 0] -= 1

        # Calculate forces
        self.f, self.PE, vir = self.calc_force_PE()

        # Second integration half-step
        self.atoms.v += 0.5*dt*self.f
        self.calc_vars(vir)

    def simulate(self, s: int, dt: Union[np.ndarray, float], fSamp: int,
                 unfold: bool = False, append=True) -> np.ndarray:
        dt = np.array(dt)
        if dt.shape != s:
            dt = np.ones(s)*dt.item(0)
        output = np.empty((s, len(self.vars_output())))
        output[0] = self.vars_output()
        self.atoms.write_xyz("0.xyz")
        for i in range(1, s):
            self.step(dt[i])
            output[i] = self.vars_output()
            # debug

            '''if s % fSamp:
                if append:
                    self.atoms.write_xyz("0.xyz", append=True)
                else:
                    self.atoms.write_xyz(f"{s}.xyz")'''
        return output

    def corrections(self, rc: float, rho: float, use_e_corr: bool) -> (float, float, float):
        # Compute the tail-corrections; assumes sigma and epsilon are both 1
        rr3 = 1/rc**3
        ecor = 8*np.pi*rho*((rr3**3)/9 - rr3/3) if use_e_corr else 0
        pcor = 16/3*np.pi*(rho**2)*(2/3*(rr3**3) - rr3) if use_e_corr else 0
        ecut = 4*(rr3**4 - rr3**2)
        return ecut, ecor, pcor

    def calc_force_PE(self):
        return force(self.atoms.r, self.atoms.L, self.rc,
                     self.corr['ecorr'], self.corr['ecut'])

    def vars_output(self):
        return np.array([self.time, self.KE, self.PE, self.TE, self.drift, self.T, self.P])

    def calc_vars(self, vir: float):
        self.KE = 0.5*np.sum(self.atoms.v*self.atoms.v)
        self.T = self.KE*2/3./self.atoms.N
        self.TE = self.PE + self.KE
        if self.time == 0:
            self.TE0 = self.TE
        self.drift = (self.TE-self.TE0)/self.TE0
        self.P = self.atoms.rho*self.KE*2./3./self.atoms.N + \
            vir/3.0/(self.atoms.N/self.atoms.rho)


class NVTAndersenState(NVEState):

    def __init__(self, atoms: Atoms, T0: float, Tbath: float,
                 nu: float, rc: float = 3.5, use_e_corr: bool = False, ):
        super().__init__(atoms, T0, rc, use_e_corr)
        self.Tbath = Tbath
        self.nu = nu

    def step(self, dt: float):
        self.time += dt
        # First integration half-step
        self.atoms.v += 0.5*dt*self.f
        self.atoms.r += self.atoms.v*dt
        # Apply periodic boundary conditions
        self.atoms.r[self.atoms.r > self.atoms.L] -= self.atoms.L
        self.atoms.i[self.atoms.r > self.atoms.L] += 1
        self.atoms.r[self.atoms.r < 0] += self.atoms.L
        self.atoms.i[self.atoms.r < 0] -= 1

        # Calculate forces
        self.f, self.PE, vir = self.calc_force_PE()

        # Andersen Thermostat
        chance = np.random.uniform(size=self.atoms.N) < self.nu*dt
        self.atoms.v[chance] = np.random.normal(scale=np.sqrt(self.Tbath),
                                                size=(np.count_nonzero(chance), 3))

        # Second integration half-step
        self.atoms.v += 0.5*dt*self.f
        self.calc_vars(vir)

def state_from_JSON(file):
    pass