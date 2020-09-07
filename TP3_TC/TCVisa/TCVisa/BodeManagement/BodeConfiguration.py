import time

import numpy

from BodeManagement.UIManagement.configureMeasurement import UIConfigMeas, SweepTypes
from BodeManagement.UIManagement.configureOsc import UIConfigOsc, ChannelTypes, AcquireTypes
from BodeManagement.UIManagement.configureWaveGen import UIConfigWaveGen, WaveFormTypes
from BodeManagement.VisaManagement import VisaManager
from graphpreview import UIGraphPreview


class BodeConfiguration:
    def __init__(self):
        self.osc_config_params = None
        self.wave_gen_config_params = None
        self.measure_config_params = None


class BodeGraph:
    def __init__(self, freqs, mods, phases):
        self.frequencies = freqs
        self.module = mods
        self.phase = phases


# BodeManager: Manages the sequence of configuration views and commands sent to the instruments.
class BodeManager:
    def __init__(self):
        # Bode points arrays
        self.bode = None
        self.frequencies = []
        self.phase_measurements = []
        self.ratio_measurements = []
        self.visa_manager = VisaManager()
        # Windows
        self.config_osc_window = UIConfigOsc(self, self.visa_manager)
        self.config_wave_window = UIConfigWaveGen(self, self.visa_manager)
        self.config_meas_window = UIConfigMeas(self)
        self.window_sequence = [self.config_osc_window, self.config_wave_window, self.config_meas_window]
        self.iterator = 0
        self.last_meas = 0
        self.bode_configuration = BodeConfiguration()

        self.window_sequence[self.iterator].show()

    def start_over(self, error_msg=""):
        """
        Starts configuration window sequence again.
        :param error_msg: Optional error message to be shown in the first window.
        """
        self.window_sequence[self.iterator].close()
        self.iterator = 0
        self.window_sequence[self.iterator].show()
        self.window_sequence[self.iterator].errorLabel.setText(error_msg)

    def show_next_window(self):
        """
        Shows the next window (if exists) in the configuration window sequence and closes the current one.
        If the current window is the last one, it starts the Bode measurement and displays the results in a graph window.
        """
        if self.iterator < (len(self.window_sequence) - 1):
            self.window_sequence[self.iterator].close()
            self.iterator += 1
            self.window_sequence[self.iterator].show()
            if self.window_sequence[self.iterator] == self.config_meas_window:
                self.config_meas_window.on_window_shown()

        else:
            conf_osc = self.bode_configuration.osc_config_params
            conf_wave = self.bode_configuration.wave_gen_config_params
            conf_meas = self.bode_configuration.measure_config_params
            self.bode = self.measure_bode(conf_osc, conf_wave, conf_meas)
            if self.bode is not None:
                self.window_sequence[self.iterator].close()
                self.graph_prev_window = UIGraphPreview(self)
                self.graph_prev_window.show()
                self.graph_prev_window.plot_window()

    def show_prev_window(self):
        """
        Shows the previous window (if exists) in the configuration window sequence and closes the current one.
        """
        if self.iterator > 0:
            self.window_sequence[self.iterator].close()
            self.iterator -= 1
            if self.window_sequence[self.iterator] == self.config_meas_window:
                self.config_meas_window.on_window_shown()
            self.window_sequence[self.iterator].show()

    def measure_bode(self, conf_osc, conf_wave, conf_meas):
        """
        Controls the instruments with the params received in order to draw a Bode graph.
        :param conf_osc: Oscilloscope configuration parameters. Dictionary.
        :param conf_wave: Wave Generator configuration parameters. Dictionary.
        :param conf_meas: Measurement configuration parameters. Dictionary.
        :return: Bode Graph instance. None if error occurred.
        """
        channel_1 = conf_osc["channelIn"]
        channel_2 = conf_osc["channelOut"]
        probe1 = conf_osc["probeIn"]
        probe2 = conf_osc["probeOut"]
        start_freq = conf_wave["startFreq"]
        stop_freq = conf_wave["stopFreq"]
        amplitude = conf_wave["amplitude"]
        sweep_type = conf_meas["sweepType"]
        measure_tick = conf_meas["measureTick"]
        establishment_time = conf_meas["establishmentTime"]
        wave_form = conf_wave["waveForm"]
        visa_osc = conf_osc["visaString"]
        visa_wave_gen = conf_wave["visaString"]
        acquire_type = conf_osc["acquireType"]
        noise_reject = conf_osc["noiseReject"]
        trigger_source = conf_osc["triggerSource"]
        trigger_level = conf_osc["triggerLevel"]
        high_freq_reject = conf_osc["highFreqReject"]
        i = 1
        # Parameter configuration
        for channel in ChannelTypes:
            if channel_1 == channel.value:
                first_channel_n_ = i
            if channel_2 == channel.value:
                second_channel_n_ = i
            i += 1
        try:
            rm = self.visa_manager.get_resource_manager()

            # Connection
            SCPI_33220 = rm.open_resource(visa_wave_gen)

            SCPI_InfiniiVision6000 = rm.open_resource(visa_osc)

            # Oscilloscope Configuration
            SCPI_InfiniiVision6000.write('*RST')
            # Channel probes, offsets and display activation
            SCPI_InfiniiVision6000.write(':CHANnel%d:PROBe %s' % (first_channel_n_, probe1))
            SCPI_InfiniiVision6000.write(':CHANnel%d:PROBe %s' % (second_channel_n_, probe2))
            SCPI_InfiniiVision6000.write(':CHANnel%d:OFFSet %G' % (first_channel_n_, 0.0))
            SCPI_InfiniiVision6000.write(':CHANnel%d:OFFSet %G' % (second_channel_n_, 0.0))
            SCPI_InfiniiVision6000.write(':CHANnel%d:DISPlay %d' % (first_channel_n_, 1))
            SCPI_InfiniiVision6000.write(':CHANnel%d:DISPlay %d' % (second_channel_n_, 1))
            SCPI_InfiniiVision6000.write(':TRIGger:NREJect %d' % (noise_reject))
            SCPI_InfiniiVision6000.write(':TRIGger:HFReject %d' % (high_freq_reject))

            # Time and trigger
            SCPI_InfiniiVision6000.write(':TIMebase:MODE %s' % ('MAIN'))
            SCPI_InfiniiVision6000.write(':TRIGger:SWEep %s' % ('AUTO'))
            SCPI_InfiniiVision6000.write(':TRIGger:EDGE:SOURce %s' % (trigger_source))
            SCPI_InfiniiVision6000.write(':ACQuire:TYPE %s' % (acquire_type))
            if acquire_type == AcquireTypes.average.value[1]:
                SCPI_InfiniiVision6000.write(':ACQuire:COUNt %d' % (4))
            SCPI_InfiniiVision6000.write(':TIMebase:MAIN:DELay %G' % (0.0))
            SCPI_InfiniiVision6000.write(':TRIGger:EDGE:LEVel %G V' % (trigger_level))


            # Measurement activation
            SCPI_InfiniiVision6000.write(':MEASure:PHASe %s,%s' % (channel_2, channel_1))
            SCPI_InfiniiVision6000.write(':MEASure:VRATio %s,%s' % (channel_2, channel_1))
            SCPI_InfiniiVision6000.write(':MEASure:VPP %s' % (channel_1))
            SCPI_InfiniiVision6000.write(':MEASure:VPP %s' % (channel_2))

            # Generator Configuration
            SCPI_33220.write('*RST')
            SCPI_33220.write(':OUTPut:LOAD %s' % ('INFinity'))
            SCPI_33220.write(':OUTPut:STATe %d' % (1))

            current_first_range = amplitude*0.8
            self.last_meas = amplitude
            SCPI_InfiniiVision6000.write(':CHANnel%d:RANGe %G' % (first_channel_n_, current_first_range))

            SCPI_InfiniiVision6000.write(':CHANnel%d:RANGe %G' % (second_channel_n_, self.last_meas*0.8))

            if sweep_type == SweepTypes.linearSweep.value:
                for freq in numpy.arange(start_freq, stop_freq, measure_tick):
                    # Signal application
                    self.__measure__(SCPI_33220, SCPI_InfiniiVision6000, amplitude*0.8, channel_1, channel_2,
                                     current_first_range,
                                     establishment_time, first_channel_n_, freq,
                                     second_channel_n_,
                                     wave_form, self.last_meas)
            elif sweep_type == SweepTypes.logarithmicSweep.value:
                base = 1
                inibase = base
                mult = 10
                iniexp = 0

                # buscar base inicial mas cercana a startfreq
                while base < start_freq:
                    base *= mult
                    iniexp += 1
                    inibase = base

                endexp = 0
                # buscar base final mas cercana a stopfreq
                base = 1
                endbase = base
                while base < stop_freq:
                    endbase = base
                    base *= mult
                    endexp += 1
                endexp -= 1

                # medir entre atartfrq y base inicial mas cercana
                if inibase > start_freq:
                    for freq in range(start_freq, inibase, int((inibase - start_freq) / int(measure_tick))):
                        self.__measure__(SCPI_33220, SCPI_InfiniiVision6000, amplitude*0.8, channel_1, channel_2,
                                         current_first_range,
                                         establishment_time, first_channel_n_, freq,
                                         second_channel_n_,
                                         wave_form, self.last_meas)

                # medir entre base inicial y base final
                while iniexp < endexp:
                    for freq in numpy.logspace(iniexp, iniexp + 1, int(measure_tick), base=10, dtype='int'):
                        self.__measure__(SCPI_33220, SCPI_InfiniiVision6000, amplitude*0.8, channel_1, channel_2,
                                         current_first_range,
                                         establishment_time, first_channel_n_, freq,
                                         second_channel_n_,
                                         wave_form, self.last_meas)
                    iniexp += 1

                # medir entre base final mas cercana y stop freq

                if endbase < stop_freq:
                    for freq in range(endbase, stop_freq, int((stop_freq - endbase) / int(measure_tick))):
                        self.__measure__(SCPI_33220, SCPI_InfiniiVision6000, amplitude*0.8, channel_1, channel_2,
                                         current_first_range,
                                         establishment_time, first_channel_n_, freq,
                                         second_channel_n_,
                                         wave_form, self.last_meas)

            SCPI_InfiniiVision6000.close()
            SCPI_33220.close()
            rm.close()
            return BodeGraph(self.frequencies, self.ratio_measurements, self.phase_measurements)
        except:
            self.start_over("An error has occurred. Reconfigure params")
            return None

    def __measure__(self, SCPI_33220, SCPI_InfiniiVision6000, amplitude, channel_1, channel_2, current_first_range,
                    establishment_time, first_channel_n_, freq, second_channel_n_, wave_form,
                    last_measurement):
        """
        Internal function used by measure_bode.
        Applies wave form, configures oscilloscope scales and measures ratio and phase.
        """
        if wave_form == WaveFormTypes.sineWave.value:
            SCPI_33220.write(':APPLy:SINusoid %G,%G,%G' % (freq, amplitude*0.8, 0.0))
        # Time scale configuration deppending on frequency
        SCPI_InfiniiVision6000.write(':TIMebase:MAIN:SCALe %G' % (1 / (5 * freq)))
        # vertical scale
        SCPI_InfiniiVision6000.write(':CHANnel%d:RANGe %G' % (second_channel_n_, last_measurement*1.4))
        time.sleep(establishment_time / 1000)
        temp_values = SCPI_InfiniiVision6000.query_ascii_values(':MEASure:VPP? %s' % (channel_1))
        vpp_in = temp_values[0]
        temp_values2 = SCPI_InfiniiVision6000.query_ascii_values(':MEASure:VPP? %s' % (channel_2))
        vpp_out = temp_values2[0]

        while vpp_in >= 0.85 * current_first_range:
            current_first_range = 1.2 * current_first_range
            SCPI_InfiniiVision6000.write(':CHANnel%d:RANGe %G' % (first_channel_n_, current_first_range))
            time.sleep(0.1)
            temp_values = SCPI_InfiniiVision6000.query_ascii_values(':MEASure:VPP? %s' % (channel_1))
            vpp_in = temp_values[0]
        while vpp_out >= 0.85 * self.last_meas :
            self.last_meas = 1.4 * self.last_meas
            SCPI_InfiniiVision6000.write(':CHANnel%d:RANGe %G' % (second_channel_n_, self.last_meas))
            time.sleep(0.1)
            temp_values2 = SCPI_InfiniiVision6000.query_ascii_values(':MEASure:VPP? %s' % (channel_2))
            vpp_out = temp_values2[0]
        while vpp_out < self.last_meas*0.2:
            self.last_meas = 0.2 * self.last_meas
            SCPI_InfiniiVision6000.write(':CHANnel%d:RANGe %G' % (second_channel_n_, self.last_meas))
            time.sleep(0.1)
            temp_values2 = SCPI_InfiniiVision6000.query_ascii_values(':MEASure:VPP? %s' % (channel_2))
            vpp_out = temp_values2[0]

        self.last_meas = vpp_out
        # Establishment time before measuring
        time.sleep(0.1)
        # Measurement
        temp_values = SCPI_InfiniiVision6000.query_ascii_values(
            ':MEASure:VRATio? %s,%s' % (channel_2, channel_1))
        temp_values2 = SCPI_InfiniiVision6000.query_ascii_values(
            ':MEASure:PHASe? %s,%s' % (channel_2, channel_1))
        if temp_values[0] < 1000000 and temp_values2[0] < 1000000:
            self.ratio_measurements.append(temp_values[0])
            self.phase_measurements.append(temp_values2[0])
            self.frequencies.append(freq)
