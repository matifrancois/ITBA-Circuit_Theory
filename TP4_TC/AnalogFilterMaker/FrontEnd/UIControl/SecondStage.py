from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QRadioButton, QWidget, QVBoxLayout, QMessageBox
from PyQt5.uic import loadUi
from sympy.physics.quantum.tests.test_circuitplot import mpl
import numpy as np
from BackEnd.BackEnd import BackEnd
from FrontEnd.UIs.Testing.BackEndTesting import BackEndTesting
from FrontEnd.UIs.UIConfigurations.StagesUILayout import StagesUILayout, HorizontalParameter
from StagesManager.StagesManager import StagesManager, ShowType


class SecondStage(QMainWindow):

    def __init__(self, ui_manager, backend, stages_manager):
        self.showing_options = []
        self.all_loaded = False
        self.param_vbox = QVBoxLayout()
        self.illegal_zeros_titles = []
        self.illegal_pole_titles = []
        self.graph_widget = None
        self.ui_manager = ui_manager
        self.a = 0
        self.filters = {}
        self.backend = backend
        self.stages_manager = stages_manager


    def start(self):
        QMainWindow.__init__(self)
        loadUi('FrontEnd/UIs/secondstage.ui', self)
        self.setWindowTitle("Filter Design Tool")
        self.__place_button_images__()
        self.__define_showing_group__()
        self.graph_widget = self.graphWidget
        self.stages_ui_layout = StagesUILayout(self.selected_amount_changed)
        self.stagesLayout.setWidget(self.stages_ui_layout)
        self.create_button.clicked.connect(self.create_clicked)
        self.deleteButton.clicked.connect(self.delete_stages)
        self.autostage.clicked.connect(self.auto_stage)
        self.reloadv.clicked.connect(self.update_rd)
        self.nextButton.clicked.connect(self.right_shift)
        self.backButton.clicked.connect(self.left_shift)
        self.prev_window.clicked.connect(self.prev_window_clicked)

        self.goGain.clicked.connect(self.set_gain)
        self.saveButton.clicked.connect(self.ui_manager.save_current_state)
        self.saveAsButton.clicked.connect(self.ui_manager.save_as_current_state)
        self.loadButton.clicked.connect(self.ui_manager.load_current_state)
        self.__plot_p_z_graph__(self.stages_manager.get_z_p_plot())
        self.poles_and_zeros_dict = self.stages_manager.get_z_p_dict()
        self.__fill_poles_and_zeros_combos__()
        self.param_group_box.setLayout(self.param_vbox)
        self.__redefine_const_params_()
        self.selected_amount_changed()
        self.showMaximized()


    def get_current_state_config(self):
        self.window_configuration = {}
        self.window_configuration["back"] = self.backend
        self.window_configuration["stages"] = self.stages_manager

        return self.window_configuration

    def load_current_state(self, configuration_dict):
        self.backend = configuration_dict["back"]
        self.stages_manager = configuration_dict["stages"]

        self.__plot_p_z_graph__(self.stages_manager.get_z_p_plot())
        self.poles_and_zeros_dict = self.stages_manager.get_z_p_dict()
        self.__fill_poles_and_zeros_combos__()
        self.stages_ui_layout.delete_all_stages()
        self.__reload_stages__()
        self.__redraw__()


    def prev_window_clicked(self):
        self.ui_manager.previous_window()


    def update_rd(self):
        validated, value = self.stages_manager.get_dr(self.vminSpin.value(), self.vmaxSpin.value())
        if validated == False:
            self.__show_error__(value)
        else:
            self.rd.setText(value)
            self.__redefine_const_params_()

    def __show_error__(self, error):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(error)
        msg.setWindowTitle("Error")
        msg.exec_()


    def selected_amount_changed(self):
        self.__redraw__()
        self.stages_manager.set_selected(self.stages_ui_layout.get_selected_ids_array())

        if self.stages_ui_layout.get_number_of_checked() == 1:
            self.gainSpin.show()
            self.goGain.setText("Set Gain")
            self.goGain.setStyleSheet("font: 63 9pt; color:rgb(255, 255, 255);")
            self.__redefine_const_params_()

        else:
            self.gainSpin.hide()
            self.goGain.setText("N/A")
            self.goGain.setStyleSheet("font: 63 10pt;color:rgb(255, 255, 255);border: 0px solid blue;")



    def __redefine_const_params_(self):
        params = self.stages_manager.get_const_data(self.stages_ui_layout.get_selected_ids_array(),self.vminSpin.value(), self.vmaxSpin.value())
        self.clear_layout(self.param_vbox)
        for key in params.keys():
            self.param_vbox.addWidget(HorizontalParameter(key, params[key][0], params[key][1]))
        self.__redraw__()

    def set_gain(self):
        self.stages_manager.set_gain(self.stages_ui_layout.get_selected_ids_array()[0], self.gainSpin.value())
        self.__redefine_const_params_()

    def right_shift(self):
        if self.stages_ui_layout.get_number_of_checked() > 0:
            if self.stages_manager.shift_stages(self.stages_ui_layout.get_selected_ids_array(), False):
                self.stages_ui_layout.delete_all_stages()
                self.__reload_stages__()
                self.__redraw__()

    def left_shift(self):
        if self.stages_ui_layout.get_number_of_checked() > 0:
            if self.stages_manager.shift_stages(self.stages_ui_layout.get_selected_ids_array(), True):
                self.stages_ui_layout.delete_all_stages()
                self.__reload_stages__()
                self.__redraw__()

    def __plot_poles_and_zeros__(self):
        z_p_plot = self.stages_manager.get_z_p_plot()
        self.__plot_p_z_graph__(z_p_plot)

    def __plot_p_z_graph__(self, graphs):

        self.z_p_diagram.canvas.axes.xaxis.label.set_color('black')

        self.z_p_diagram.canvas.axes.ticklabel_format(useOffset=False)

        self.z_p_diagram.canvas.axes.grid(True, which="both")
        self.z_p_diagram.canvas.axes.yaxis.label.set_color('black')
        self.__fix_axes_titles_position__(self.z_p_diagram, graphs[1][0], graphs[1][1])
        for graph_data in graphs[0]:
            if graph_data.log:
                self.z_p_diagram.canvas.axes.set_xscale('log')
            n_array_text = []
            for n in graph_data.n_array:
                string_gen = ""
                if n > 1:
                    string_gen += str(n)
                n_array_text.append(string_gen)


            r = 1.5 * np.amax(np.concatenate((graph_data.x_values, graph_data.y_values, [1])))
            self.z_p_diagram.canvas.axes.axis('scaled')
            self.z_p_diagram.canvas.axes.axis([-1.5*r, r / 5, -r, r])
            self.z_p_diagram.canvas.axes.spines['left'].set_position('zero')
            self.z_p_diagram.canvas.axes.spines['right'].set_color('none')
            self.z_p_diagram.canvas.axes.spines['bottom'].set_position('zero')
            self.z_p_diagram.canvas.axes.spines['top'].set_color('none')


            if not graph_data.x_marks:
                self.z_p_diagram.canvas.axes.scatter(graph_data.x_values, graph_data.y_values)
                for i in range(0, len(n_array_text)):
                    self.z_p_diagram.canvas.axes.annotate(n_array_text[i],
                                                          (graph_data.x_values[i], graph_data.y_values[i]))
            else:
                self.z_p_diagram.canvas.axes.scatter(graph_data.x_values, graph_data.y_values, marker='x')
                for i in range(0, len(n_array_text)):
                    self.z_p_diagram.canvas.axes.annotate(n_array_text[i],
                                                          (graph_data.x_values[i], graph_data.y_values[i]))


        self.z_p_diagram.figure.tight_layout()



    # Funciones que configuran y muestran los titulos de los ejes.
    def __fix_axes_titles_position__(self, widget, label_x, label_y):
        #widget.canvas.axes.legend.remove()
        self.__fix_y_title_position__(widget, label_y)
        self.__fix_x_title_position__(widget, label_x)

    def __fix_x_title_position__(self, widget, label):
        ticklabelpad = mpl.rcParams['xtick.major.pad']
        widget.canvas.axes.annotate(label, xy=(1, 0), xytext=(-ticklabelpad*5, 0),
                                    ha='right', va='top',
                                    xycoords='axes fraction', rotation=0, color="w",size=10, textcoords='offset points')

    def __fix_y_title_position__(self, widget, label):
        ticklabelpad = mpl.rcParams['ytick.major.pad']
        widget.canvas.axes.annotate(label, xy=(0, 1), xytext=(-ticklabelpad*5, -ticklabelpad*30),
                                    ha='left', va='bottom',size=10,
                                    xycoords='axes fraction', color="w", rotation=90, textcoords='offset points')

    def delete_stages(self):
        if self.stages_ui_layout.get_number_of_checked() > 0:
            self.stages_manager.delete_stages(self.stages_ui_layout.get_selected_ids_array())
            self.stages_ui_layout.delete_all_stages()
            self.__reload_stages__()
            self.__redraw__()
            self.__plot_p_z_graph__(self.stages_manager.get_z_p_plot())
            self.poles_and_zeros_dict = self.stages_manager.get_z_p_dict()
            self.__fill_poles_and_zeros_combos__()

    def auto_stage(self):
        self.stages_manager.auto_max_rd(self.vminSpin.value(), self.vmaxSpin.value())
        self.stages_ui_layout.delete_all_stages()
        self.__reload_stages__()
        self.update_rd()
        self.__redraw__()

    def create_clicked(self):
        if (self.combo1.currentText() not in self.illegal_pole_titles) and (self.combo2.currentText() not in self.illegal_zeros_titles):
            validated, strerr = self.stages_manager.add_stage(self.combo1.currentText(), self.combo2.currentText())
            if validated:
                self.stages_ui_layout.delete_all_stages()
                self.__reload_stages__()
                self.__redraw__()
                self.__plot_p_z_graph__(self.stages_manager.get_z_p_plot())
                self.poles_and_zeros_dict = self.stages_manager.get_z_p_dict()
                self.__fill_poles_and_zeros_combos__()
                self.__redefine_const_params_()
            else:
                self.__show_error__(strerr)
        else:
            self.__show_error__("Illegal pole or zero selection")

    def __reload_stages__(self, ):
        current_stages, selected = self.stages_manager.get_stages()
        i = 0
        for stage in current_stages:
            if len(selected) > i:
                sel = selected [i]
            else:
                sel = True
            self.stages_ui_layout.add_stage(stage,i, sel )
            i+=1

    def __fill_poles_and_zeros_combos__(self):
        # self.comboFilter.model().item(1).setEnabled(False)
        self.combo1.clear()
        self.combo2.clear()
        self.combo2.addItem("")
        keys = list(self.poles_and_zeros_dict.keys())
        self.title_combo_1.setText(keys[0])
        self.title_combo_2.setText(keys[1])

        for i in range(0, 2):
            for key in self.poles_and_zeros_dict[keys[i]]:
                if i == 0:
                    self.combo1.addItem(key)
                    self.combo1.model().item(self.combo1.findText(key)).setEnabled(False)
                    self.illegal_pole_titles.append(key)
                    for sing in self.poles_and_zeros_dict[keys[i]][key]:
                        self.combo1.addItem(sing.get_msg())
                        if sing.used:
                            self.combo1.model().item(self.combo1.findText(sing.get_msg())).setEnabled(False)
                            self.illegal_pole_titles.append(sing.get_msg())
                if i == 1:
                    self.combo2.addItem(key)
                    self.combo2.model().item(self.combo2.findText(key)).setEnabled(False)
                    self.illegal_zeros_titles.append(key)
                    for sing in self.poles_and_zeros_dict[keys[i]][key]:
                        self.combo2.addItem(sing.get_msg())
                        if sing.used:
                            self.combo2.model().item(self.combo2.findText(sing.get_msg())).setEnabled(False)
                            self.illegal_zeros_titles.append(sing.get_msg())

    def __place_button_images__(self):
        pixmap = QPixmap("FrontEnd/UIs/figs/button_figs/next.png")
        next_icon = QIcon(pixmap)
        pixmap2 = QPixmap("FrontEnd/UIs/figs/button_figs/prev.png")
        back_icon = QIcon(pixmap2)
        pixmap3 = QPixmap("FrontEnd/UIs/figs/button_figs/delete.png")
        delete_icon = QIcon(pixmap3)
        self.nextButton.setIcon(next_icon)
        self.backButton.setIcon(back_icon)
        self.deleteButton.setIcon(delete_icon)

    def __define_showing_group__(self):
        self.showing_options.clear()
        hbox = QHBoxLayout()
        self.showing_group.setLayout(hbox)

        for show_type in ShowType:
            radiobutton = QRadioButton(show_type.name)
            hbox.addWidget(radiobutton)
            radiobutton.setStyleSheet("font: 63 7pt ; color:rgb(255, 255, 255);")
            self.showing_options.append(radiobutton)
            radiobutton.clicked.connect(self.__redraw__)

        self.showing_options[0].setChecked(True)




    def clear_layout(self, layout):
        """
        Clears widgets from a layout.
        :param layout: layout to clear
        """
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()


    def __redraw__(self):
        show_type = None
        for radio_but in self.showing_options:
            if radio_but.isChecked():
                show_type = radio_but.text()

        #if len(self.stages_ui_layout.get_selected_ids_array() )> 0:
        graphs = self.stages_manager.get_stages_plot(self.stages_ui_layout.get_selected_ids_array(), show_type)
        self.__plot_graph__(graphs)



    def __plot_graph__(self, graph):
        self.graph_widget.canvas.axes.clear()
        self.graph_widget.canvas.axes.set_xlabel(graph[1][0])
        self.graph_widget.canvas.axes.xaxis.label.set_color('white')
        self.graph_widget.canvas.axes.set_ylabel(graph[1][1])
        #self.graph_widget.canvas.axes.ticklabel_format(useOffset=False)
        self.graph_widget.canvas.axes.yaxis.label.set_color('white')
        # self.__fix_axes_titles_position__(self.graph_widget, graph[1][0], graph[1][1])
        self.graph_widget.canvas.axes.grid(True, which="both")
        for graph_data in graph[0]:
            if graph_data.log:
                self.graph_widget.canvas.axes.set_xscale('log')

            if not graph_data.scattered:
                if not graph_data.x_marks:
                    self.graph_widget.canvas.axes.plot(graph_data.x_values, graph_data.y_values, label=graph_data.extra_information)
                else:
                    self.graph_widget.canvas.axes.plot(graph_data.x_values, graph_data.y_values, marker='x',
                                                       label=graph_data.extra_information)

            else:
                n_array_text = []
                for n in graph_data.n_array:
                    string_gen = ""
                    if n > 1:
                        string_gen += str(n)
                    n_array_text.append(string_gen)
                if not graph_data.x_marks:
                    self.graph_widget.canvas.axes.scatter(graph_data.x_values, graph_data.y_values,
                                                          label=graph_data.extra_information)
                    for i in range(0, len(n_array_text)):
                        self.graph_widget.canvas.axes.annotate(n_array_text[i],
                                                               (graph_data.x_values[i], graph_data.y_values[i]))
                else:
                    self.graph_widget.canvas.axes.scatter(graph_data.x_values, graph_data.y_values, marker='x',
                                                          label=graph_data.extra_information)
                    for i in range(0, len(n_array_text)):
                        self.graph_widget.canvas.axes.annotate(n_array_text[i],
                                                               (graph_data.x_values[i], graph_data.y_values[i]))
        self.graph_widget.canvas.axes.legend(loc='best')
        self.graph_widget.figure.tight_layout()
        self.graph_widget.canvas.draw()






