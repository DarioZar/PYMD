from typing import Union

from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtMultimedia import QSound

from pymd.gui import resources  # noqa: F401
from pymd.gui.view.ProgressDialog import ProgressDialog
from pymd.gui.view.PlotWindow import PlotWindow
from pymd.gui.view.ui.Ui_MainWindow import Ui_MainWindow


class MainView(QtWidgets.QMainWindow):
    def __init__(self, model, main_ctrl):
        self.model = model
        self.main_ctrl = main_ctrl
        super(MainView, self).__init__()
        self.build_ui()
        # Initial values
        self.update_ui_from_model()
        # register func with model for model update announcements
        self.model.subscribe_update_func(self.update_ui_from_model)

    def build_ui(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # set Qt model for compatible widget types
        self.ui.comboBox_element.setModel(self.model.element_model)
        self.ui.comboBox_statistics.setModel(self.model.statistics_model)

        # connect widget signals to event functions
        self._connectSignals()
        self._attachValidators()

    def _connectSignals(self):
        self.ui.comboBox_element.currentTextChanged.connect(self.on_element)
        self.ui.checkBox_fromFile.stateChanged.connect(self.on_fromFile)
        self.ui.pushButton_browseFile.clicked.connect(self.on_browseFile)
        self.ui.lineEdit_number.textEdited.connect(self.on_number)
        self.ui.lineEdit_number.editingFinished.connect(self.update_L)
        self.ui.lineEdit_rho.textEdited.connect(self.on_rho)
        self.ui.lineEdit_rho.editingFinished.connect(self.update_L)
        self.ui.comboBox_statistics.currentIndexChanged.connect(
            self.on_statistics
        )
        self.ui.lineEdit_t0.textEdited.connect(self.on_t0)
        self.ui.lineEdit_rc.textEdited.connect(self.on_rc)
        self.ui.lineEdit_tBath.textEdited.connect(self.on_tBath)
        self.ui.lineEdit_nu.textEdited.connect(self.on_nu)
        self.ui.checkBox_eCorr.stateChanged.connect(self.on_eCorr)
        self.ui.lineEdit_steps.textEdited.connect(self.on_steps)
        self.ui.lineEdit_dt.textEdited.connect(self.on_dt)
        self.ui.lineEdit_output.textEdited.connect(self.on_output)
        self.ui.lineEdit_fSamp.textEdited.connect(self.on_fSamp)
        self.ui.checkBox_unfold.stateChanged.connect(self.on_unfold)
        self.ui.checkBox_singleFile.stateChanged.connect(self.on_singleFile)
        self.ui.pushButton_start.clicked.connect(self.on_start)

    def _attachValidators(self):
        """ Set validator for every numeric field"""
        self.ui.lineEdit_number.setValidator(QIntValidator(bottom=0))
        self.ui.lineEdit_rho.setValidator(QDoubleValidator(bottom=0))
        self.ui.lineEdit_L.setValidator(QDoubleValidator(bottom=0))
        self.ui.lineEdit_t0.setValidator(QDoubleValidator(bottom=0))
        self.ui.lineEdit_rc.setValidator(QDoubleValidator(bottom=0))
        self.ui.lineEdit_tBath.setValidator(QDoubleValidator(bottom=0))
        self.ui.lineEdit_nu.setValidator(QDoubleValidator(bottom=0))
        self.ui.lineEdit_steps.setValidator(QIntValidator(bottom=0))
        self.ui.lineEdit_dt.setValidator(QDoubleValidator(bottom=0))
        self.ui.lineEdit_fSamp.setValidator(QIntValidator(bottom=0))

    def update_ui_from_model(self):
        # update widget values from model
        self.element = self.model.element
        self.fromFile = self.model.fromFile
        self.fileName = self.model.fileName
        self.browseFile = self.model.browseFile
        self.number = self.model.number
        self.rho = self.model.rho
        self.L = self.model.L
        self.statistics = self.model.statistics
        self.t0 = self.model.t0
        self.rc = self.model.rc
        self.tBath = self.model.tBath
        self.nu = self.model.nu
        self.eCorr = self.model.eCorr
        self.steps = self.model.steps
        self.dt = self.model.dt
        self.output = self.model.output
        self.fSamp = self.model.fSamp
        self.unfold = self.model.unfold
        self.singleFile = self.model.singleFile
        if self.model.start:
            self.model.start = False
            self.showProgressDialog(self.model.worker)
            self.hide()
        if self.model.showPlot:
            self.showPlot(self.model.plotModel)

    # widget signal event functions
    def on_element(self, index):
        self.main_ctrl.change_element(index)

    def on_fromFile(self, state):
        self.main_ctrl.change_fromFile(state)

    def on_browseFile(self):
        self.main_ctrl.change_browseFile(
            self.browseFile, self.showFileDialog()
        )

    def on_number(self, text):
        self.main_ctrl.change_number(text)

    def on_rho(self, text):
        self.main_ctrl.change_rho(text)

    def update_L(self):
        self.main_ctrl.update_L()

    def on_statistics(self, index):
        self.main_ctrl.change_statistics(index)

    def on_t0(self, text):
        self.main_ctrl.change_t0(text)

    def on_rc(self, text):
        self.main_ctrl.change_rc(text)

    def on_tBath(self, text):
        self.main_ctrl.change_tBath(text)

    def on_nu(self, text):
        self.main_ctrl.change_nu(text)

    def on_eCorr(self, state):
        self.main_ctrl.change_eCorr(state)

    def on_steps(self, text):
        self.main_ctrl.change_steps(text)

    def on_dt(self, text):
        self.main_ctrl.change_dt(text)

    def on_output(self, text):
        self.main_ctrl.change_output(text)

    def on_fSamp(self, text):
        self.main_ctrl.change_fSamp(text)

    def on_unfold(self, state):
        self.main_ctrl.change_unfold(state)

    def on_singleFile(self, state):
        self.main_ctrl.change_singleFile(state)

    def on_start(self):
        valid, error = self.model.isInputValid()
        if not valid:
            self.showErrorDialog(error)
        self.main_ctrl.change_start(valid)

    def showErrorDialog(self, string: str):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage(string)
        error_dialog.setWindowTitle("Error!")
        errsound = QSound(":/sound/error")
        errsound.play()
        error_dialog.exec_()

    def showFileDialog(self) -> str:
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Scegli file di coordinate *.xyz",
            "",
            "XYZ Files (*.xyz);;All Files (*)",
            options=options,
        )
        return fileName

    def showProgressDialog(self, worker):
        dialog = ProgressDialog(self.main_ctrl, parent=self)
        dialog.worker = worker
        dialog.show()

    def showPlot(self, plotModel):
        plotWindow = PlotWindow(plotModel, parent=self)
        plotWindow.show()

    # properties for widget value
    @property
    def element(self) -> str:
        return self.ui.comboBox_element.currentText()

    @element.setter
    def element(self, value: str):
        self.ui.comboBox_element.setCurrentText(value)

    @property
    def fromFile(self) -> bool:
        return self.ui.checkBox_fromFile.isChecked()

    @fromFile.setter
    def fromFile(self, value: bool):
        self.ui.checkBox_fromFile.setChecked(value)
        self.ui.lineEdit_fileName.setVisible(value)
        self.ui.pushButton_browseFile.setVisible(value)
        self.ui.lineEdit_number.setEnabled(not value)
        self.ui.comboBox_element.setEnabled(not value)

    @property
    def browseFile(self) -> bool:
        return self.ui.pushButton_browseFile.isChecked()

    @browseFile.setter
    def browseFile(self, value: bool):
        self.ui.pushButton_browseFile.setChecked(value)

    @property
    def fileName(self) -> str:
        return self.ui.lineEdit_fileName.text()

    @fileName.setter
    def fileName(self, value: str):
        self.ui.lineEdit_fileName.setText(value)

    @property
    def number(self) -> int:
        return int(self.ui.lineEdit_number.text())

    @number.setter
    def number(self, value: int):
        self.ui.lineEdit_number.setText(as_str(value))

    @property
    def rho(self) -> float:
        return float(self.ui.lineEdit_rho.text())

    @rho.setter
    def rho(self, value: float):
        self.ui.lineEdit_rho.setText(as_str(value))

    @property
    def L(self) -> float:
        return float(self.ui.lineEdit_L.text())

    @L.setter
    def L(self, value: float):
        self.ui.lineEdit_L.setText(as_str(value, fmtstr=":0.3f"))

    @property
    def statistics(self) -> int:
        return self.ui.comboBox_statistics.currentIndex()

    @statistics.setter
    def statistics(self, value: int):
        self.ui.comboBox_statistics.setCurrentIndex(value)
        self.ui.tBathGroup.setVisible(value != 0)

    @property
    def t0(self) -> float:
        return float(self.ui.lineEdit_t0.text())

    @t0.setter
    def t0(self, value: float):
        self.ui.lineEdit_t0.setText(as_str(value))

    @property
    def rc(self) -> float:
        return float(self.ui.lineEdit_rc.text())

    @rc.setter
    def rc(self, value: float):
        self.ui.lineEdit_rc.setText(as_str(value))

    @property
    def tBath(self) -> float:
        return float(self.ui.lineEdit_tBath.text())

    @tBath.setter
    def tBath(self, value: float):
        self.ui.lineEdit_tBath.setText(as_str(value))

    @property
    def nu(self) -> float:
        return self.ui.lineEdit_nu.text()

    @nu.setter
    def nu(self, value: float):
        self.ui.lineEdit_nu.setText(as_str(value))

    @property
    def eCorr(self) -> bool:
        return self.ui.checkBox_eCorr.isChecked()

    @eCorr.setter
    def eCorr(self, value: bool):
        self.ui.checkBox_eCorr.setChecked(value)

    @property
    def steps(self) -> int:
        return self.ui.lineEdit_steps.text()

    @steps.setter
    def steps(self, value: int):
        self.ui.lineEdit_steps.setText(as_str(value))

    @property
    def dt(self) -> float:
        return self.ui.lineEdit_dt.text()

    @dt.setter
    def dt(self, value: float):
        self.ui.lineEdit_dt.setText(as_str(value))

    @property
    def output(self) -> str:
        return self.ui.lineEdit_output.text()

    @output.setter
    def output(self, value: str):
        self.ui.lineEdit_output.setText(value)

    @property
    def fSamp(self) -> int:
        return self.ui.lineEdit_fSamp.text()

    @fSamp.setter
    def fSamp(self, value: int):
        self.ui.lineEdit_fSamp.setText(as_str(value))

    @property
    def unfold(self) -> bool:
        return self.ui.checkBox_unfold.isChecked()

    @unfold.setter
    def unfold(self, value):
        self.ui.checkBox_unfold.setChecked(value)

    @property
    def singleFile(self) -> bool:
        return self.ui.checkBox_singleFile.isChecked()

    @singleFile.setter
    def singleFile(self, value: bool):
        self.ui.checkBox_singleFile.setChecked(value)

    @property
    def start(self) -> bool:
        return self.ui.pushButton_start.isChecked()

    @start.setter
    def start(self, value: bool):
        self.ui.pushButton_start.setChecked(value)


def as_str(val: Union[int, float], fmtstr=""):
    if val is not None:
        return ("{" + fmtstr + "}").format(val)
    else:
        return ""
