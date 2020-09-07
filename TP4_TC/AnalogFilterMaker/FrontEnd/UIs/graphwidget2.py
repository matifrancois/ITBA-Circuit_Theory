from PyQt5.QtWidgets import QWidget
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class GraphWidget2(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.x_label = "X"
        self.y_label = "Y"
        self.title = " "
        self.figure = Figure()
        self.figure.patch.set_facecolor((40/255, 55/255, 57/255,1))
        self.canvas = FigureCanvas(self.figure)


        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.figure.tight_layout()

        self.setLayout(vertical_layout)
        self.figure.tight_layout()
        self.canvas.axes.tick_params(direction='inout', length=.2, width=.2, labelsize=5, colors='k')
