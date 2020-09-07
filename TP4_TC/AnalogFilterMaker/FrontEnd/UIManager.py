import os
import pickle

from PyQt5.QtWidgets import *

from BackEnd.BackEnd import BackEnd
from FrontEnd.UIControl.FirstStage import FirstStage, QMessageBox
from FrontEnd.UIControl.SecondStage import SecondStage
from FrontEnd.UIControl.UIMainWindow import UIMainWindow
from FrontEnd.UIs.Testing.BackEndTesting import BackEndTesting
from FrontEnd.UIs.Testing.StagesManagerTesting import StagesManagerTesting
from StagesManager.StagesManager import StagesManager


class UIManager:
    def __init__(self):
        self.active_window = None
        self.back_end = BackEnd()
        self.stages_manager = StagesManager()
        self.list_of_windows = [FirstStage(self, self.back_end, self.stages_manager), SecondStage(self, self.back_end, self.stages_manager)]  # Sequence of windows to show
        self.window_iterator = -1
        self.project_path = None
        self.program_state = {
            "window_iterator": self.window_iterator,
            "active_window_configuration": {}
        }
        self.configuration_dicts = []
        for i in range (0, len(self.list_of_windows)):
            self.configuration_dicts.append(None)


    def begin(self):
        """
        Shows the first window (Main Window)
        """
        self.active_window = UIMainWindow(self)
        self.active_window.show()
        self.active_window.showMaximized()

    def next_window(self):
        """
        Closes the current active window and shows the next one from the window sequence.
        """
        if len(self.list_of_windows) > self.window_iterator + 1:
            if self.window_iterator > -1:
                self.configuration_dicts[self.window_iterator] = self.active_window.get_current_state_config()
            self.active_window.hide()
            self.window_iterator += 1
            self.active_window = self.list_of_windows[self.window_iterator]


            '''
            if self.window_iterator == 1 and self.active_window.i == 1:
                if self.configuration_dicts[self.window_iterator] is not None:
                    self.active_window.load_current_state(self.configuration_dicts[self.window_iterator])
            else:
            '''
            self.active_window.ui_manager = self
            self.active_window.backend = self.back_end
            self.active_window.stages_manager = self.stages_manager
            self.active_window.start()


    def previous_window(self):
        """
        Closes the current active window and shows the previous one from the window sequence.
        """
        if self.window_iterator > 0:
            self.active_window.hide()
            self.window_iterator -= 1
            self.active_window = self.list_of_windows[self.window_iterator]
            self.active_window.start()

            if self.configuration_dicts[self.window_iterator] is not None:
                self.active_window.load_current_state(self.configuration_dicts[self.window_iterator])

    def load_current_state(self):
        try:
            filename = QFileDialog.getOpenFileName(None, "Select Project File", os.getenv('HOME'), "Filter Design Tool Project File (*.fdtpf)")[0]
            configuration_dict = pickle.load(open(filename, "rb"))  # Loads the file
            self.project_path = filename
            self.active_window.hide()
            self.window_iterator  = configuration_dict["window_iterator"]
            self.configuration_dicts = configuration_dict["window_configurations"]
            self.active_window = self.list_of_windows[self.window_iterator]
            self.active_window.start()
            self.active_window.load_current_state(self.configuration_dicts[self.window_iterator])
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Couldn't open file")
            msg.setWindowTitle("Error")
            msg.exec_()

    def save_as_current_state(self):
        try:
            self.program_state["window_iterator"] = self.window_iterator
            self.configuration_dicts[self.window_iterator] = self.active_window.get_current_state_config()
            self.program_state["window_configurations"] = self.configuration_dicts
            # self.program_state["active_window_configuration"] = self.active_window.get_current_state_config()
            Save = self.program_state  # Saves the desired class AND a chosen attribute
            path = QFileDialog.getSaveFileName(None, 'Save Project File', os.getenv('HOME'), "Filter Design Tool Project File (*.fdtpf)")[0]
            pickle.dump(Save, open(path, "wb"))  # Creates the file and puts the data into the file
            self.project_path = path
        except:
             msg = QMessageBox()
             msg.setIcon(QMessageBox.Critical)
             msg.setText("Error")
             msg.setInformativeText("Couldn't save file")
             msg.setWindowTitle("Error")
             msg.exec_()

    def save_current_state(self):
        self.program_state["window_iterator"] = self.window_iterator
        self.configuration_dicts[self.window_iterator] = self.active_window.get_current_state_config()
        self.program_state["window_configurations"] = self.configuration_dicts
        #self.program_state["active_window_configuration"] = self.active_window.get_current_state_config()
        Save = self.program_state  # Saves the desired class AND a chosen attribute
        if self.project_path is not None:
            pickle.dump(Save, open(self.project_path, "wb"))  # Creates the file and puts the data into the file
        else:
            self.save_as_current_state()