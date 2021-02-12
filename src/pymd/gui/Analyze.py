import sys

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QApplication

from pymd.gui.model.PlotModel import PlotModel, getValues
from pymd.gui.view.PlotView import PlotView


class Analyze(QApplication):
    def __init__(self, sys_argv, output, atomsOutput, rc):
        super(Analyze, self).__init__(sys_argv)
        self.model = PlotModel(output, atomsOutput, rc)
        self.view = PlotView(self.model)
        self.view.show()


def main(values=None, filename=None):
    locale = QLocale(QLocale.English)
    locale.setNumberOptions(QLocale.RejectGroupSeparator)
    QLocale.setDefault(locale)
    if values is None and filename is not None:
        values = getValues(filename)
    elif values is None and filename is None:
        raise Exception("Must specify a filename or some values")
    app = Analyze(sys.argv, values[0], values[1], values[2])
    sys.exit(app.exec_())


if __name__ == "__main__":
    filename = input("Enter filename:")
    main(filename=filename)
