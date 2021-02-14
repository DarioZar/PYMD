from PyQt5.QtCore import QThread
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QDialog

from pymd.gui import resources  # noqa: F401
from pymd.gui.view.ui.Ui_ProgressDialog import Ui_ProgressDialog


class ProgressDialog(QDialog, Ui_ProgressDialog):
    @property
    def worker(self):
        return self._worker

    @worker.setter
    def worker(self, value):
        self._worker = value
        self.runWorker()
        self._connectWorkerSignals()

    def __init__(self, main_ctrl, parent=None):
        super().__init__(parent)
        self.main_ctrl = main_ctrl
        self.finishsound = QSound(":/sound/joy")
        self.setupUi()

    def setupUi(self):
        # Initialize view
        super().setupUi(self)
        self.text.clear()
        self.rejected.connect(self.closeEvent)
        self.plotgr.clicked.connect(self.plotgrSlot)

    def plotgrSlot(self):
        self.main_ctrl.change_showPlot()
        self.plotgr.setEnabled(False)

    def closeEvent(self, _):
        self._worker.flag = True
        self.parent().show()

    def runWorker(self):
        # Create a QThread object
        thread = QThread(parent=self.parent())
        # Move worker to the thread
        self._worker.moveToThread(thread)
        # Connect signals and slots
        thread.started.connect(self._worker.run)
        self._worker.finished.connect(thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        # Start the thread
        thread.start()

    def _connectWorkerSignals(self):
        self._worker.progress.connect(
            lambda p: self.progressBar.setValue(100 * p)
        )
        self._worker.currentoutput.connect(lambda out: self.text.append(out))
        self._worker.timeElapsed.connect(
            lambda t: (
                self.text.append(f"Elapsed time: {t:0.3g} s"),
                self.progressBar.setValue(100),
            )
        )
        self._worker.finished.connect(
            lambda: (self.plotgr.setEnabled(True), self.finishsound.play())
        )
