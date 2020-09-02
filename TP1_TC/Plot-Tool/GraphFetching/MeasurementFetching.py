import math
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

from GraphStructures.GraphValues import GraphValues, GraphTypes
from GraphStructures.ToggleableGraph import ToggleableGraph


class MeasurementFetching(QDialog):
    def __init__(self, main_window, *args, **kwargs):
        super(MeasurementFetching, self).__init__(*args, **kwargs)
        """ Loading the 2 windows we will need"""
        self.chose_type = QWidget()
        loadUi("GraphFetching/inputType.ui", self.chose_type)
        self.select_name = QWidget()
        loadUi("GraphFetching/nombre.ui", self.select_name)

        """ Callback to define which type of input we will receive """
        self.chose_type.finish.clicked.connect(self.__input_type__)
        self.select_name.finish.clicked.connect(self.chooser)

        self.type = False
        self.file = ""
        self.window = main_window
        self.data = {"Frequency": [],
                     "Amplitude": [],
                     "Phase": []}  # Structure to store frequency, amplitude an phase

    def measurement_plot(self):
        self.chose_type.show()  # Start showing a window

    def __input_type__(self):
        self.chose_type.close()  # Hide select type window
        """ Select the file """
        self.file, _ = QFileDialog.getOpenFileName(self.window.parent, "Select measured plots", "C://",
                                                   "Bodes (*.xls , *.xlsx , *.csv)")

        """ Check the input type to load it correctly """
        input_type = self.chose_type.type_box.currentText()
        if self.file:
            ok = False
            if input_type == "Frecuencia | Vin | Vout":
                self.type = True
                ok = self.__process_data_amp_only__()
            elif input_type == "Frecuencia | Amplitud | Fase":
                self.type = False
                ok = self.__process_all_data__()
            """ If the data was well loaded, the programs continue"""
            if ok:
                filename = self.file.split('/').pop()
                instruction = self.select_name.instruction.text()
                instruction += " del archivo " + filename
                self.select_name.instruction.setText(instruction)
                self.select_name.show()

    def chooser(self):
        if self.type:
            self.__send_data_amp_only__()
        else:
            self.__send_complete_data__()

    def __send_data_amp_only__(self):
        """ Loading the graph name """
        label = self.select_name.label.text()
        self.select_name.label.setText("")
        if label == "":
            label = "Graph " + str((len(self.window.graphicsToShow) + 1))
        color_graph = self.window.get_next_color()
        """ Sending the graph to the GraphManager"""
        module_graph = ToggleableGraph(GraphValues(label, self.data["Frequency"].copy(), self.data["Amplitude"].copy(),
                                                   GraphTypes.BodeModule, True), self.window.parent.medCheck.isChecked())

        self.window.add_graphic(module_graph, self.window.medKey, color_graph)

        """ Resetting properties """
        self.select_name.close()
        self.select_name.label.setText("")
        self.select_name.instruction.setText("Ingrese un nombre para el gráfico")  # Reset the instruction label
        self.data["Frequency"] = []
        self.data["Amplitude"] = []

        """ Redraw window"""
        self.window.draw()

    def __send_complete_data__(self):
        """ Loading the graph name """
        label = self.select_name.label.text()
        self.select_name.label.setText("")
        if label == "":
            label = "Graph " + str((len(self.window.graphicsToShow) + 1))
        color_graph = self.window.get_next_color()

        """ Sending the graph to the GraphManager"""
        module_graph = ToggleableGraph(GraphValues(label, self.data["Frequency"].copy(), self.data["Amplitude"].copy(),
                                                   GraphTypes.BodeModule, True), self.window.parent.medCheck.isChecked())

        self.window.add_graphic(module_graph, self.window.medKey, color_graph)

        phase_graph = ToggleableGraph(GraphValues(label, self.data["Frequency"].copy(), self.data["Phase"].copy(),
                                                  GraphTypes.BodePhase, True), self.window.parent.medCheck.isChecked())

        self.window.add_graphic(phase_graph, self.window.medKey, color_graph)

        self.select_name.close()
        self.select_name.label.setText("")
        self.select_name.instruction.setText("Ingrese un nombre para el gráfico")  # Reset the instruction label
        self.data["Frequency"] = []
        self.data["Amplitude"] = []
        self.data["Phase"] = []

        self.window.draw()

    def __process_data_amp_only__(self):
        try:
            raw_data = None
            file, extension = self.file.split('.')

            if extension == "xlsx" or extension == "xls":
                raw_data = pd.read_excel(self.file, header=None, skiprows=1)
            elif extension == "csv":
                raw_data = pd.read_csv(self.file, header=None, skiprows=1)

            if raw_data.shape[1] is not 3:  # Check if the number of columns is ok
                raise ValueError

            for i in range(0, len(raw_data)):
                self.data["Frequency"].append(float("{0:.1f}".format(raw_data[0][i])))
                _vin_vo_ = raw_data[2][i] / raw_data[1][i]
                self.data["Amplitude"].append(20 * math.log(_vin_vo_, 10))
            return True

        except IOError:
            QMessageBox.question(self.window.parent, "Important", "¿Seguro que existe el archivo?", QMessageBox.Yes)
        except ValueError:
            QMessageBox.warning(self.window.parent, "Important", "Formato inválido, revise el archivo", QMessageBox.Ok)
        return False

    def __process_all_data__(self):
        try:
            raw_data = None
            file, extension = self.file.split('.')

            if extension == "xlsx" or extension == "xls":
                raw_data = pd.read_excel(self.file, header=None, skiprows=1)
            elif extension == "csv":
                raw_data = pd.read_csv(self.file, header=None, skiprows=1)

            if raw_data.shape[1] is not 3:  # Check if the number of columns is ok
                raise ValueError

            for i in range(0, len(raw_data)):
                self.data["Frequency"].append(float("{0:.1f}".format(raw_data[0][i])))
                self.data["Amplitude"].append(float("{0:.1f}".format(raw_data[1][i])))
                self.data["Phase"].append(float("{0:.1f}".format(raw_data[2][i])))
            return True

        except IOError:
            QMessageBox.question(self.window.parent, "Important", "¿Seguro que existe el archivo?", QMessageBox.Yes)
        except ValueError:
            QMessageBox.warning(self.window.parent, "Important", "Formato inválido, revise el archivo", QMessageBox.Ok)
        return False
