# Main class of the output window.
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import cv2
import matplotlib as mpl
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from GraphStructures.GraphValues import GraphTypes
from ImageMananagent.ImageManagement import ImageManagement
from UIManagement.GraphManager import GraphManager

# Clase UIWindow. Maneja lo relacionado con la ventana mostrada al usuario.
class UIWindow(QMainWindow):

    def __init__(self):  # Conecta los componentes del .ui realizado en QT con el programa en python
        QMainWindow.__init__(self)
        loadUi('tcDesign.ui', self)
        self.setWindowTitle("Plot Tool")
        self.graphics = None
        self.graphManager = GraphManager(self)
        self.transfButton.clicked.connect(self.graphManager.trans_button_graph)
        self.spiceButton.clicked.connect(self.graphManager.spice_button_graph)
        self.medButton.clicked.connect(self.graphManager.med_button_graph)
        self.deleteButton.clicked.connect(self.delete_all)
        self.changeModuleLabels.clicked.connect(self.__label_module_edit__)
        self.changePhaseLabels.clicked.connect(self.__label_phase_edit__)
        self.spiceCheck.stateChanged.connect(self.graphManager.spice_checked)
        self.transferenceCheck.stateChanged.connect(self.graphManager.transf_checked)
        self.medCheck.stateChanged.connect(self.graphManager.med_checked)
        self.ModuleWidget = self.graphwidget  # Objeto de la clase GraphWidget
        self.PhaseWidget = self.phaseGraph  # Objeto de la clase GraphWidget
        self.ModuleWidget.canvas.axes.set_title('Módulo')
        self.PhaseWidget.canvas.axes.set_title('Fase')
        self.ModuleWidget.save_all_callback = self.export_graphs
        self.PhaseWidget.save_all_callback = self.export_graphs
        self.ModuleWidget.redraw_callback = self.__update_graph__
        self.PhaseWidget.redraw_callback = self.__update_graph__

    def delete_all(self):  # borra todos los graficos
        self.graphManager.delete_button_graph()
        self.ModuleWidget.clear_marked_points()
        self.PhaseWidget.clear_marked_points()
        self.__update_graph__()

    def export_graphs(self):  # exporta los graficos a archivos png
        application_window = tk.Tk()  # Utiliza Tk para seleccionar la carpeta donde se guarda
        application_window.withdraw()  # Esconde la ventana que muestra por defecto Tk
        folder_path = filedialog.askdirectory()  # Le pide al usuario que seleccione una carpeta para guardar las imagenes
        if folder_path is not None and folder_path != "":  # Valida la seleccion del usuario
            answer = messagebox.askyesnocancel(title="Selecciona",
                                               message="¿Desea guardar las imagenes en archivos separados?")
            """ A partir de ahora, aunque el usuario quiera guardar las imagenes en una unica foto, en principio se 
            guardan por separado. """
            moduleimage = ImageManagement.save_image(folder_path, self.ModuleWidget.figure, "module")
            phaseimage = ImageManagement.save_image(folder_path, self.PhaseWidget.figure, "phase")
            if not answer:
                """"Si el usuario quiso que las imagenes se guarden en una unica foto, concatena las dos imagenes
                guardadas anteriormente, guarda la nueva imagen y elimina las viejas."""
                im_v = ImageManagement.concat_images(moduleimage, phaseimage)
                name = ImageManagement.get_image_name(folder_path, "signals")
                cv2.imwrite(name, im_v)
                os.remove(moduleimage)
                os.remove(phaseimage)

    # Cambia labels del grafico de modulo
    def __label_module_edit__(self):
        self.ModuleWidget.x_label = self.xTextEdit.toPlainText()
        self.ModuleWidget.y_label = self.yTextEdit.toPlainText()
        self.__fix_axes_titles_position__(self.ModuleWidget)
        self.__update_graph__()
        self.xTextEdit.setPlainText(" ")
        self.yTextEdit.setPlainText(" ")

    # Cambia labels del grafico de fase
    def __label_phase_edit__(self):
        self.PhaseWidget.x_label = self.xTextEdit.toPlainText()
        self.PhaseWidget.y_label = self.yTextEdit.toPlainText()
        self.__fix_axes_titles_position__(self.PhaseWidget)
        self.__update_graph__()
        self.xTextEdit.setPlainText(" ")
        self.yTextEdit.setPlainText(" ")

    # update_graph(). Se la debe llamar para actualizar el contenido mostrado en los gráficos Esta función buscará en
    # self.graphics los datos que deba mostrar. Para agregar/eliminar graficos de self.graphics se utilizan las
    # funciones del archivo UIManagement/GraphManager.py En self.graphic se van guardando listas de gráficos. Para
    # este caso cada lista tendria un gráfico de módulo y uno de fase, si lo necesitara.
    def __update_graph__(self):
        self.ModuleWidget.canvas.axes.clear()  # Se limpian los gráficos
        self.PhaseWidget.canvas.axes.clear()

        self.PhaseWidget.canvas.draw()  # Se defibujan en blanco
        self.ModuleWidget.canvas.draw()
        self.ModuleWidget.graph_labels = []  # Array para las leyendas de los gráficos.
        self.PhaseWidget.graph_labels = []
        # draw each activated graph
        if self.graphics is not None:
            if len(self.graphics) > 0:  # Si hay graficos para mostrar
                for graphList in self.graphics:  # Se itera por cada lista de gráficos (generalmente lista de 2
                    # valores, PhaseGraph y ModuleGraph)
                    for toggeable_graph in graphList:  # Se itera por cada gráfico
                        if toggeable_graph[0].activated:  # Chequea el flag de mostrar el gráfico en pantalla está
                            # activado
                            if toggeable_graph[0].graph.type == GraphTypes.BodeModule:
                                self.ModuleWidget.graph_labels.append(toggeable_graph[0].graph.title)  # Agrega leyenda
                                self.__plot_graph__(toggeable_graph[0].graph, self.ModuleWidget,
                                                    toggeable_graph[1])  # Dibuja el gráfico
                            elif toggeable_graph[0].graph.type == GraphTypes.BodePhase:
                                self.PhaseWidget.graph_labels.append(toggeable_graph[0].graph.title)  # Agrega leyenda
                                self.__plot_graph__(toggeable_graph[0].graph, self.PhaseWidget,
                                                    toggeable_graph[1])  # Dibuja el gráfico

        # Se dibujan los puntos que fueron marcados por el usuario.

        self.__plot_points__(self.PhaseWidget)

        self.__plot_points__(self.ModuleWidget)

    # Función plot_points. Dibuja en pantalla los puntos que fueron marcados por el usuario en el grafico que
    # corresponda. Parametro, el grafico donde se desea actualizar el dibujo de los puntos
    # Esta función busca los puntos en graph_widget.x_marked_points y graph_widget.y_marked_points.
    # El agregado de puntos a estas variables se realiza directamente en graphwidget.py
    def __plot_points__(self, graph_widget):
        for i in range(len(graph_widget.x_marked_points)):  # Se itera cada punto
            x_point = graph_widget.x_marked_points[i]
            y_point = graph_widget.y_marked_points[i]
            graph_widget.canvas.axes.plot(x_point,  # Se dibuja el punto en forma de X y en color rojo.
                                          y_point, color='red',
                                          markersize=8, marker='x')

            # Si el valor del punto es chico (entre -10 y 10) se utilizan 2 decimales para su label. Sino,
            # ningún decimal.
            if 10 > x_point > -10:
                x_text = str(round(x_point, 2))
            else:
                x_text = str(int(round(x_point)))

            if 10 > y_point > -10:
                y_text = str(round(y_point, 2))
            else:
                y_text = str(int(round(y_point)))

            graph_widget.canvas.axes.annotate("[" + x_text + "; " + y_text + "]"
                                              , (x_point, y_point))  # Se agrega el label a cada punto
        graph_widget.canvas.axes.grid(self)
        graph_widget.canvas.draw()  # Se redibuja el grafico con los puntos-

    # Función plot_graph. Se la llama de update_graph dibujar cada grafico.. Parametros: graph, valores del grafico a
    # mostrar; graph_widget: widget donde se añadirá el gráfico; color: color del gráfico.
    def __plot_graph__(self, graph, graph_widget, color):
        self.__fix_axes_titles_position__(graph_widget)
        if (not graph_widget.continuous_line_flag) and graph.scatterable:
            graph_widget.canvas.axes.scatter(graph.x_values,  # Función principal que setea los gráficos a escala
                                              graph.y_values,  # logarítmica con los valores indicados en los arrays.
                                              color=color)
        else:
            graph_widget.canvas.axes.plot(graph.x_values,  # Función principal que setea los gráficos a escala
                                          graph.y_values,  # logarítmica con los valores indicados en los arrays.
                                          color=color)
        if graph_widget.log_flag:
            graph_widget.canvas.axes.set_xscale('log')
        graph_widget.canvas.axes.legend(graph_widget.graph_labels,
                                        loc='best')  # leyendas ubicadas en el mejor lugar posible

        self.ModuleWidget.canvas.axes.set_title('Módulo')
        self.PhaseWidget.canvas.axes.set_title('Fase')
        graph_widget.canvas.axes.grid(self)
        graph_widget.canvas.draw()  # redibuja

    # Funciones que configuran y muestran los titulos de los ejes.
    def __fix_axes_titles_position__(self, widget):
        self.__fix_y_title_position__(widget)
        self.__fix_x_title_position__(widget)

    def __fix_x_title_position__(self, widget):
        ticklabelpad = mpl.rcParams['xtick.major.pad']
        widget.canvas.axes.annotate(widget.x_label, xy=(1, 0), xytext=(20, -ticklabelpad),
                                    ha='left', va='top',
                                    xycoords='axes fraction', textcoords='offset points')

    def __fix_y_title_position__(self, widget):
        ticklabelpad = mpl.rcParams['ytick.major.pad']
        widget.canvas.axes.annotate(widget.y_label, xy=(0, 1), xytext=(-30, -ticklabelpad+10),
                                    ha='left', va='bottom',
                                    xycoords='axes fraction', textcoords='offset points', rotation=0)
