import json
from typing import Callable, List

import numpy as np
from nptyping import NDArray

import pymd.atoms as mdatoms
from pymd.atoms import Atoms
from pymd.state import NVEState


class PlotModel(object):
    def __init__(
        self,
        output: NDArray[NVEState.OUTDTYPE],
        atomsOutput: List[Atoms],
        rc: float,
    ):
        self._update_funcs: List[Callable] = []

        self.output = output
        self.atomsOutput = atomsOutput

        self.grStart = 1
        self.grStartMax = len(atomsOutput) - 1
        self.grStop = len(atomsOutput)
        self.grStopMax = len(atomsOutput)
        self.grStep = 1
        self.grStepMax = len(atomsOutput)

        self.rc = rc
        self.dr = 0.01
        self.drMax = rc

        self._var = "KE"
        self.units = 0
        self.current = np.array([self.output["time"], self.output[self.var]])
        self.updatedVars = True
        self.updatedG_r = False

        self.calcGr()

    def calcGr(self):
        self.gr = mdatoms.pair_correlation(
            self.atomsOutput[self.grStart : self.grStop : self.grStep],
            self.rc,
            self.dr,
        )
        self.updatedG_r = True
        self.announce_update()

    def change_units(self, id: int):
        if id == 0:
            self.current[0] = self.output["time"]
            self.current[1] = self.output[self.var]
            self.units = 0
        elif id == 1:
            self.current[0] = self.output["time"] * self.get_unit("time")
            self.current[1] = self.output[self.var] * self.get_unit(self.var)
            self.units = 1
        else:
            pass
        self.updatedVars = True

    def get_unit(self, var: str):
        intvar = self.output.dtype.names.index(var)
        if intvar != 4:
            units = self.atomsOutput[0].elem.units
            outputunits = [
                "time",
                "energy",
                "energy",
                "energy",
                "",
                "temp",
                "pressure",
            ]
            return units[outputunits[intvar]]
        else:
            return 1

    def subscribe_update_func(self, func: Callable):
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    def unsubscribe_update_func(self, func: Callable):
        if func in self._update_funcs:
            self._update_funcs.remove(func)

    def announce_update(self):
        for func in self._update_funcs:
            func()

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, value: int):
        self._var = self.output.dtype.names[value]
        self.current[1] = self.output[self._var]
        self.updatedVars = True


def getValues(filename: str):
    with open(filename + ".json") as f:
        values = json.load(f)
    output = np.loadtxt(filename + ".txt", dtype=NVEState.OUTDTYPE, skiprows=1)
    atomsOutput = mdatoms.atomslist_fromfile(
        values["rho"], filename + "_0.xyz"
    )
    rc = values["rc"]
    return (output, atomsOutput, rc)
