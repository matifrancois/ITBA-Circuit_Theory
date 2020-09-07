from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure


# GraphWidget. Promoted class from the widgets used in UIGraphPreview. Associated with a QWidget instance.
class GraphWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.x_label = "Eje X"
        self.y_label = "Eje Y"
        self.title = " "
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        vertical_layout = QVBoxLayout()

        vertical_layout.addWidget(self.canvas)

        #
        self.canvas.axes = self.canvas.figure.add_subplot(111)

        self.setLayout(vertical_layout)
