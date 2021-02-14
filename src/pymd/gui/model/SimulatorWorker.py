import time
from typing import Union

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from pymd.state import NVEState, NVTAndersenState


class SimulatorWorker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(float)
    currentoutput = pyqtSignal(str)
    timeElapsed = pyqtSignal(float)

    def __init__(self, state: Union[NVEState, NVTAndersenState], values: dict):
        super().__init__()
        self.state = state
        self.values = values
        self.flag = False

    def run(self):
        a = time.time()
        # Unpacks variables
        steps = self.values["steps"]
        dt = self.values["dt"]
        fSamp = self.values["fSamp"]
        append = self.values["append"]
        unfold = self.values["unfold"]
        filename = self.values["outputfile"]
        # JSON output
        with open(filename + ".json", "w") as f:
            f.write(self.state.to_JSON())
        # Positions, velocities output
        atomsOutput = [self.state.atoms.copy()]
        self.state.atoms.write_xyz(filename + "_0.xyz", unfold=unfold)
        # State variables output
        output = np.empty(steps, dtype=self.state.OUTDTYPE)
        self.currentoutput.emit("Time\tKE\tPE\tTE\tdrift\tT\tP")
        output[0] = self.state.vars_output()
        self.currentoutput.emit(self.tostring(output[0]))
        # Simulation loop
        for i in range(1, steps):
            # Break condition if window is closed
            if self.flag:
                break
            # Time step
            self.state.step(dt)
            # Save output
            output[i] = self.state.vars_output()
            if i % fSamp == 0:
                self.currentoutput.emit(self.tostring(output[i]))
                atomsOutput += [self.state.atoms.copy()]
                if append:
                    self.state.atoms.write_xyz(
                        filename + "_0.xyz", append=True
                    )
                else:
                    self.state.atoms.write_xyz(filename + f"_{i}.xyz")
            # Show progress in bar
            self.progress.emit(i / steps)
        # Emit signals and save output
        self.timeElapsed.emit(time.time() - a)
        np.savetxt(
            filename + ".txt",
            output,
            header="Time\tKE\tPE\tTE\tdrift\tT\tP",
            comments="",
        )
        self.output = output
        self.atomsOutput = atomsOutput
        self.finished.emit()

    def tostring(self, output):
        outstring = ""
        for n in output:
            outstring += "{:0.3g}\t".format(n)
        return outstring
