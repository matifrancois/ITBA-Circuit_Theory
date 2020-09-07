from PyQt5 import QtWidgets
from FrontEnd.UIManager import UIManager


def start():
    app = QtWidgets.QApplication([])

    uiMan = UIManager()
    uiMan.begin()

    app.exec()


if __name__ == "__main__":
    start()
