from enum import Enum

from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


class UIConfigMeas(QMainWindow):

    def __init__(self, bode_manager):
        QMainWindow.__init__(self)
        loadUi('BodeManagement/UIManagement/configureMeasurement.ui', self)
        self.setWindowTitle("Measurement Configuration")
        self.continueButton.clicked.connect(self.continue_action)
        self.backButton.clicked.connect(self.back_action)
        self.sweepTypeBox.currentIndexChanged.connect(self.sweep_type_changed)
        self.sweep_type = SweepTypes.linearSweep
        self.bode_manager = bode_manager
        self.measure_every = 1
        self.measurement_per_decade = 1
        self.multipliers = {
            "Hz": 1,
            "kHz": 1000,
            "MHz": 1000000
        }
        self.start_freq = None
        self.stop_freq = None

    def on_window_shown(self):
        self.start_freq = self.bode_manager.bode_configuration.wave_gen_config_params["startFreq"]
        self.stop_freq = self.bode_manager.bode_configuration.wave_gen_config_params["stopFreq"]
        self.update_values()

    def update_values(self):
        """
        Updates default values depending on the type of measurement.
        """
        if self.sweep_type == SweepTypes.linearSweep:
            self.measureSpinBox.setValue(100.00)
        elif self.sweep_type == SweepTypes.logarithmicSweep:
            self.measureSpinBox.setValue(20.00)
        self.update_labels()

    def update_labels(self):
        """
        Updates labels depending on the type of measurement.
        """
        if self.sweep_type == SweepTypes.linearSweep:
            self.measureTitleLabel.setText("Measure Every")
            self.measure_every = self.measureSpinBox.value() * self.multipliers[self.measMultiplier.currentText()]
        elif self.sweep_type == SweepTypes.logarithmicSweep:
            self.measureTitleLabel.setText("Measurements per decade")
            self.measurement_per_decade = self.measureSpinBox.value()

    def back_action(self):
        self.bode_manager.show_prev_window()

    def continue_action(self):
        error = False

        self.update_labels()
        meas_configuration = {
            "sweepType": self.sweep_type.value,
            "measureTick": self.measure_every,
            "establishmentTime": self.establishmentSpinBox.value()
        }
        if self.sweep_type == SweepTypes.linearSweep:
            if self.measure_every > (self.stop_freq - self.start_freq):
                error = True

        elif self.sweep_type == SweepTypes.logarithmicSweep:
            meas_configuration = {
                "sweepType": self.sweep_type.value,
                "measureTick": self.measurement_per_decade,
                "establishmentTime": self.establishmentSpinBox.value()
            }
        if error:
            self.errorLabel.setText("Invalid measuring step")
        else:
            self.errorLabel.setText("")

            self.close()

            self.bode_manager.bode_configuration.measure_config_params = meas_configuration
            self.bode_manager.show_next_window()

    def sweep_type_changed(self):
        """
        Updates ui components depending on the type of measurement.
        """
        for sweep in SweepTypes:
            if self.sweepTypeBox.currentText() == sweep.value:
                self.sweep_type = sweep
                if sweep == SweepTypes.logarithmicSweep:
                    self.measMultiplier.hide()
                    self.measureSpinBox.setDecimals(0)
                else:
                    self.measMultiplier.show()
                    self.measureSpinBox.setDecimals(2)

        self.update_values()


class SweepTypes(Enum):
    """ Sweep Types """
    linearSweep = "Lineal"
    logarithmicSweep = "Logarithmic"
    none = "No Sweep"
