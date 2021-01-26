from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QDialog

from pymd.gui import resources  # noqa: F401
from pymd.gui.view.ui.Ui_ProgressDialog import Ui_ProgressDialog


class ProgressDialog(Ui_ProgressDialog):
    @property
    def worker(self):
        return self.myworker

    @worker.setter
    def worker(self, value):
        self.myworker = value
        self.myworker.progress.connect(self.reportProgressSlot)
        self.myworker.currentoutput.connect(self.reportProgressString)
        self.myworker.timeElapsed.connect(self.reportFinishTime)
        self.myworker.finished.connect(self.enablePlotting)
        self.myworker.finished.connect(self.playFinishSound)

    def __init__(self):
        super().__init__()
        self.finishsound = QSound(":/sound/joy")

    def setupUi(self, Dialog: QDialog):
        # Initialize view
        super().setupUi(Dialog)
        self.text.clear()
        Dialog.rejected.connect(self.closeEvent)
        self.plotgr.clicked.connect(self.plotgrSlot)

    def reportProgressSlot(self, value):
        self.progressBar.setValue(100 * value)

    def reportProgressString(self, value):
        self.text.append(value)

    def reportFinishTime(self, value):
        self.text.append(f"Elapsed time: {value:0.3g} s")
        self.progressBar.setValue(100)

    def enablePlotting(self):
        self.plotgr.setEnabled(True)

    def playFinishSound(self):
        self.finishsound.play()

    def plotgrSlot(self):
        # window =
        pass

    def closeEvent(self):
        self.myworker.flag = True
