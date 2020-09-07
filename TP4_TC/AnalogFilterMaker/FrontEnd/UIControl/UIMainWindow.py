from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi


class UIMainWindow(QMainWindow):

    def __init__(self, ui_manager):  # Conecta los componentes del .ui realizado en QT con el programa en python
        QMainWindow.__init__(self)
        loadUi('FrontEnd/UIs/mainscreen.ui', self)
        self.setWindowTitle("Filter Design Tool")
        self.ui_manager = ui_manager
        self.initButton.clicked.connect(self.initialize)
        self.load_project_button.clicked.connect(self.load_project_clicked)

    def initialize(self):
        self.ui_manager.next_window()

    def load_project_clicked(self):
        self.ui_manager.load_current_state()