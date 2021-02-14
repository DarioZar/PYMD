import sys

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QApplication

from pymd.gui.model.PlotModel import PlotModel, getValues
from pymd.gui.view.PlotView import PlotView
from pymd.gui.view.util import showErrorDialog, showFileDialog


class Analyze(QApplication):
    def __init__(self, sys_argv, values=None, filename=None):
        super().__init__(sys_argv)
        if values is None:
            if filename is None:
                filename = self.getFile()
            values = getValues(filename)
        output, atomsOutput, rc = values[0], values[1], values[2]
        self.model = PlotModel(output, atomsOutput, rc)
        self.view = PlotView(self.model)
        self.view.show()

    def getFile(self) -> str:
        fileSelected = False
        while not fileSelected:
            filename = showFileDialog("json")
            filename = filename.split(".json")[0]
            try:
                _ = getValues(filename)
                fileSelected = True
            except Exception as e:
                showErrorDialog(e.args)
                fileSelected = False
        return filename


def main(values=None, filename=None):
    locale = QLocale(QLocale.English)
    locale.setNumberOptions(QLocale.RejectGroupSeparator)
    QLocale.setDefault(locale)
    app = Analyze(sys.argv, values, filename)
    sys.exit(app.exec_())


if __name__ == "__main__":
    filename = input("Enter filename:")
    main(filename=filename)
