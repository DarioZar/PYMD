# import json
from typing import List, Tuple, Union

import numpy as np

from pymd.atoms import Atoms
from pymd.force_LJ import force


# TODO: correct simulate for optional s
# TODO: add force object to generalize
# TODO: add thermostat object to generalize
class NVEState:
    """
    Defines a microcanonical ensemble of atoms, in normal units.

    Attributes:
        time (float):  time of simulation
        atoms (Atoms): Atoms object, with information about element, positions,
            velocities, box length, box crossing
        rc (float): Cutoff radius
        corr (Dict[str,float]): dictionary with energy at cutoff,
            energy correction, potential correction
        f (np.ndarray): array of forces on particles
        T (float): temperature
        PE (float): potential energy
        KE (float): kinetic energy
        TE (float): total energy
        TEO (float): total energy at time=0
        drift (float): energy drift from the start ((TE-TE0)/TE0)
        P (float): pressure
    """

    def __init__(
        self,
        atoms: Atoms,
        T0: float,
        rc: float,
        use_e_corr: bool = False,
    ):
        """
        Initialize NVEState object.

        Args:
            atoms (Atoms): Atoms object
            T0 (float): Initial temperature of state
            rc (float): Cutoff radius for force calculation
            use_e_corr (bool, optional): Use energy corrections.
                Defaults to False.

        Raises:
            ValueError: If cutoff radius is greater than half box length
        """
        self.time = 0.0
        self.atoms = atoms
        self.rc = rc
        if self.rc > self.atoms.L / 2:
            raise ValueError(
                "Cutoff radius can't be greater than half box length"
            )
        # Calc forces, potential energy, virial term
        # using the chosen potential
        self.corr = {"ecut": 0.0, "ecorr": 0.0, "pcorr": 0.0}
        corr = self.corrections(self.rc, self.atoms.rho, use_e_corr)
        self.corr["ecut"] = corr[0]
        self.corr["ecorr"] = corr[1]
        self.corr["pcorr"] = corr[2]
        self.f, self.PE, vir = self.calc_force_PE()
        if T0 > 0:
            self.KE = 0.5 * np.sum(self.atoms.v * self.atoms.v)
            self.T = self.KE * 2 / 3.0 / self.atoms.N
            self.atoms.v *= np.sqrt(T0 / self.T)
        self.calc_vars(vir)

    def step(self, dt: float):
        """
        Simulation step. Brings state to time+dt using a
        velocity verlet integration algorithm.

        Args:
            dt (float): timestep
        """
        self.time += dt
        # First integration half-step
        self.atoms.v += 0.5 * dt * self.f
        self.atoms.r += self.atoms.v * dt
        # Apply periodic boundary conditions
        self.atoms.r[self.atoms.r > self.atoms.L] -= self.atoms.L
        self.atoms.i[self.atoms.r > self.atoms.L] += 1
        self.atoms.r[self.atoms.r < 0] += self.atoms.L
        self.atoms.i[self.atoms.r < 0] -= 1

        # Calculate forces
        self.f, self.PE, vir = self.calc_force_PE()

        # Second integration half-step
        self.atoms.v += 0.5 * dt * self.f
        self.calc_vars(vir)

    def simulate(
        self,
        s: int,
        dt: Union[np.ndarray, float],
        fSamp: int,
        unfold: bool = False,
        append: bool = True,
        filename: str = None,
    ) -> Tuple[np.ndarray, List[Atoms]]:
        """
        Simulate for a given number of timesteps, saving the position
        and velocities as Atoms objects in a List. If a filename is given,
        a .xyz file is generated, with frequency fSamp, with positions
        and velocities.

        Args:
            s (int): number of timesteps
            dt (Union[np.ndarray, float]): timestep or array of timesteps.
                if the shape of the array is not (s,), defauolts timestep to
                the first element of the array
            fSamp (int): sampling frequency of .xyz output
            unfold (bool, optional): if True, unfolds coordinates to
                r+i*L, accounting for particles leaving the box.
                Defaults to False.
            append (bool, optional): if True, save a single .xyz file.
                Defaults to True.
            filename (str, optional): filename of .xyz file, without the
                extension.

        Returns:
            np.ndarray: output array with all the state variables, as
                [time, KE, PE, TE, drift, T, P]
            List[Atoms]: snapshots of the atoms, sample frequency fSamp
        """
        # Creates array of timesteps
        dt = np.array(dt)
        if dt.shape != s:
            dt = np.ones(s) * dt.item(0)
        # Creates output array and output list
        output = np.empty((s, len(self.vars_output())))
        output[0] = self.vars_output()
        atomsOutput = [self.atoms]
        # If a filename is given, writes .xyz output
        if filename is not None:
            self.atoms.write_xyz(filename + "_0.xyz")
        # Simulation loop
        for i in range(1, s):
            # Step
            self.step(dt[i])
            # Save all variables
            output[i] = self.vars_output()
            if i % fSamp == 0:
                atomsOutput += [self.atoms]
                if filename is not None:
                    if append:
                        self.atoms.write_xyz(filename + "_0.xyz", append=True)
                    else:
                        self.atoms.write_xyz(filename + f"_{i}.xyz")
        return output, atomsOutput

    def corrections(
        self, rc: float, rho: float, use_e_corr: bool
    ) -> Tuple[float, float, float]:
        """
        Computes the tail-corrections of a Lennard Jones potential, in
        normal units.

        Args:
            rc (float): Cutoff radius
            rho (float): density of particles
            use_e_corr (bool): if True, computes energy and potential
                corrections.

        Returns:
            Tuple[float, float, float]: energy at cutoff, energy correction,
                potential correction
        """
        rr3 = 1 / rc ** 3
        ecor = (
            8 * np.pi * rho * ((rr3 ** 3) / 9 - rr3 / 3) if use_e_corr else 0
        )
        pcor = (
            16 / 3 * np.pi * (rho ** 2) * (2 / 3 * (rr3 ** 3) - rr3)
            if use_e_corr
            else 0
        )
        ecut = 4 * (rr3 ** 4 - rr3 ** 2)
        return ecut, ecor, pcor

    def calc_force_PE(self) -> Tuple[np.ndarray, float, float]:
        """
        Computes force, potential energy and virial term using the
        imported extension.

        Returns:
            Tuple[np.ndarray, float, float]: array of forces, potential
                energy, virial term
        """
        return force(
            self.atoms.r,
            self.atoms.L,
            self.rc,
            self.corr["ecorr"],
            self.corr["ecut"],
        )

    def vars_output(self) -> np.ndarray:
        """
        Outputs all the state variables.

        Returns:
            np.ndarray: output array with all the state variables, as
                [time, KE, PE, TE, drift, T, P]
        """
        return np.array(
            [self.time, self.KE, self.PE, self.TE, self.drift, self.T, self.P]
        )

    def calc_vars(self, vir: float):
        """
        Calculate the state variables.

        Args:
            vir (float): virial term, used to calculate pressure
        """
        self.KE = 0.5 * np.sum(self.atoms.v * self.atoms.v)
        self.T = self.KE * 2 / 3.0 / self.atoms.N
        self.TE = self.PE + self.KE
        if self.time == 0:
            self.TE0 = self.TE
        self.drift = (self.TE - self.TE0) / self.TE0
        self.P = (
            self.atoms.rho * self.KE * 2.0 / 3.0 / self.atoms.N
            + vir / 3.0 / (self.atoms.N / self.atoms.rho)
        )


