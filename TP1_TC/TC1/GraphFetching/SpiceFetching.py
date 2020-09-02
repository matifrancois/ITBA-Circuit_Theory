from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

from GraphStructures.GraphValues import GraphValues, GraphTypes
from GraphStructures.ToggleableGraph import ToggleableGraph


class SpiceFetching(QWidget):
    def __init__(self, window, *args, **kwargs):
        super(SpiceFetching, self).__init__(*args, **kwargs)

        self.window = window
        self.file = ""
        self.f = []
        self.amp = []
        self.phase = []
        """ Create de window from the UI file"""
        loadUi("GraphFetching/nombre.ui", self)

        """ Link callback to analyze the information """
        self.finish.clicked.connect(self.process_data)

    def spice_plot(self):
        """ Fisrt function to be called after clicking the spice button in the main window """
        self.file, _ = QFileDialog.getOpenFileName(self.window.parent, "Select LTSpice plots", "C://", "Bodes (*.txt)")

        """ Checked whether the file is an appropriate one"""
        if self.__parse_file__():
            """ If a file is selected correct the instruction in the window and show it"""
            if self.file:
                filename = self.file.split('/').pop()
                instruction = self.instruction.text()
                instruction += " del archivo "+ filename
                self.instruction.setText(instruction)
                self.show()

    def __parse_file__(self):
        try:
            """ At first we try to open the file """
            file = open(self.file, "r")
            if file.mode is not "r":
                print("ERROR")
                return False
            """ Catch every line from the file"""
            lines = file.readlines()
            del lines[0]  # Throw away the first line, labels of the columns
            for string in lines:
                freq, value = string.split()
                amp_, phase_ = value[1:-2].split(',')  # The [1:-2] eliminates the ( ) from the string
                self.f.append(float(freq))
                self.amp.append(float(amp_[:-2]))  # Eliminates the dB unit
                self.phase.append(float(phase_))
            """ We closed the file after using it"""
            file.close()
            return True
        except IOError:
            QMessageBox.question(self.window.parent, "Important", "¿Seguro que existe el archivo?", QMessageBox.Yes)
        except ValueError:
            QMessageBox.warning(self.window.parent, "Important", "Formato inválido, revise el archivo", QMessageBox.Ok)
        return False

    def process_data(self):
        """ Final step before showing the graphic """
        label = self.label.text()  # Catching the name
        self.label.setText("")  # Cleaning the LineEdit for next time

        if label == "":  # If no label is enter, a default one is generated
            label = "Graph " + str((len(self.window.graphicsToShow)+1))

        color_graph = self.window.get_next_color()  # Color for the graphic is requested

        """ Loading the graphics to de GraphManager """
        module_graph = ToggleableGraph(GraphValues(label, self.f.copy(), self.amp.copy(), GraphTypes.BodeModule),
                                       self.window.parent.spiceCheck.isChecked())
        self.window.add_graphic(module_graph, self.window.spiceKey, color_graph)

        phase_graph = ToggleableGraph(GraphValues(label, self.f.copy(), self.phase.copy(), GraphTypes.BodePhase),
                                      self.window.parent.spiceCheck.isChecked())

        self.window.add_graphic(phase_graph, self.window.spiceKey, color_graph)

        """ Resetting some useful things """
        self.instruction.setText("Ingrese un nombre para el gráfico")  # Reset the instruction label
        self.label.setText("")
        self.close()  # Closing the name window
        self.f = []
        self.amp = []
        self.phase = []

        self.window.draw()  # Telling the GraphManager to be redraw
