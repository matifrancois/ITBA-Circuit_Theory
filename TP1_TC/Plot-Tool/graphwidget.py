# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
# ------------------------------------------------------
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# Clase GraphWidget. Es la clase a la cual corresponden los rectángulos (widgets) donde se muestran los gráficos.
# Se asocian con un QWidget
class GraphWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.x_label = "Eje X"
        self.y_label = "Eje Y"
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)  # Canvas a agregar al widget
        self.toolbar = NavigationToolbar(self.canvas, self)  # cada gráfico tiene un toolbar con herramientos para
        # trabajar sobre él

        vertical_layout = QVBoxLayout()

        # Se le agregan nuevos botones al toolbar, además de los que vienen por defecto y se les asigna una función para
        # cuando son clickeados.
        self.toolbar.addAction(QIcon("Resources\saveall.png"), "Guardar ambos gráficos", self.save_all_pressed)
        self.toolbar.addAction(QIcon("Resources\mark.png"), "Marcar puntos", self.mark_points)
        self.toolbar.addAction(QIcon("Resources\log_lin_approx.jpg"), "Cambiar escala", self.change_scale)
        self.toolbar.addAction(QIcon("Resources\scatter_or_lineal.png"), "Lineal o Dispersión", self.change_format)

        self.cid = self.figure.canvas.mpl_connect('button_press_event', self)  # Evento de cuando se aprieta un botón

        vertical_layout.addWidget(self.canvas)  # Se le agrega el canvas al widget
        vertical_layout.addWidget(self.toolbar)  # Se le agrega el toolbar al widget
        self.graph_labels = []  # Acá se agregan las leyendas de los distintos gráficos mostrados en el toolbar.

        # Arreglos de los puntos marcados por el usuario.
        self.x_marked_points = []
        self.y_marked_points = []

        #
        self.canvas.axes = self.canvas.figure.add_subplot(111)  # Plotea el canvas. Si no se entiende que es el ploteo,
        # mirar
        # https://stackoverflow.com/questions/3584805/in-matplotlib-what-does-the-argument-mean-in-fig-add-subplot111

        self.setLayout(vertical_layout)

        # callbacks de los nuevos botones del toolbar. En None por defecto
        self.save_all_callback = None
        self.redraw_callback = None

        self.mark_points_flag = False  # Flag que indica si los puntos se deben mostrar o estar escondidos.
        self.log_flag = True  # Flag que indica si el grafico se encuentra en escala logaritmica.
        self.continuous_line_flag = False # Flag que indica si el grafico de medicion se muestra como una curva continua o de
        # dispersion

    def __call__(self, event):  # Se llama con un evento de click en el widget.
        if self.mark_points_flag:  # Si el flag de mostrar puntos está activado se agregarán las coordenadas del
            # click a un nuevo punto
            self.x_marked_points.append(event.xdata)
            self.y_marked_points.append(event.ydata)
            self.redraw_callback()

    def save_all_pressed(self):  # Funcion que se llama el tocar en el toolbar el boton de guardar todos los graficos.
        self.save_all_callback()  # Callback que exporte todos los graficos.

    def mark_points(self):  # Funcion que se llama el tocar en el toolbar el boton de marcar puntos.
        self.mark_points_flag = not self.mark_points_flag  # Función que togglea el flag de marcar puntos.

    def clear_marked_points(self):  # Se limpian los puntos marcados
        self.x_marked_points = []
        self.y_marked_points = []

    def change_scale(self):
        self.log_flag = not self.log_flag
        self.redraw_callback()

    def change_format(self):
        self.continuous_line_flag = not self.continuous_line_flag
        self.redraw_callback()