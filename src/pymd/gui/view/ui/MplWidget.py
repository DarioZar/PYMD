from PyQt5 import QtWidgets
import matplotlib

matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # noqa: E402
from matplotlib.backends.backend_qt5agg import (  # noqa: E402
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure  # noqa: E402


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        # super().setSizePolicy(
        #    QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        # )
        # super().updateGeometry()


class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = MplCanvas()
        self.axes = self.canvas.axes
        self.navbar = NavigationToolbar(self.canvas, self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.navbar)
        self.setLayout(self.layout)

    def setPlot(self, *args):
        return self.axes.plot(*args)

    def updatePlot(self, plot, data):
        plot.set_xdata(data[0])
        plot.set_ydata(data[1])
        self.axes.relim()
        self.axes.autoscale_view()
        self.canvas.draw()
