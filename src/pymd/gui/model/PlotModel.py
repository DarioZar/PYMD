import numpy as np
import json
import pymd.atoms as mdatoms


class PlotModel(object):
    def __init__(self, output, atomsOutput, rc):
        self._update_funcs = []

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

        self._var = 1
        self.units = 0
        self.current = np.array([self.output[0], self.output[self.var]])
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

    def change_units(self, id):
        if id == 0:
            self.current[0] = self.output[0]
            self.current[1] = self.output[self.var]
            self.units = 0
        elif id == 1:
            self.current[0] = self.output[0] * self.get_unit(0)
            self.current[1] = self.output[self.var] * self.get_unit(self.var)
            self.units = 1
        else:
            pass
        self.updatedVars = True

    def get_unit(self, var: int):
        if var != 4:
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
            return units[outputunits[var]]
        else:
            return 1

    def subscribe_update_func(self, func):
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    def unsubscribe_update_func(self, func):
        if func in self._update_funcs:
            self._update_funcs.remove(func)

    def announce_update(self):
        for func in self._update_funcs:
            func()

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, value):
        self._var = value
        self.current[1] = self.output[value]
        self.updatedVars = True


def getValues(filename: str):
    with open(filename + ".json") as f:
        values = json.load(f)
    output = np.loadtxt(filename + ".txt", skiprows=1, unpack=True)
    atomsOutput = mdatoms.atomslist_fromfile(
        values["rho"], filename + "_0.xyz"
    )
    rc = values["rc"]
    print(output)
    return [output, atomsOutput, rc]
