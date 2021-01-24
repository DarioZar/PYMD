from PyQt5 import QtWidgets
from pymd.gui.view.MainWindow import MainWindow
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    QMainWindow = QtWidgets.QMainWindow()
    ui = MainWindow()
    ui.setupUi(QMainWindow)
    QMainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
