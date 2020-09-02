from GraphStructures.GraphValues import GraphValues, GraphTypes
from GraphStructures.ToggleableGraph import ToggleableGraph

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from scipy import signal
import math

from GraphStructures.GraphValues import GraphValues, GraphTypes
from GraphStructures.ToggleableGraph import ToggleableGraph


class TransferenceFetching(QWidget):
    def __init__(self, window, *args, **kwargs):
        super(TransferenceFetching, self).__init__(*args, **kwargs)
        loadUi('GraphFetching/transfer.ui', self)
        self.user_inerfase = window
        self.finish.clicked.connect(self.analyzer)
        self.num_input.textChanged.connect(self.equation_draw)
        self.den_input.textChanged.connect(self.equation_draw)

    def transference_plot(self):
        self.show()

    def analyzer(self):
        numerator = self.num_input.text()
        denominator = self.den_input.text()
        """ Agarro los valores de los coeficientes"""
        coefficients_num = numerator.split(',')
        coefficients_den = denominator.split(',')
        try:
            """ Fisrt converting strings to numbers """
            num_list = [float(i) for i in coefficients_num]
            den_list = [float(i) for i in coefficients_den]
            """ Creating Lti item """
            transfer = signal.lti(num_list, den_list)
            """ Getting the bode values """
            freq, amp, phase = transfer.bode()
            freq = [(i/(2*math.pi)) for i in freq]  # Converting from radians to hertz
            """ Getting graph's name """
            label = self.labelName.text()
            self.labelName.setText("")
            if label == "":
                label = "Graph " + str((len(self.user_inerfase.graphicsToShow) + 1))

            graph_color = self.user_inerfase.get_next_color()
            """ Sending the information to the GraphManager """
            module_graph = ToggleableGraph(GraphValues(label, freq.copy(), amp.copy(), GraphTypes.BodeModule),
                                           self.user_inerfase.parent.transferenceCheck.isChecked())
            self.user_inerfase.add_graphic(module_graph, self.user_inerfase.transferenceKey, graph_color)

            phase_graph = ToggleableGraph(GraphValues(label, freq.copy(), phase.copy(), GraphTypes.BodePhase),
                                          self.user_inerfase.parent.transferenceCheck.isChecked())

            self.user_inerfase.add_graphic(phase_graph, self.user_inerfase.transferenceKey, graph_color)

        except ValueError:
            QMessageBox.warning(self, "Important", "Not numeric input", QMessageBox.Ok)

        self.close()
        self.equation.figure.clear()
        self.equation.canvas.draw()
        self.num_input.setText("")
        self.den_input.setText("")
        self.user_inerfase.draw()

    def equation_draw(self):
        """ First of all clear the place to draw """
        self.equation.figure.clear()

        """ Catching the new values """
        numerator = self.num_input.text()
        denominator = self.den_input.text()
        coefficients_num = numerator.split(',')
        coefficients_den = denominator.split(',')

        """ Create the string to be written in LaTex"""
        num_str = ""
        length = len(coefficients_num)
        for i in range(0, length):
            if (length - i) > 2:
                num_str += str(coefficients_num[i]) + ".s^" + str(length - 1 - i) + " + "
            elif (length - i) == 2:
                num_str += str(coefficients_num[i]) + ".s + "
            else:
                num_str += str(coefficients_num[i])
        if num_str == "":
            num_str = "-"
        den_str = ""
        length = len(coefficients_den)
        for i in range(0, length):
            if (length - i) > 2:
                den_str += str(coefficients_den[i]) + ".s^" + str(length - 1 - i) + " + "
            elif (length - i) == 2:
                den_str += str(coefficients_den[i]) + ".s + "
            else:
                den_str += str(coefficients_den[i])
        if den_str == "":
            den_str = "-"

        """ Writing the fraction in LaTex's style """
        equation = "$ \\frac{"+num_str+"}{"+den_str+"}$"
        self.equation.figure.text(0.1, 0.6, equation, fontsize=10)
        self.equation.canvas.draw()