class NVTAndersenState(NVEState):
    """
    Defines a canonical ensemble of atoms, in normal units, extending
    NVEState and adding an Andersen Stochastic Thermostat.

    Attributes:
        Tbath (float): thermostat temperature
        nu (float): thermostat frequency
    """

    def __init__(
        self,
        atoms: Atoms,
        T0: float,
        Tbath: float,
        nu: float,
        rc: float,
        use_e_corr: bool = False,
    ):
        """
        Initialize NVTAndersenState object.

        Args:
            Tbath (float): [description]
            nu (float): [description]
        """
        super().__init__(atoms, T0, rc, use_e_corr)
        self.Tbath = Tbath
        self.nu = nu

    def step(self, dt: float):
        """
        Simulation step. Brings state to time+dt using a
        velocity verlet integration algorithm and uses an
        Andersen thermostat.

        Args:
            dt (float): timestep
        """
        self.time += dt
        # First integration half-step
        self.atoms.v += 0.5 * dt * self.f
        self.atoms.r += self.atoms.v * dt
        # Apply periodic boundary conditions
        self.atoms.r[self.atoms.r > self.atoms.L] -= self.atoms.L
        self.atoms.i[self.atoms.r > self.atoms.L] += 1
        self.atoms.r[self.atoms.r < 0] += self.atoms.L
        self.atoms.i[self.atoms.r < 0] -= 1

        # Calculate forces
        self.f, self.PE, vir = self.calc_force_PE()

        # Andersen Thermostat
        chance = np.random.uniform(size=self.atoms.N) < self.nu * dt
        self.atoms.v[chance] = np.random.normal(
            scale=np.sqrt(self.Tbath), size=(np.count_nonzero(chance), 3)
        )

        # Second integration half-step
        self.atoms.v += 0.5 * dt * self.f
        self.calc_vars(vir)


# TODO: input json to get a State object.
def state_from_JSON(file):
    pass


def available_statistics() -> List[str]:
    """
    List of available statistics. May remove it later.

    Returns:
        List[str]: list of available state classes.
    """
    stats = ["NVE", "NVT (Andersen)"]
    return stats
