import time
from typing import Union

import numpy as np
from pymd.state import NVEState, NVTAndersenState
from PyQt5.QtCore import QObject, pyqtSignal


class SimulatorWorker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(float)
    currentoutput = pyqtSignal(str)
    timeElapsed = pyqtSignal(float)

    def __init__(self, state: Union[NVEState, NVTAndersenState], values: dict,
                 result: np.ndarray):
        super().__init__()
        self.state = state
        self.values = values
        self.flag = False

    def run(self):
        a = time.time()
        steps = self.values['steps']
        dt = self.values['dt']
        fSamp = self.values['fSamp']
        append = self.values['append']
        unfold = self.values['unfold']
        filename = self.values['outputfile']
        self.state.atoms.write_xyz(filename+"_0.xyz", unfold=unfold)
        output = np.empty((steps, len(self.state.vars_output())))
        self.currentoutput.emit("Time\t\tKE\t\tPE\t\tTE\t\tdrift\t\tT\t\tP")
        output[0] = self.state.vars_output()
        self.currentoutput.emit(self.tostring(output[0]))
        for i in range(1, steps):
            if self.flag:
                break
            self.state.step(dt)
            output[i] = self.state.vars_output()
            if i % fSamp == 0:
                self.currentoutput.emit(self.tostring(output[i]))
                if append:
                    self.state.atoms.write_xyz(filename+"_0.xyz", append=True)
                else:
                    self.state.atoms.write_xyz(filename+f"_{i}.xyz")
            self.progress.emit(i/steps)
        self.finished.emit()
        self.timeElapsed.emit(time.time() - a)
        np.savetxt(filename+".txt",
                   output, header="Time\tKE\tPE\tTE\tdrift\tT\tP")

    def tostring(self, output):
        outstring = ""
        for n in output:
            outstring += "{:.3e}\t".format(n)
        return outstring
