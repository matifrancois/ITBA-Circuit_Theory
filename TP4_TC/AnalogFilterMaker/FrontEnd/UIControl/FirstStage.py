import webbrowser

import matplotlib as mpl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import numpy as np
from FrontEnd.UIControl.FinalGraph import FinalGraph
from FrontEnd.UIs.FilterConfigurations.Config import Config
from FrontEnd.UIs.FilterConfigurations.Template import Template
from FrontEnd.UIs.UIConfigurations.ParameterLayout import DefaultRadioGroup


class FirstStage(QMainWindow):

    def __init__(self, ui_manager, backend, stages_manager):
        self.graph_widget = None
        self.ui_manager = ui_manager
        self.a = 0
        self.filters = {}
        self.backend = backend
        self.stages_manager = stages_manager
        self.filters_received, self.approximations_received = self.backend.get_util()

        self.showingGraphs = []

    def start(self):
        """
        Actions to perform when the window is shown.
        """
        QMainWindow.__init__(self)
        loadUi('FrontEnd/UIs/firststage.ui', self)

        self.setWindowTitle("Filter Design Tool")
        self.graph_widget = self.graphWidget
        self.comboFilter.clear()
        for filter in self.filters_received:
            self.comboFilter.addItem(filter)
            self.filters[filter] = Config(filter, self.filters_received[filter], self.approximations_received[filter])


        self.addApproxButton.clicked.connect(self.add_approx)
        self.removeApproxButton.clicked.connect(self.remove_approx)
        self.filterTypeLabel.clicked.connect(self.filter_type_label_clicked)
        self.approximationLabel.clicked.connect(self.approximation_label_clicked)
        self.parametersLabels.clicked.connect(self.parameters_label_clicked)
        self.comboFilter.currentIndexChanged.connect(self.update_filter_type)
        self.approxCombo.currentIndexChanged.connect(self.update_approximation)
        self.plotTemplateButton.clicked.connect(self.plot_template_button_clicked)
        self.toggleApprox.toggled.connect(self.toggle_approximation)
        self.editApproximationButton.clicked.connect(self.edit_approx)
        self.activeApproxsCombo.currentIndexChanged.connect(self.approx_combo_changed)
        self.save_as_project_button.clicked.connect(self.save_as_current_state_clicked)
        self.save_project_button.clicked.connect(self.save_current_state_clicked)
        self.toggleApprox.hide()
        self.fill_combo_graph()
        self.comboGraph.currentIndexChanged.connect(self.combo_graph_changed)
        self.load_project_button.clicked.connect(self.load_project_clicked)
        self.templateCheckBox.toggled.connect(self.template_toggled)
        self.nextButton.clicked.connect(self.next_stage)
        self.templateCheckBox.hide()
        self.group_box = DefaultRadioGroup(self.__ui_template_activation_)
        self.radioButtonsLayout.addWidget(self.group_box)
        self.templates = []
        self.update_filter_type()
        self.showMaximized()

    def next_stage(self):
        if (self.activeApproxsCombo.currentText() != ""):
            id = self.activeApproxsCombo.findText(self.activeApproxsCombo.currentText())
            backend_filter = self.backend.get_filter(id)
            self.stages_manager.load_filter(backend_filter)
            self.ui_manager.next_window()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("No approximation detected.")
            msg.setWindowTitle("Error")
            msg.exec_()

    def load_project_clicked(self):
        self.ui_manager.load_current_state()

    def load_current_state(self, configuration_dict):
        self.filname = configuration_dict["name"]
        self.imagetemp = configuration_dict["image"]
        self.backend.load_save_info(configuration_dict["backend"])
        self.graphPic.setPixmap(QPixmap(self.imagetemp))  # filter template image

        self.showingGraphs = []
        self.showingGraphs = configuration_dict["showing_graphs"]
        self.__update_active_approx_combo__()

        self.fill_combo_graph()

        if len(self.showingGraphs) == 0:
            self.toggleApprox.hide()

        self.__update_templates__()
        self._template_ploting_w_graphs_()
        self.redraw()

        self.comboFilter.currentIndexChanged.disconnect()
        index = self.comboFilter.findText(self.filname)
        self.comboFilter.setCurrentIndex(index)
        self.comboFilter.currentIndexChanged.connect(self.update_filter_type)

    def get_current_state_config(self):
        self.window_configuration = {}
        self.filter = self.filters[self.comboFilter.currentText()]
        requirements = []
        for requirement in self.filters[self.comboFilter.currentText()].parameter_list:
            requirements.append(requirement.get_value())
        self.window_configuration["showing_graphs"] = self.showingGraphs
        self.window_configuration["image"] = self.filter.template_image
        self.window_configuration["name"] = self.filter.name
        self.window_configuration["backend"] = self.backend.get_save_info()
        return self.window_configuration

    def combo_graph_changed(self):
        self.redraw_graphs()
        self._template_ploting_w_graphs_()

    def fill_combo_graph(self):
        self.comboGraph.clear()

        for graph in self.showingGraphs:
            for key in graph.graphs.keys():
                if self.comboGraph.findText(key) == -1:
                    self.comboGraph.addItem(key)

    def approx_combo_changed(self):
        for graph in self.showingGraphs:
            if graph.get_total_string() == self.activeApproxsCombo.currentText():
                if graph.enabled:
                    self.toggleApprox.setChecked(True)
                else:
                    self.toggleApprox.setChecked(False)

    def toggle_approximation(self):
        for graph in self.showingGraphs:
            if graph.get_total_string() == self.activeApproxsCombo.currentText():
                graph.toggle_graph(self.toggleApprox.isChecked())
                self.redraw()
        self.get_current_state_config()

    def edit_approx(self):
        approx_name = ""
        for graph in self.showingGraphs:
            if graph.get_total_string() == self.activeApproxsCombo.currentText():
                for property_tuple in graph.properties:
                    if property_tuple[0] == "Approximation":
                        approx_name = property_tuple[1]
                        index = self.approxCombo.findText(approx_name)
                        self.approxCombo.setCurrentIndex(index)
                    else:
                        self.filter = self.filters[self.comboFilter.currentText()]
                        for approximation in self.filter.approximation_list:
                            if approximation.name == approx_name:
                                for parameter in approximation.parameter_list:
                                    if parameter.name == property_tuple[0]:
                                        if property_tuple[1] == "Auto":

                                            parameter.rows[1].hide()
                                            parameter.check_box.show()
                                            parameter.check_box.setChecked(False)

                                            if not parameter.toggleable:
                                                parameter.check_box.hide()
                                        else:
                                            parameter.set_value(float(property_tuple[1]))
                                            parameter.check_box.show()
                                            parameter.check_box.setChecked(False)
                                            if not parameter.toggleable:
                                                parameter.check_box.hide()

    def template_toggled(self):
        if self.sender().isChecked():
            for template in self.templates:
                template.enabled = template.name == self.comboGraph.currentText()
        else:
            for template in self.templates:
                template.enabled = False
        self.redraw()

    def redraw(self):
        self.redraw_graphs()
        for template in self.templates:
            if template.enabled:
                mpl_squares = template.get_matplotlib_squares()
                if mpl_squares is not None:
                    for square in mpl_squares:
                        square.set_linewidth(3)
                        self.plot_rectangle(square, template)



    def plot_template_button_clicked(self):
        if len(self.showingGraphs) == 0:
            self.__update_templates__()

        else:
            self._template_ploting_w_graphs_()


    def _template_ploting_w_graphs_(self):

        self.group_box.hide()

        self.any_coincidence = False

        for template in self.templates:
            coincidence = template.name == self.comboGraph.currentText()
            if self.templateCheckBox.isChecked():
                template.enabled = coincidence
            if coincidence:
                self.any_coincidence = True

        if self.any_coincidence:
            self.templateCheckBox.show()
            self.plotTemplateButton.setText("Toggle Template ->")
            self.plotTemplateButton.setCheckable(False)
            self.plotTemplateButton.setStyleSheet("font: 63 10pt; color:rgb(255, 255, 255); border: 0px solid blue;")
        else:
            self.templateCheckBox.hide()
            self.plotTemplateButton.setText("Plot Template")
            self.plotTemplateButton.setCheckable(True)
            self.plotTemplateButton.setStyleSheet("font: 63 10pt; color:rgb(255, 255, 255); padding: 8px; bottom-margin:3px;")
        self.redraw()

    def __update_templates__(self, appoximation=None):
        self.filter = self.filters[self.comboFilter.currentText()]
        dict = self.filter.make_feature_dictionary()
        self.templates_dict = self.__ask_for_templates__([self.filter.name, dict], appoximation)
        self.templates = []
        for key in self.templates_dict.keys():
            self.templates.append(Template(key, self.templates_dict[key], False))
        self.group_box.clear_layout()
        for template in self.templates:
            self.group_box.add_radio_button(template.name)
        self.group_box.add_radio_button("None")
        self.group_box.first_activation()
        self.__ui_template_activation_()

    def __ui_template_activation_(self):
        group_name = self.group_box.enabled_text
        for template in self.templates:
            template.enabled = template.name == group_name

        self.redraw()
        self.templateCheckBox.hide()

    def __ask_for_templates__(self, param_list, approximation=None):
        validated, error_string = self.backend.validate_filter(param_list)
        if validated:
            templates = self.backend.get_template(param_list, approximation)
            return templates
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText(error_string)
            msg.setWindowTitle("Error")
            msg.exec_()
            return None

    def save_as_current_state_clicked(self):
        self.ui_manager.save_as_current_state()

    def save_current_state_clicked(self):
        self.ui_manager.save_current_state()

    def approximation_label_clicked(self):
        webbrowser.open('http://dsp-book.narod.ru/HFTSP/8579ch12.pdf')

    def parameters_label_clicked(self):
        webbrowser.open('https://electronicspani.com/electric-filter-types-of-filter/')

    def filter_type_label_clicked(self):
        webbrowser.open('https://www.allaboutcircuits.com/technical-articles/an-introduction-to-filters/')

    def update_filter_type(self):
        """
        Changes the filter template image and requirements whenever the current selected filter type is changed.
        """
        self.comboGraph.clear()
        self.showingGraphs = []
        self.__update_active_approx_combo__()
        self.templateCheckBox.setChecked(True)
        self.templateCheckBox.hide()
        self.redraw_graphs()
        # update plot
        self.backend.reset()

        try:
            for filters in self.filters.values():  # Clearing requirement widgets
                for parameters in filters.parameter_list:
                    parameters.setParent(None)
                for approx in filters.approximation_list:
                    for parameter in approx.parameter_list:
                        parameter.setParent(None)
        except:
            a = 0


        self.filter = self.filters[self.comboFilter.currentText()]
        self.approxCombo.clear()

        for approximation in self.filter.approximation_list:
            self.approxCombo.addItem(approximation.name)

        self.update_approximation()
        self.graphPic.setPixmap(QPixmap(self.filter.template_image))  # filter template image

        self.clear_layout(self.configurationLayout)
        for parameter in self.filter.parameter_list:  # Refilling requierement widgets
            self.configurationLayout.addWidget(parameter)
        self.configurationLayout.addStretch(50)  # space
        if len(self.showingGraphs) == 0:
            self.toggleApprox.hide()

        self.__update_templates__()
        self._template_ploting_w_graphs_()

    def update_approximation(self):
        for filters in self.filters.values():  # Clearing requirement widgets
            for approx in filters.approximation_list:
                for parameter in approx.parameter_list:
                    parameter.setParent(None)
        self.filter = self.filters[self.comboFilter.currentText()]
        self.clear_layout(self.approxConfigurationLayout)

        for approximation in self.filter.approximation_list:
            if approximation.name == self.approxCombo.currentText():
                for parameter in approximation.parameter_list:
                    self.approxConfigurationLayout.addWidget(parameter)
        self.configurationLayout.addStretch(2)  # space
        self.show()

    def remove_approx(self):
        """
        Removes graphs and text when an active approximation is removed by the user.
        """
        if self.activeApproxsCombo.currentText() is not None or self.activeApproxsCombo.currentText() != "":
            for approx in self.showingGraphs:
                if approx.get_total_string() == self.activeApproxsCombo.currentText():
                    id = self.activeApproxsCombo.findText(self.activeApproxsCombo.currentText())
                    self.backend.del_filter(id)
                    self.showingGraphs.remove(approx)
            self.fill_combo_graph()
            self.__update_active_approx_combo__()
            self.redraw_graphs()
        if len(self.showingGraphs) == 0:
            self.toggleApprox.hide()


    def add_approx(self):
        """
        Appends user selected approximation to active approximations and applies it to the filter.
        """
        self.toggleApprox.show()
        properties = []
        self.graphics_returned = []
        self.filter = self.filters[self.comboFilter.currentText()]
        dict = self.filter.make_feature_dictionary()
        validated, error_string = self.backend.validate_filter([self.filter.name, dict])
        approx = None
        if validated:
            for approximation in self.filter.approximation_list:
                if approximation.name == self.approxCombo.currentText():
                    properties.append(["Approximation", approximation.name])
                    for prop in approximation.parameter_list:

                        if not prop.toggleable or prop.check_box.isChecked():
                            properties.append([prop.name, str(prop.get_value())])
                        else:
                            properties.append([prop.name, "Auto"])
                    self.graphics_returned = self.backend.get_graphics([self.filter.name, dict], [approximation.name,
                                                                                          approximation.make_approx_dict(),
                                                                                          approximation.extra_combos])
                    approx = approximation

                    new_graph = FinalGraph(self.graphics_returned, properties, True, id)

                    self.showingGraphs.append(new_graph)
            self.fill_combo_graph()
            self.__update_active_approx_combo__()
            self.__update_templates__([approx.name, approx.make_approx_dict(),
                                       approx.extra_combos])
            self.redraw_graphs()
            self._template_ploting_w_graphs_()

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText(error_string)
            msg.setWindowTitle("Error")
            msg.exec_()


    def __update_active_approx_combo__(self):
        self.activeApproxsCombo.clear()
        i = 0
        for approx in self.showingGraphs:
            approx.id = i
            i += 1
            self.activeApproxsCombo.addItem(approx.get_total_string())
        self.activeApproxsCombo.setCurrentIndex(self.activeApproxsCombo.count() - 1)

    def clear_layout(self, layout):
        """
        Clears widgets from a layout.
        :param layout: layout to clear
        """
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()

    def plot_rectangle(self, square, template):

        self.graph_widget.canvas.axes.set_title(self.comboGraph.currentText(), color="w")
        self.graph_widget.canvas.axes.set_xscale('log')
        self.graph_widget.canvas.axes.grid(True, which="both")
        self.graph_widget.canvas.axes.add_patch(square)
        axes = template.find_axes_limits()
        self.graph_widget.canvas.axes.set_xlim(axes[0])
        self.graph_widget.canvas.axes.set_ylim(axes[1])
        self.graph_widget.canvas.draw()  # Redraws

    def redraw_graphs(self):
        try:
            self.graph_widget.canvas.axes.clear()
            self.graph_widget.canvas.axes.set_title(self.comboGraph.currentText(), color="w")

            self.graph_widget.canvas.axes.grid(True, which="both")

            self.graph_widget.canvas.draw()  # Redraws

            for graph in self.showingGraphs:
                if graph.enabled:
                    graph_values = graph.graphs[self.comboGraph.currentText()]
                    if graph_values is not None:
                        self.__plot_graph__(graph_values, "ID: " + str(graph.id) + ". ")

                        self.graph_widget.canvas.axes.grid(True, which="both")
                        self.graph_widget.canvas.axes.set_title(self.comboGraph.currentText(), color="w")
                        self.graph_widget.canvas.draw()  # Redraws
        except:
            a = 0

    def __plot_graph__(self, graph, legend_string):

        #self.graph_widget.canvas.axes.ticklabel_format(useOffset=False)

        #self.__fix_axes_titles_position__(self.graph_widget, graph[1][0], graph[1][1])
        for graph_data in graph[0]:
            if graph_data.log:
                self.graph_widget.canvas.axes.set_xscale('log')
            complete_legend = legend_string
            if graph_data.extra_information != "":
                complete_legend += "-" + graph_data.extra_information
            if not graph_data.scattered:
                self.graph_widget.canvas.axes.set_xlabel(graph[1][0])

                self.graph_widget.canvas.axes.set_ylabel(graph[1][1])
                self.graph_widget.canvas.axes.axis('auto')
                self.graph_widget.canvas.axes.yaxis.label.set_color('white')
                self.graph_widget.canvas.axes.xaxis.label.set_color('white')
                self.graph_widget.canvas.axes.tick_params(direction='out', length=1, width=1, labelsize=8, colors='w')
                if not graph_data.x_marks:
                    self.graph_widget.canvas.axes.plot(graph_data.x_values, graph_data.y_values, label=complete_legend)
                else:
                    self.graph_widget.canvas.axes.plot(graph_data.x_values, graph_data.y_values, marker='x',
                                                       label=complete_legend)

            else:

                r = 1.5 * np.amax(np.concatenate((graph_data.x_values, graph_data.y_values, [1])))
                self.graph_widget.canvas.axes.yaxis.label.set_color('black')
                self.graph_widget.canvas.axes.xaxis.label.set_color('black')
                self.__fix_axes_titles_position__(self.graph_widget, graph[1][0], graph[1][1])
                self.graph_widget.canvas.axes.axis('scaled')
                self.graph_widget.canvas.axes.axis([-1.5*r, r / 5, -r, r])
                self.graph_widget.canvas.axes.spines['left'].set_position('zero')
                self.graph_widget.canvas.axes.spines['right'].set_color('none')
                self.graph_widget.canvas.axes.spines['bottom'].set_position('zero')
                self.graph_widget.canvas.axes.spines['top'].set_color('none')
                self.graph_widget.canvas.axes.tick_params(direction='out', length=1, width=1, labelsize=8, colors='k')
                # self.z_p_diagram.canvas.axes.xaxis.set_ticks_position('bottom')
                # self.z_p_diagram.canvas.axes.yaxis.set_ticks_position('left')
                n_array_text = []
                for n in graph_data.n_array:
                    string_gen = ""
                    if n>1:
                        string_gen += str(n)
                    n_array_text.append(string_gen)
                if not graph_data.x_marks:
                    self.graph_widget.canvas.axes.scatter(graph_data.x_values, graph_data.y_values,
                                                          label=complete_legend)
                    for i in range(0, len(n_array_text)):
                        self.graph_widget.canvas.axes.annotate(n_array_text[i], (graph_data.x_values[i], graph_data.y_values[i]))
                else:
                    self.graph_widget.canvas.axes.scatter(graph_data.x_values, graph_data.y_values, marker='x',
                                                          label=complete_legend)
                    for i in range(0, len(n_array_text)):
                        self.graph_widget.canvas.axes.annotate(n_array_text[i], (graph_data.x_values[i], graph_data.y_values[i]))
        self.graph_widget.canvas.axes.legend(loc='best')
        self.graph_widget.figure.tight_layout()


    # Funciones que configuran y muestran los titulos de los ejes.
    def __fix_axes_titles_position__(self, widget, label_x, label_y):
        self.__fix_y_title_position__(widget, label_y)
        self.__fix_x_title_position__(widget, label_x)

    def __fix_x_title_position__(self, widget, label):
        ticklabelpad = mpl.rcParams['xtick.major.pad']
        widget.canvas.axes.annotate(label, xy=(1, 0), xytext=(-ticklabelpad * 5, 0),
                                    ha='right', va='top',
                                    xycoords='axes fraction', rotation=0, color="w", size=10,
                                    textcoords='offset points')

    def __fix_y_title_position__(self, widget, label):
        ticklabelpad = mpl.rcParams['ytick.major.pad']
        widget.canvas.axes.annotate(label, xy=(0, 1), xytext=(-ticklabelpad * 5, -ticklabelpad * 30),
                                    ha='left', va='bottom', size=10,
                                    xycoords='axes fraction', color="w", rotation=90, textcoords='offset points')
