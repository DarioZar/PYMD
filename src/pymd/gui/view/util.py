from PyQt5 import QtWidgets
from PyQt5.QtMultimedia import QSound

from pymd.gui import resources  # noqa: F401


def showFileDialog(strtype: str) -> str:
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
        None,
        f"Scegli file {strtype} della simulazione",
        "",
        f"{strtype} Files (*.{strtype});;All Files (*)",
        options=options,
    )
    return fileName


def showErrorDialog(string: str):
    error_dialog = QtWidgets.QErrorMessage()
    error_dialog.showMessage(string)
    error_dialog.setWindowTitle("Error!")
    errsound = QSound(":/sound/error")
    errsound.play()
    error_dialog.exec_()
