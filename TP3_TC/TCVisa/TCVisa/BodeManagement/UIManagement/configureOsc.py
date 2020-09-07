from enum import Enum

from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


class UIConfigOsc(QMainWindow):

    def __init__(self, bode_manager,
                 visa_manager):
        QMainWindow.__init__(self)
        loadUi('BodeManagement/UIManagement/configureOsc.ui', self)
        self.setWindowTitle("Oscilloscope Configuration")
        self.continueButton.clicked.connect(self.continue_action)
        self.visa_string = ""
        self.channel_in = ChannelTypes.none
        self.trigger_level = 0.1
        self.channel_out = ChannelTypes.none
        self.acquire_type = AcquireTypes.none
        self.trigger_source = TriggerSources.none
        self.probe_in = ProbeTypes.x1.value[1]
        self.probe_out = ProbeTypes.x1.value[1]
        self.high_freq_reject = False
        self.noise_reject = False
        self.bode_manager = bode_manager
        self.visa_manager = visa_manager
        instrument_list = self.visa_manager.get_list_of_detailed_instruments()
        for instrument in instrument_list:
            self.visaStringOsc.addItem(instrument.idnString)

    def continue_action(self):
        error = False
        # Gets visa string from selected instrument.
        self.visa_string = self.visa_manager.get_visa_from_idn(self.visaStringOsc.currentText())

        # Gets selected acquire mode
        acquire_type_text = str(self.acquireBox.currentText())
        for acquire_types in AcquireTypes:
            if acquire_type_text == acquire_types.value[0]:
                self.acquire_type = acquire_types.value[1]

        if self.acquire_type == ChannelTypes.none.value[0]:
            error = True
            self.errorLabel.setText("Select a valid acquire type.")

        # Gets selected trigger source
        trigger_source_text = str(self.triggerSourceBox.currentText())
        for trigger in TriggerSources:
            if trigger_source_text == trigger.value[0]:
                self.trigger_source = trigger.value[1]

        if self.trigger_source == TriggerSources.none.value[0]:
            error = True
            self.errorLabel.setText("Select a valid trigger source.")

        # Gets selected channels
        channel_in_text = str(self.channelInBox.currentText())
        for channel in ChannelTypes:
            if channel_in_text == channel.value:
                self.channel_in = channel.value
        channel_out_text = str(self.channelOutBox.currentText())
        for channel in ChannelTypes:
            if channel_out_text == channel.value:
                self.channel_out = channel.value

        if self.channel_in == ChannelTypes.none.value or self.channel_out == ChannelTypes.none.value:
            error = True
            self.errorLabel.setText("Select a valid channel.")
        elif self.channel_in == self.channel_out:
            error = True
            self.errorLabel.setText("In & Out channels can't be the same.")

        # Get selected probes
        if self.probeInCheck.isChecked():
            self.probe_in = ProbeTypes.x10.value[1]

        if self.probeOutCheck.isChecked():
            self.probe_out = ProbeTypes.x10.value[1]

        if self.noiseRejectBox.isChecked():
            self.noise_reject = True
        else:
            self.noise_reject = False

        if self.highFreqBox.isChecked():
            self.high_freq_reject = True
        else:
            self.high_freq_reject = False

        self.trigger_level = round(self.triggerLevelBox.value(), 1)

        if not error:
            self.errorLabel.setText("")
            self.close()
            oscilloscope_configuration = {
                "visaString": self.visa_string,
                "channelIn": self.channel_in,
                "channelOut": self.channel_out,
                "probeIn": self.probe_in,
                "probeOut": self.probe_out,
                "noiseReject": self.noise_reject,
                "acquireType": self.acquire_type,
                "triggerSource": self.trigger_source,
                "triggerLevel": self.trigger_level,
                "highFreqReject": self.high_freq_reject
            }
            self.bode_manager.bode_configuration.osc_config_params = oscilloscope_configuration
            self.bode_manager.show_next_window()


class ProbeTypes(Enum):
    """ ProbeTypes """
    x1 = ["X1",1]
    x10 = ["X10",10]


class ChannelTypes(Enum):
    """ ProbeTypes """
    channel1 = "CHANNEL1"
    channel2 = "CHANNEL2"
    channel3 = "CHANNEL3"
    channel4 = "CHANNEL4"
    none = "No Channel"


class AcquireTypes(Enum):
    """ AcquireTypes"""
    normal = ["NORMAL", "NORMal"]
    peak = ["PEAK", "PEAK"]
    average = ["AVERAGE", "AVERage"]
    high_res = ["HIGH RESOLUTION", "HRESolution"]
    none = ["No Channel", "No Channel"]


class TriggerSources(Enum):
    """TriggerSources"""
    channel1 = ["CHANNEL1", "CHANnel1"]
    channel2 = ["CHANNEL2", "CHANnel2"]
    channel3 = ["CHANNEL3", "CHANnel3"]
    channel4 = ["CHANNEL4", "CHANnel4"]
    external = ["EXTERNAL", "EXTernal"]
    line = ["LINE", "LINE"]
    none = ["No Source", "No Source"]
