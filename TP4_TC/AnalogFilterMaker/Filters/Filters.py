# python native modules
from enum import Enum

# third-party modules
from numpy import poly, conjugate
from numpy import sqrt
from numpy import conj
from numpy import angle
from numpy import log10
from numpy import amax
from numpy import unwrap
from numpy import diff
from numpy import pi
from scipy import signal
from numpy import imag
from numpy import real

# AFM project modules
from BackEnd.Output.plots import GraphValues


class FilterTypes(Enum):
    LowPass = "Low Pass"
    HighPass = "High Pass"
    BandPass = "Band Pass"
    BandReject = "Band Stop"
    GroupDelay = "Group Delay"


class TemplateInfo(Enum):
    Ap = "Ap [dB]"
    Aa = "Aa [dB]"
    fa = "fa [Hz]"
    fp = "fp [Hz]"
    fa_ = "fa+ [Hz]"
    fa__ = "fa- [Hz]"
    fp_ = "fp+ [Hz]"
    fp__ = "fp- [Hz]"
    gd = "Group delay [us]"
    ft = "ft [Hz]"
    tol = "Tolerance [%]"
    k = "Gain [dB]"


class GraphTypes(Enum):
    NormalizedAt = "Normalized Attenuation"
    NormalizedGd = "Normalized Group Delay"
    Attenuation = "Attenuation"
    Module = "Module"
    Phase = "Phase"
    PolesZeros = "Zeros and Poles"
    Step = "Step response"
    Impulse = "Impulse response"
    GroupDelay = "Group delay"
    StagesQ = "Q"


