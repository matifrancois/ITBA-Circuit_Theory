import csv
import os

import matplotlib as mpl
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi


# UIGraphPreview: Window which plots and shows the measures obtained in order to decide to save them or to start a
# new measure.
class UIGraphPreview(QMainWindow):

    def __init__(self, bode_manager):  # Conecta los componentes del .ui realizado en QT con el programa en python
        QMainWindow.__init__(self)
        loadUi('graphpreview.ui', self)
        self.setWindowTitle("Graph Preview")
        self.ModuleWidget = self.graphwidget  # GraphWidget instance.
        self.PhaseWidget = self.phaseGraph  # GraphWidget instance.
        # Sets titles.
        self.ModuleWidget.title = "Module"
        self.PhaseWidget.title = "Phase"
        self.ModuleWidget.x_label = "f [Hz]"
        self.PhaseWidget.x_label = "f [Hz]"
        self.PhaseWidget.y_label = "° [deg]"
        self.ModuleWidget.y_label = "|H| [dB]"
        self.ModuleWidget.canvas.axes.set_title(self.ModuleWidget.title)
        self.PhaseWidget.canvas.axes.set_title(self.PhaseWidget.title)
        self.__fix_axes_titles_position__(self.ModuleWidget)
        self.__fix_axes_titles_position__(self.PhaseWidget)

        self.saveButton.clicked.connect(self.save_action)
        self.newBode.clicked.connect(self.new_bode)

        self.bode_manager = bode_manager

    def new_bode(self):
        self.close()
        self.bode_manager.start_over("")

    def plot_window(self):
        """
        Plots the Bode graph received.
        """
        self.__plot_graph__(self.bode_manager.bode.frequencies, self.bode_manager.bode.module,
                            self.ModuleWidget)
        self.__plot_graph__(self.bode_manager.bode.frequencies, self.bode_manager.bode.phase,
                            self.PhaseWidget)

    def __fix_axes_titles_position__(self, widget):
        """
        Axes titles configuration.
        :param widget: Widget to edit the titles. PhaseWidget or ModuleWidget.
        """
        self.__fix_y_title_position__(widget)
        self.__fix_x_title_position__(widget)

    def __fix_x_title_position__(self, widget):
        ticklabelpad = mpl.rcParams['xtick.major.pad']
        widget.canvas.axes.annotate(widget.x_label, xy=(1, 0), xytext=(20, -ticklabelpad),
                                    ha='left', va='top',
                                    xycoords='axes fraction', textcoords='offset points')

    def __fix_y_title_position__(self, widget):
        ticklabelpad = mpl.rcParams['ytick.major.pad']
        widget.canvas.axes.annotate(widget.y_label, xy=(0, 1), xytext=(-30, -ticklabelpad + 10),
                                    ha='left', va='bottom',
                                    xycoords='axes fraction', textcoords='offset points', rotation=0)


    def __plot_graph__(self, x_values, y_values, graph_widget):
        """
        Plots a graph in a graph widget with the values received. The plot is made in the form of a scatter graph.
        :param x_values: x axes values to plot.
        :param y_values: y axes values to plot.
        :param graph_widget: widget to plot the graph in. PhaseWidget or ModuleWidget.
        """
        graph_widget.canvas.axes.scatter(x_values,
                                         y_values,
                                         color='b')
        graph_widget.canvas.axes.set_xscale('log')
        graph_widget.canvas.axes.grid(True, which="both")

        graph_widget.canvas.draw()  # Redraws

    def save_action(self):
        """
        Creates a .csv file with the measurements values and saves it at a selected directory.
        """
        my_data = [['freqs', 'amp', 'phase']] # List of the rows to save in the file.

        for i in range(0, len(self.bode_manager.bode.frequencies)):
            my_data.append([str(self.bode_manager.bode.frequencies[i]),
                           str(self.bode_manager.bode.module[i]),
                           str(self.bode_manager.bode.phase[i])])

        folder_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.__save_csv__(folder_path, my_data, "auto_bode")
        self.errorLabel.setText("File saved. Format: freq, module, phase")

    def __save_csv__(self, folder_path, myData, name):
        """
        Finds the correct name for the file to be saved and saves it at the selected directory.
        :param folder_path: Directory to save the file at.
        :param myData: List of lists with the rows of values to save in the file.
        :param name: Base name of the file.
        """
        i = 1
        if os.path.isfile(folder_path + "/" + name + ".csv"):
            while os.path.isfile(folder_path + "/" + name + "(" + str(i) + ").csv"):
                i = i + 1
            myFile = open(folder_path + "/" + name + "(" + str(i) + ").csv", 'w')
        else:
            myFile = open(folder_path + "/" + name + ".csv", 'w')

        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(myData)
