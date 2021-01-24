from typing import Union

import numpy as np
from pymd.gui.ui.Ui_ProgressDialog import Ui_ProgressDialog
from pymd.gui.worker.SimulatorWorker import SimulatorWorker
from pymd.state import NVEState, NVTAndersenState
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QDialog


class ProgressDialog(Ui_ProgressDialog):
    def __init__(self):
        super().__init__()

    def setupUi(self, ProgressDialog: QDialog):
        # Initialize view
        super().setupUi(ProgressDialog)
        self.plotgr.clicked.connect(self.plotgrSlot)

    def runSimulation(self, state: Union[NVEState, NVTAndersenState],
                      values: dict, result: np.ndarray):
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = SimulatorWorker(state, values, result)
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgressSlot)
        self.worker.currentoutput.connect(self.reportProgressString)
        self.worker.timeElapsed.connect(self.reportFinishTime)
        self.thread.finished.connect(self.enablePlotting)
        # Start the thread
        self.thread.start()

    def reportProgressSlot(self, value):
        self.progressBar.setValue(100*value)

    def reportProgressString(self, value):
        self.text.append(value)

    def reportFinishTime(self, value):
        self.text.append(f"Finito in {value:.3e} s")
        self.progressBar.setValue(100)

    def enablePlotting(self):
        self.plotgr.setEnabled(True)

    def plotgrSlot(self):
        pass
