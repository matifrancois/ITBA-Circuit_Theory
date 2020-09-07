# python native modules

# third-party modules
from scipy import signal
import numpy as np
from matplotlib import pyplot as plt

# AFM project modules
from Approximations.Approx import Approximation
from Filters.Filters import FilterTypes
from Filters.Filters import TemplateInfo
from Filters.Filters import Filter


class Bessel(Approximation):

    def __init__(self):
        Approximation.__init__(self, "Bessel")
        self.application = [FilterTypes.GroupDelay.value]

    def load_information(self, filter_in_use: Filter):

        self.information.clear()

        if filter_in_use.get_type() not in self.application:
            print("Something done wrong, Bessel is not valid for ", filter_in_use.get_type())
            return False

        specs = filter_in_use.get_requirements()
        for each in specs:
            self.information[each] = filter_in_use.get_req_value(each)

        return True

    def calculate(self, filter_in_use: Filter, kwargs):
        super().calculate(filter_in_use, kwargs)
        z = []
        p = []
        k = 0
        """ First I calculate the Normalized LowPass, to get the useful w """
        normalized_n, useful_w = self._bessord(2*np.pi*self.information[TemplateInfo.ft.value], self.information[TemplateInfo.tol.value],
                                               self.information[TemplateInfo.gd.value], self.n_max)
        if self.fixed_n > 0:
            normalized_n = self.fixed_n
        elif normalized_n > self.n_max:
            normalized_n = self.n_max

        while True:
            """ First search the order and the normalizer 'cut' frequency """
            z_norm, p_norm, k_norm = signal.bessel(normalized_n, 1, analog=True, output='zpk', norm='delay')
            # w, h = signal.freqs_zpk(z_norm, p_norm, k_norm)
            # plt.semilogx(w[1:]/(1*np.pi), -np.diff(np.unwrap(np.angle(h))) / np.diff(w))
            if filter_in_use.get_type() is FilterTypes.GroupDelay.value:
                z, p, k = signal.bessel(normalized_n, useful_w, 'low', True, 'zpk', norm='delay')
                filter_in_use.load_z_p_k(z, p, k)
            else:
                print("Bessel.py: Invalid filter type passed to Bessel aproximation")
                return
            if self.q_max < 0 or self.q_max >= filter_in_use.get_max_q() or normalized_n == self.n_max or self.fixed_n > 0:
                break
            normalized_n = normalized_n + 1
        filter_in_use.load_normalized_z_p_k(z_norm, p_norm, k_norm)

    def _bessord(self, wrg, tol, tau_0, max_order):
        wrgn = wrg*tau_0*1e-6
        n = 0
        while True:  # do{}while() statement python style
            n = n+1
            z_n, p_n, k_n = signal.bessel(n, 1, 'low', analog=True, output='zpk', norm='delay')
            w, h = signal.freqs_zpk(z_n, p_n, k_n, worN=np.logspace(-1, np.log10(wrgn)+1, num=2000))
            g_delay = -np.diff(np.unwrap(np.angle(h)))/np.diff(w)
            w_prima = [abs(j-wrgn) for j in w]
            i = w_prima.index(min(w_prima))  # Busco el wrgn (en su defecto el mas cercano)
            if g_delay[i] >= (1-tol/100) or n is max_order:
                break
        return n, 1/(tau_0*1e-6)
