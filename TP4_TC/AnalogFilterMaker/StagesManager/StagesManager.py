# python native modules
from enum import Enum

from numpy import conjugate, amax, amin, pi, real, imag, floor
from numpy import argmin
from numpy import full
from numpy import log10
from enum  import Enum
from numpy import sum

# AFM project modules
from scipy import signal

from BackEnd.Output.plots import GraphValues
from Filters.Filters import Filter
from StagesManager.Pole import Pole
from StagesManager.Stage import Stage
from StagesManager.Zero import Zero


class ShowType(Enum):
    Selected = "Selected",
    Superposed = "Superposed",
    Total = "Total"


class StagesManager(object):

    def __init__(self):
        self.p_pairs = [] # va a tener arreglo de Poles
        self.z_pairs = [] # va a tener arreglos de Zeros
        self.unused_p = []
        self.unused_z = []
        self.sos = []
        self.k_tot = 0
        self.selected = []

    def load_filter(self, fil: Filter):
        self.selected = []
        self.p_pairs = []  # va a tener arreglo de Poles
        self.z_pairs = []  # va a tener arreglos de Zeros
        self.unused_p = []
        self.unused_z = []
        self.sos = []
        self.k_tot = 0
        """ Guarda todos los polos y ceros agrupados en etapas de 1/2do orden """
        z, p, self.k_tot, q = fil.get_z_p_k_q()

        saved = False
        while len(p):  # guardo en self.p_pairs los pares de polos complejos conjugados como [wo,Q]
            if len(p) > 1:
                if p[0] == conjugate(p[1]):
                    self.p_pairs.append(Pole(p[0]))
                    p.remove(p[1])
                    saved = True
            if not saved:
                self.p_pairs.append(Pole(p[0]))  # si no tiene conjugado deberia ser real
            p.remove(p[0])
            saved = False
        while len(z):  # guardo en self.z_pairs los pares de ceros complejos conjugados como [wo,n]
            if len(z) > 1:
                if z[0] == conjugate(z[1]):
                    self.z_pairs.append(Zero(abs(z[0]), 2))
                    z.remove(z[1])
                    saved = True
            if not saved:
                self.z_pairs.append(Zero(abs(z[0]), 1))  # si no tiene conjugado es de primer orden en el origen
            z.remove(z[0])
            saved = False
        self.p_pairs.sort(key=lambda x: x.q, reverse=True)  # ordeno polos por Q creciente
        self.z_pairs.sort(key=lambda x: x.n, reverse=True)  # ordeno ceros por orden creciente

    def auto_max_rd(self, vi_min, vi_max):
        # agrupo todas
        self.sos = []
        z_i = None  # habra como mucho un cero de primer orden
        p_i = None  # habra como mucho un polo de primer orden
        """ To agrupate nearest poles and zeros """
        if len(self.z_pairs):   # si tiene ceros
                adj_matrix = [] # aqui se guardaran todas las distancias entre frecuencias de corte de polos y ceros
                for i in range(len(self.z_pairs)):      # para cada cero
                    if self.z_pairs[i].n == 2:  # si el cero es de segundo orden
                        adj_matrix.append([])
                        for j in range(len(self.p_pairs)):
                            if self.p_pairs[j].q > 0:  # si el polo es de segundo orden
                                dist = abs(self.z_pairs[i].im - self.p_pairs[j].fo)
                                adj_matrix[i].append(dist)          # guardo la distancia entre cada polo y cero de orden 2
                            else:
                                if p_i is None:
                                    p_i = j
                    else:
                        if z_i is None:
                            z_i = i
                used_p = full(len(adj_matrix), False)
                i, j = (0, 0)
                while adj_matrix[i][j] < 1e9:
                    i, j = argmin(adj_matrix)
                    self.z_pairs[i].used = True
                    self.p_pairs[j] = True
                    self.sos.append(Stage(self.z_pairs[i], self.p_pairs[j], 1)) # ganancia 1 por defecto
                    adj_matrix[i] = full(len(adj_matrix), 1e9)  # ya no me interesa esta distancia, la hago grande para que no salga elegida
                    adj_matrix[:, j] = full(len(adj_matrix), 1e9)
                    used_p[j] = True    # marca que este polo ya se utilizo
                for i in range(adj_matrix.shape(1)):
                    if not used_p[i]:
                        self.p_pairs[i].used = True
                        if z_i is None:
                            self.sos.append(Stage(None, self.p_pairs[i], 1))
                        else:   # si hay algun cero de primer oden, se lo agrego a la primera etapa sin ceros que aparezca
                            self.z_pairs[z_i].used = True
                            self.sos.append(Stage(self.z_pairs[z_i], self.p_pairs[i], 1))
                            z_i = None
                if p_i is not None:
                    zero = complex(0)
                    self.p_pairs[p_i].used = True
                    if z_i is not None:
                        self.z_pairs[z_i].used = True
                        zero = self.z_pairs[z_i]
                        z_i = None
                    self.sos.append(Stage(zero, self.p_pairs[p_i], 1))
                    p_i = None
        else:
            for i in range(len(self.p_pairs)):
                self.p_pairs[i].used = True
                self.sos.append(Stage(None, self.p_pairs[i], 1))
        self.sos.sort(key=lambda x: x.pole.q)  # ordena por Q decreciente
        ganancias = []
        # for i in range(len(self.sos)):
        #     self.sos[i].k = 1  # Le pongo a todas ganancias 1
        #     polos = 0
        #     if self.sos[i].pole.q > 0:  # Polo de segundo orden
        #         polos *= abs(self.sos[i].pole.p)**2
        #     else:
        #         polos *= abs(self.sos[i].pole.p)
        #     zero = 0
        #     if self.sos[i].z is not None:
        #         zero = abs(self.sos[i].z.im)**self.sos[i].z
        #     else:
        #         zero = 1
        #     self.k_tot /= polos/zero
        #
        # print(self.k_tot)
        #
        # self.sos[:-1].k += self.k_tot

        return self.sos

    def get_stages(self):
        """" Returns Stages list """
        ret = []
        for i in self.sos:
            if i in self.selected:
                ret.append(True)
            else:
                ret.append(False)
        return self.sos, ret

    def add_stage(self, p_str: str, z_str: str) -> (bool,str):
        """ Devuelve True es valida la etapa solicitada, False si no """
        ret = ""
        ok = False
        z_ind = None
        p_ind = None
        for i_z in range(len(self.z_pairs)):    # busco el indice del cero seleccionado
            if z_str == self.z_pairs[i_z].get_msg():
                z_ind = i_z
                break
        for i_p in range(len(self.p_pairs)):    # busco el indice del polo seleccionado
            if p_str == self.p_pairs[i_p].get_msg():
                p_ind = i_p
                break
            # self.sos.append(Stage(zero, pole, 1))
        n_z = 0
        n_p = 1 if self.p_pairs[p_ind].q < 0 else 2
        if z_ind is not None:
            n_z = self.z_pairs[z_ind].n
        if n_p >= n_z:
            pole_n_left = 0
            z_n_left = 0
            for p in self.p_pairs:
                if not p.used:
                    pole_n_left += 2 if p.q > 0 else 1
            for z in self.z_pairs:
                if not z.used:
                    z_n_left += z.n
            if pole_n_left-n_p >= z_n_left-n_z:
                ok = True
                self.p_pairs[p_ind].used = True
                if z_ind is not None:
                    self.z_pairs[z_ind].used = True
                    self.sos.append(Stage(self.z_pairs[z_ind], self.p_pairs[p_ind], 1))
                else:
                    self.sos.append(Stage(None, self.p_pairs[p_ind], 1))
            else:
                ret = "There must be greater o equal amount of poles than zeros remaing after selection"
        else:
            ret = "Zero's order can't be greater than pole's order"
        return ok, ret

    def shift_stages(self, indexes: list, left):
        """ Shifts the stages indicated at the indexes list. Shifts left if left == True,shifts rigth otherwise"""
        ret = False
        if len(self.sos) > 1:
            ret = True
            if left:
                step = -1
                i_lim = 0
                i = len(self.sos)
            else:
                step = 1
                i_lim = len(self.sos)
                i = 0

            rep = step
            while i != i_lim:
                if i in indexes:
                    while i+rep in indexes:
                        rep += step
                    if i+rep != i_lim:
                        self.sos[i], self.sos[i+rep] = (self.sos[i+rep], self.sos[i])
                i += step
                rep = step
        return ret

    def delete_stages(self, indexes: list):
        """" Deletes stages indicated by indexes list """
        if amax(indexes) < len(self.sos):
            for i in reversed(indexes):
                s = self.sos.pop(i)
                for j in range(len(self.p_pairs)):
                    if self.p_pairs[j] == s.pole:
                        self.p_pairs[j].used = False
                for j in range(len(self.z_pairs)):
                    if self.z_pairs[j] == s.z:
                        self.z_pairs[j].used = False
            self.selected = [0]
        else:
            print("Indexes list out of range!")

    def set_gain(self, i, k) -> (bool, str):
        if i < len(self.sos):
            partial_gain = 0
            for j in range(len(self.sos)):
                partial_gain += self.sos[j].k if j != i else 10**(k/20)
            if partial_gain <= self.k_tot:
                self.sos[i].k = 10**(k/20)
                return True, ""
            else:
                return False, f"Total gain can't exceed {self.k_tot:.2f} dB"
        else:
            return False, f"Stage {i + 1} doesn't exist."

    def get_z_p_plot(self):
        """" Returns poles and zeros diagram with number of repeticiones of each pole and zero """
        repeated_z = []
        z = []
        repeated_p = []
        p = []
        i = 0
        while i < len(self.z_pairs):
            count = self.z_pairs.count(self.z_pairs[i])
            add = 0
            for j in range(count):
                add += self.z_pairs[i + j].n
            add_z = complex(0, self.z_pairs[i].im)
            if self.z_pairs[i].n == 2:
                z += [add_z, conjugate(add_z)]
                repeated_z.append(int(floor(add/2)))
                repeated_z.append(int(floor(add/2)))
            else:
                repeated_z.append(add)
                z += [add_z]
            i += count
        i = 0
        while i < len(self.p_pairs):
            count = self.p_pairs.count(self.p_pairs[i])
            repeated_p.append(count)
            add_p = self.p_pairs[i].p
            p += [add_p, conjugate(add_p)] if self.p_pairs[i].q > 0 else [add_p]
            i += count
        return [[GraphValues(real(z), imag(z), True, False, False, "Zeros", repeated_z), GraphValues(real(p),
                        imag(p), True, True, False, "Poles", repeated_p)], ["Re(s)[rad/sec]", "Im(s)[rad/sec]"]]

    def get_z_p_dict(self):
        """ Returns a dictionary with all zeros and poles:
         { "Poles": {"1st order": [Poles], "2nd order": [Poles]}
           "Zeros": {"1st order": [Zeros], "2nd order": [Zeros]} } """
        #ret = {"Poles": {"1st order": [], "2nd order": []}, "Zeros": {"1st order": [], "2nd order": []}}
        ret = {"Poles": {}, "Zeros": {}}
        first = False
        sec = False
        change = False
        for p in self.p_pairs:
            if p.q < 0:
                key2 = "1st order"
                if not first:
                    change = True
                    first = True
            else:
                key2 = "2nd order"
                if not sec:
                    change = True
                    sec = True
            if change:
                ret["Poles"][key2] = [p]
            else:
                ret["Poles"][key2].append(p)
            change = False
        first = False
        sec = False
        for z in self.z_pairs:
            if z.n == 1:
                key2 = "1st order"
                if not first:
                    change = True
                    first = True
            else:
                key2 = "2nd order"
                if not sec:
                    change = True
                    sec = True
            if change:
                ret["Zeros"][key2] = [z]
            else:
                ret["Zeros"][key2].append(z)
            change = False
        return ret

    def get_stages_plot(self, indexes, type: ShowType):
        plot_list = [[], ["", ""]]
        if len(self.sos):
            if type == ShowType.Total.value:
                zeros = []
                poles = []
                for z in self.z_pairs:
                    zeros.append(complex(0, z.im))
                    if z.n == 2:
                        zeros.append(complex(0, -z.im))
                for p in self.p_pairs:
                    poles.append(complex(p.p))
                    if p.q > 0:
                        poles.append(conjugate(p.p))
                transf = signal.ZerosPolesGain(zeros, poles, self.k_tot)
                w, mag = transf.freqresp(n=3000)
                f = w/(2*pi)
                plot_list = [[GraphValues(f, 20*log10(mag), False, False, True)], ["Frequency [Hz]", "Amplitude [dB]"]]
            else:
                if type == ShowType.Superposed.value[0]:
                    indexes = list(range(len(self.sos)))
                plot_list[0] = [self.sos[i].get_tf_plot(i) for i in indexes]
                plot_list[1] = ["Frequency [Hz]", "Amplitude [dB]"]
        return plot_list

    def get_dr(self, vi_min, vo_max):
        """Returns a tuple:
            (True, dr) if everytihing ok, (False, err_str) if error
            Could fail because of: Invalid vi values, or not all stages loaded"""
        ok = True
        end = True
        ret = ""
        for p in self.p_pairs:
            if not p.used:
                end = False
                ret = "N/A"
        if end:
            valid = self._validate_vi(vi_min, vo_max)
            ok = valid[0]
            ret = valid[1]
            if valid[0]:
                max_rd = 0
                for i in range(len(self.sos)):
                    rd = self._get_stg_dr(i, vi_min, vo_max)
                    if rd > max_rd:
                        max_rd = rd
                    ret = str(round(max_rd)) + " dB"
        return ok, ret

    def _get_stg_dr(self, i, vi_min, vo_max):
        """ Returns stage i dynamic range """
        partial_gain = 1
        for j in range(i+1): # recorro todas las etapas hasta la que quiero calcular el rango dinamico
            partial_gain *= self.sos[j].k
        vi_max = vo_max if partial_gain < 1 else vo_max/partial_gain
        vi_min = vi_min if partial_gain > 1 else vi_min/partial_gain # vi_min: minimo valor a la entrada tal que la salida no este en el piso de ruido y la entrada no este en el piso de ruido
        return 20*log10(vi_max/vi_min)

    def get_const_data(self, indexes, vi_min, vo_max):
        """Returns a dictionary with string values of the stage i"""
        ret = {"Q": ["", ""], "fo": ["", "Hz"], "DR": ["", "dB"]}
        if len(indexes) == 1:
            i = indexes[0]
            if i < len(self.sos):
                q = self.sos[i].pole.q
                if q > 0:
                    ret["Q"][0] = f"{q:.4f}"
                ret["fo"][0] = f"{self.sos[i].pole.fo:.1f}"
                if self._validate_vi(vi_min, vo_max)[0]:
                    pass
                    ret["DR"][0] = str(self._get_stg_dr(i, vi_min, vo_max))
        return ret

    @staticmethod
    def _validate_vi(vi_min, vo_max):
        ok = False
        ret = ""
        if vi_min < vo_max:
            if vi_min <= 2:
                if vo_max >= 3:
                    ok = True
                else:
                    ret = "Vo max should be greater than 3V"
            else:
                ret = "Vi min should be smaller than 2V (go to a less noisy place!)"
        else:
            ret = "Vo max must be greater than vi min"
        return ok, ret

    def get_save_info(self):
        return {"Sos": self.sos, "Zeros": self.z_pairs, "Poles": self.p_pairs}

    def load_saved_info(self, info: dict):
        self.sos = info["Sos"]
        self.z_pairs = info["Zeros"]
        self.p_pairs = info["Poles"]

    def set_selected(self, indexes: list):
        self.selected = indexes
