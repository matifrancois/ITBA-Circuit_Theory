from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

from BodeManagement.BodeConfiguration import BodeManager


class UIMainWindow(QMainWindow):

    def __init__(self):  # Conecta los componentes del .ui realizado en QT con el programa en python
        QMainWindow.__init__(self)
        loadUi('MainUI/mainWindow.ui', self)
        self.setWindowTitle("Instrument Automation")
        self.bode_manager = None
        self.bodeButton.clicked.connect(self.bode_config)

    def bode_config(self):
        self.hide()
        self.bode_manager = BodeManager()