class Filter(object):

    def __init__(self, filter_type: FilterTypes):
        self.filter = filter_type
        self.requirements = {}
        self.normalized = {"Order": None,
                           "Zeros": [],
                           "Poles": [],
                           "Gain": None}
        self.denormalized = {"Order": None,
                             "Zeros": [],
                             "Poles": [],
                             "Gain": None,
                             "StagesQ": None,
                             "MaxQ": None}
        self.limits = {
            TemplateInfo.Aa.value: (0, 10e9), TemplateInfo.Ap.value: (0, 10e9), TemplateInfo.fa.value: (0, 10e9),
            TemplateInfo.fp.value: (0, 10e9), TemplateInfo.fp_.value: (0, 10e9), TemplateInfo.fp__.value: (0, 10e9),
            TemplateInfo.fa_.value: (0, 10e9), TemplateInfo.fa__.value: (0, 10e9), TemplateInfo.ft.value: (0, 10e9),
            TemplateInfo.gd.value: (0, 10e9), TemplateInfo.tol.value: (0, 100), TemplateInfo.k.value: (-10e9, 10e9)}
        self.selectivity = 0
        self.normalized_freqs = []
        self.defaults = []

    def get_type(self) -> FilterTypes:
        return self.filter

    def get_limit(self, info: TemplateInfo):
        return self.limits[info]

    def get_default(self, info: TemplateInfo):
        return self.defaults[info]

    def get_requirements(self):
        return [key for key in self.requirements]

    def get_order(self):
        return self.normalized["Order"], self.denormalized["Order"]

    def load_requirements(self, specs):
        for each in specs:
            if each in self.requirements.keys():
                self.requirements[each] = specs[each]
            else:
                print("Key not found in requirements")
                return False
        if not self.validate_requirements():
            return False

    def validate_requirements(self) -> (bool, str):
        pass

    def get_req_value(self, key: TemplateInfo):
        return self.requirements[key]

    def get_max_q(self):
        return self.denormalized["MaxQ"]

    def load_z_p_k(self, z, p, k):
        self.denormalized["Zeros"] = self._agrup_roots(z)
        self.denormalized["Gain"] = k*pow(10, self.requirements[TemplateInfo.k.value]/20)
        self.denormalized["Order"] = len(p)
        self.denormalized["StagesQ"] = []
        max_q = 0
        p = self._agrup_roots(p)     # ordena Re(p) creciente, se asegura que los comp conj tengan el mismo valor
        self.denormalized["Poles"] = p.copy()
        while len(p):                 # agrupo en polos complejos conjugados
            # len_in = len(self.denormalized["StagesQ"])
            for i in range(1, len(p)):
                if p[0] == p[i].conjugate():
                    # pairs.append(p[0])
                    wo = sqrt(abs(p[0] * p[i]))
                    q = -wo / (p[0].real + p[i].real)
                    self.denormalized["StagesQ"].append(q)
                    p.remove(p[i])
                    break
            p.remove(p[0])
            # if len_in == len(self.denormalized["StagesQ"]):  # si no le encontre un conjugado
            #    pairs.append([p[0]])  # no lo tiene :(
            #    self.denormalized["StagesQ"].append(-1)
        if len(self.denormalized["StagesQ"]):
            self.denormalized["MaxQ"] = amax(self.denormalized["StagesQ"])

    def load_normalized_z_p_k(self, z, p, k):
        self.normalized["Zeros"] = z
        self.normalized["Poles"] = p
        self.normalized["Gain"] = k
        self.normalized["Order"] = len(p)

    def get_z_p_k_q(self):
        """ Returns poles ordered: conjugates are next to each other """
        return self.denormalized["Zeros"], self.denormalized["Poles"], self.denormalized["Gain"], self.denormalized["StagesQ"]

    def get_req_limit(self, key: TemplateInfo):
        return self.limits[key]

    def get_all_graphs(self):
        graphs = {}
        if self.denormalized["MaxQ"] is not None:
            extra_info = f'n={self.denormalized["Order"]} Qmax={self.denormalized["MaxQ"]:.2}'
        else:
            extra_info = f'n={self.denormalized["Order"]} Qmax= - '
        k = self.denormalized["Gain"]
        trans_func = signal.ZerosPolesGain(self.denormalized["Zeros"], self.denormalized["Poles"], k)
        w, h = trans_func.freqresp(n=3000)
        f = w / (2 * pi)
        mag = 20 * log10(abs(h))
        phase = angle(h, deg=True)
        graphs[GraphTypes.Module.value] = [[GraphValues(f, mag, False, False, True, extra_info)],
                                           ["Frequency [Hz]", "Amplitude [dB]"]]
        graphs[GraphTypes.Phase.value] = [[GraphValues(f, phase, False, False, True, extra_info)], ["Frequency[Hz]", "Phase[deg]"]]

        trans_func = signal.ZerosPolesGain(self.denormalized["Zeros"], self.denormalized["Poles"],
                                           self.denormalized["Gain"]/pow(10, self.requirements[TemplateInfo.k.value]/20))
        norm_trans_func = signal.ZerosPolesGain(self.normalized["Zeros"], self.normalized["Poles"], self.normalized["Gain"])
        w, h = trans_func.freqresp(n=3000)
        f = w/(2*pi)
        mag = 20 * log10(abs(h))
        phase = angle(h)
        w_n, h_n = norm_trans_func.freqresp(n=3000)
        f_n = w_n/(2*pi)
        mag_n = 20 * log10(abs(h_n))
        phase_n = angle(h_n)
        graphs[GraphTypes.Attenuation.value] = [[GraphValues(f, -mag, False, False, True, extra_info)], ["Frequency [Hz]", "Attenuation[dB]"]]   # se pasa una lista de graphvalues
        if self.filter is FilterTypes.GroupDelay.value:
            # norm_gd = -2 * pi * diff(unwrap(phase_n)) / diff(w_n)
            norm_gd = -diff(unwrap(phase)) / diff(w)
            f_n = f*norm_gd[0]
            graphs[GraphTypes.NormalizedGd.value] = [[GraphValues(f_n[:-1], norm_gd/norm_gd[0], False, False, True, extra_info)],
                                             ["Frequency[Hz]", "Group delay [s]"]]  # -d(Phase)/df = -dP/dw * dw/df = -dP/dw * 2pi
        else:
            graphs[GraphTypes.NormalizedAt.value] = [[GraphValues(f_n, -mag_n, False, False, True, extra_info)], ["Frequency[Hz]", "Attenuation[dB]"]]
        graphs[GraphTypes.GroupDelay.value] = [[GraphValues(f[:-1], -diff(unwrap(phase))/diff(w)*1e6, False, False, True, extra_info)], ["Frequency[Hz]", "Group delay[us]"]]  # -d(Phase)/df = -dP/dw * dw/df = -dP/dw * 2pi
        t, imp = signal.impulse(trans_func)
        graphs[GraphTypes.Impulse.value] = [[GraphValues(t, imp, False, False, False, extra_info)], ["t[s]", "V[V]"]]
        t, step = signal.step(trans_func)
        graphs[GraphTypes.Step.value] = [[GraphValues(t, step, False, False, False, extra_info)], ["t[s]", "V[V]"]]
        graphs[GraphTypes.StagesQ.value] = [[], []]
        if len(self.denormalized["StagesQ"]):   # los filtros de primer orden no tienen Q
            i = 0
            while i < len(self.denormalized["StagesQ"]):
                graphs[GraphTypes.StagesQ.value][0].append(GraphValues([0, self.denormalized["StagesQ"][i]], [i+1, i+1], False, False, False, extra_info))
                i += 1
            graphs[GraphTypes.StagesQ.value][1] = ["Q", "Q N°"]

        repeated_z = []
        z = []
        repeated_p = []
        p = []
        graphs[GraphTypes.PolesZeros.value] = [[], []]
        i=0
        while i < len(self.denormalized["Zeros"]):
            count = self.denormalized["Zeros"].count(self.denormalized["Zeros"][i])
            count_conj = self.denormalized["Zeros"].count(conjugate(self.denormalized["Zeros"][i]))
            z.append(self.denormalized["Zeros"][i])
            z.append(conjugate(self.denormalized["Zeros"][i]))
            repeated_z.append(count)
            repeated_z.append(count_conj)
            i += count + count_conj
        i = 0
        while i < len(self.denormalized["Poles"]):
            count = self.denormalized["Poles"].count(conjugate(self.denormalized["Poles"][i]))
            count_conj = self.denormalized["Poles"].count(conjugate(self.denormalized["Poles"][i]))
            for j in range(count):
                p.append(self.denormalized["Poles"][i])
            for j in range(count_conj):
                p.append(conjugate(self.denormalized["Poles"][i]))
            repeated_p.append(count)
            repeated_p.append(count_conj)
            i += count + count_conj
        if len(self.denormalized["Zeros"]):
            graphs[GraphTypes.PolesZeros.value][0].append(GraphValues(real(z), imag(z), True, False, False, extra_info, repeated_z))
        graphs[GraphTypes.PolesZeros.value][0].append(GraphValues(real(p), imag(p), True, True, False, extra_info, repeated_p))
        graphs[GraphTypes.PolesZeros.value][1] = ["Re(s)[rad/sec]", "Im(s)[rad/sec]"]
        return graphs

    @staticmethod
    def _agrup_roots(p):
        if len(p) is 0:
            return p
        new_p = []
        p = sorted(p, key=lambda x: x.real)  # ordeno por parte real creciente
        while len(p):
            len_in = len(new_p)
            for i in range(1, len(p)):
                if (abs(p[0].real - p[i].real) < 1e-10) and (abs(p[0].imag + p[i].imag) < 1e-10):
                    new_p.append(p[0])
                    new_p.append(complex(p[0].real, -p[0].imag))    # fuerzo que sean valores iguales
                    p.remove(p[i])
                    break
            if len_in == len(new_p):  # si no le encontre un conjugado
                new_p.append(p[0])  # no lo tiene :(
            p.remove(p[0])
        return new_p

    def get_templates(self):
        pass

    def get_selectivity(self):
        return self.selectivity
