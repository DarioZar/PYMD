import time

from pymd.gui.model.model import Model
from pymd.gui.ui.Ui_MainWindow import Ui_MainWindow
from pymd.gui.view.ProgressDialog import ProgressDialog
from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIntValidator


class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.model = Model()

    def setupUi(self, MainWindow):
        # Initialize view
        super().setupUi(MainWindow)
        # Set items of Combo, default values and visibility
        self.element.addItems(self.model.available_molecules())
        self.statistics.addItems(self.model.available_statistics())
        self.fileName.setVisible(self.fromFileCheck.isChecked())
        self.browseFile.setVisible(self.fromFileCheck.isChecked())
        self.tBathGroup.setVisible(self.statistics.currentIndex() == 1)
        self.output.setText(time.strftime("%Y%m%d-%H%M%S", time.localtime()))
        # Attach validators and signals
        self.attachValidators()
        self._connectSignals()

    def attachValidators(self):
        ''' Set validator for every numeric field'''
        self.number.setValidator(QIntValidator(bottom=0))
        self.rho.setValidator(QDoubleValidator(bottom=0))
        self.t0.setValidator(QDoubleValidator(bottom=0))
        self.rc.setValidator(QDoubleValidator(bottom=0))
        self.tBath.setValidator(QDoubleValidator(bottom=0))
        self.nu.setValidator(QDoubleValidator(bottom=0))
        self.steps.setValidator(QIntValidator(bottom=0))
        self.dt.setValidator(QDoubleValidator(bottom=0))
        self.fSamp.setValidator(QIntValidator(bottom=0))

    def startSlot(self):
        if self.canStart():
            self.getModeValues()
            self.model.setSimulationData()
            self.runSimulation()
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage("Fill all numeric fields before\
                starting the simulation!")
            error_dialog.setWindowTitle("Error!")
            error_dialog.exec_()

    def runSimulation(self):
        self.dialog = QProgressDialog = QtWidgets.QDialog()
        self.progressdialog = ProgressDialog()
        self.progressdialog.setupUi(QProgressDialog)
        self.progressdialog.runSimulation(
            self.model.state, self.model.values, self.model.result)
        self.dialog.show()

    def getModeValues(self):
        self.model.mode = self.statistics.currentIndex()
        self.model.values.update({
            'N': int(self.number.text()),
            'elem': self.element.currentText(),
            'rho': float(self.rho.text()),
            't0': float(self.t0.text()),
            'rc': float(self.rc.text()),
            'steps': int(self.steps.text()),
            'dt': float(self.dt.text()),
            'fSamp': int(self.fSamp.text()),
            'use_ecorr': self.eCorrCheck.isChecked(),
            'append': self.singleFileCheck.isChecked(),
            'unfold': self.unfold.isChecked(),
            'outputfile': self.output.text()
        })
        if self.model.mode == 1:
            self.model.values.update({
                'Tbath': float(self.tBath.text()),
                'nu':    float(self.nu.text())
            })
        else:
            self.model.values.update({
                'Tbath': None,
                'nu':   None
            })

    def enableAdditionalSlot(self):
        '''Show thermostat options if NVT is selected'''
        idx = self.statistics.currentIndex()
        self.tBathGroup.setVisible(idx == 1)

    def browseSlot(self):
        '''Browse folders for .xyz file'''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "QFileDialog.getOpenFileName()",
            "",
            "XYZ Files (*.xyz);;All Files (*)",
            options=options)
        if fileName:
            self.model.setFile(fileName)
            self.refreshAll()

    def useFileSlot(self):
        '''Show file options if file check is checked.
           Also, resets file dependent values.'''
        useFile = self.fromFileCheck.isChecked()
        self.fileName.setVisible(useFile)
        self.browseFile.setVisible(useFile)
        self.element.setEnabled(not useFile)
        self.number.setEnabled(not useFile)
        # self.rho.setEnabled(not useFile)
        self.model.filename = None
        self.fileName.setText(".xyz file")

    def _connectSignals(self):
        '''Connect signals to buttons'''
        self.fromFileCheck.stateChanged.connect(self.useFileSlot)
        self.browseFile.clicked.connect(self.browseSlot)
        self.statistics.currentIndexChanged.connect(self.enableAdditionalSlot)
        self.start.clicked.connect(self.startSlot)

    def refreshAll(self):
        if self.model.fileName:
            self.fileName.setText(self.model.fileName)
            self.element.setCurrentText(self.model.elemstr)
            self.number.setText(str(self.model.N))
        else:
            self.fileName.setText("Invalid file!")

    def canStart(self):
        numfields = [self.number, self.rho, self.t0, self.rc,
                     self.steps, self.dt, self.fSamp]
        mode = self.statistics.currentIndex()
        if mode == 1:
            numfields += [self.tBath, self.nu]
        numericfilled = all(not n.text() == "" for n in numfields)
        outputfilled = not (self.output == "")
        canStart = (numericfilled and outputfilled)
        return canStart
