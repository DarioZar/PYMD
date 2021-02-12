from PyQt5 import QtWidgets
from pymd.gui.controller.PlotController import PlotController
from pymd.gui.view.ui.Ui_PlotWindow import Ui_PlotWindow


class PlotView(QtWidgets.QMainWindow, Ui_PlotWindow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.ctrl = PlotController(model)
        self.setupUi()

    def setupUi(self):
        # Initialize view
        super().setupUi(self)
        self.tab1RadioButtons = ["KE", "PE", "TE", "drift", "T", "P"]
        self.tab1UnitsButtons = ["normal", "MKS"]
        self.tab1Plot = self.plotVars.axes.plot(
            self.model.current[0], self.model.current[1]
        )[0]
        self.tab2Plot = self.plotG_r.axes.plot([0], [0], "bo-")[0]
        self._setLimits()
        self._connectSignals()
        self.model.subscribe_update_func(self.update_ui_from_model)

    def _setLimits(self):
        self.spinBox_start.setRange(0, self.model.grStartMax)
        self.spinBox_stop.setRange(1, self.model.grStopMax)
        self.spinBox_step.setRange(1, self.model.grStepMax)
        self.doubleSpinBox_dr.setRange(0, self.model.drMax)
        self.doubleSpinBox_dr.setDecimals(4)

    def _connectSignals(self):
        # Tab 1
        self._setButtonsIds()
        self.buttonGroup.idClicked.connect(self.ctrl.change_buttonId)
        self.buttonGroup_units.idClicked.connect(self.ctrl.change_units)
        # Tab 2
        self.doubleSpinBox_dr.valueChanged.connect(self.ctrl.change_dr)
        self.spinBox_start.valueChanged.connect(self.ctrl.change_start)
        self.spinBox_stop.valueChanged.connect(self.ctrl.change_stop)
        self.spinBox_step.valueChanged.connect(self.ctrl.change_step)
        self.pushButton_plot.clicked.connect(self.ctrl.change_plot)

    def _setButtonsIds(self):
        for id, name in enumerate(self.tab1RadioButtons):
            self.buttonGroup.setId(getattr(self, f"radioButton_{name}"), id)
        for id, name in enumerate(self.tab1UnitsButtons):
            self.buttonGroup_units.setId(
                getattr(self, f"radioButton_{name}"), id
            )

    def update_ui_from_model(self):
        if self.model.updatedVars:
            self.plotVars.updatePlot(self.tab1Plot, self.model.current)
            self.model.updatedVars = False
        if self.model.updatedG_r:
            self.plotG_r.updatePlot(self.tab2Plot, self.model.gr)
            self.model.updatedG_r = False

    @property
    def dr(self):
        return self.doubleSpinBox_dr.value()

    @dr.setter
    def dr(self, value: float):
        self.doubleSpinBox_dr.setValue(value)

    @property
    def start(self):
        return self.spinBox_start.value()

    @start.setter
    def start(self, value: int):
        self.spinBox_start.setValue(value)

    @property
    def stop(self):
        return self.spinBox_stop.value()

    @stop.setter
    def stop(self, value: int):
        self.spinBox_stop.setValue(value)

    @property
    def step(self):
        return self.spinBox_step.value()

    @step.setter
    def step(self, value: int):
        self.spinBox_step.setValue(value)
