import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale
from pymd.gui.model.Model import Model
from pymd.gui.controller.MainController import MainController
from pymd.gui.view.MainView import MainView

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.model = Model()
        self.main_ctrl = MainController(self.model)
        self.main_view = MainView(self.model, self.main_ctrl)
        self.main_view.show()

def main():
    locale = QLocale(QLocale.English)
    locale.setNumberOptions(QLocale.RejectGroupSeparator)
    QLocale.setDefault(locale)
    app = App(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()