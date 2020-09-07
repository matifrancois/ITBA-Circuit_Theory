# python native modules

# third-party modules
from scipy import signal
import numpy as np

# AFM project modules
from Approximations.Approx import Approximation
from Filters.Filters import FilterTypes
from Filters.Filters import TemplateInfo
from Filters.Filters import Filter


class ChebyII(Approximation):

    def __init__(self):
        Approximation.__init__(self, "Chebyshev II")  # Band reject fuera, tira overflow
        self.application = [FilterTypes.HighPass.value, FilterTypes.LowPass.value, FilterTypes.BandPass.value]
        self.information = {}
        self.dict["Denorm."] = [(0, 100, True, int()), 0]

    def load_information(self, filter_in_use: Filter):

        if filter_in_use.get_type() not in self.application:
            print("Something done wrong, Cheby II is not valid for ", filter_in_use.get_type())
            return False

        specs = filter_in_use.get_requirements()
        for each in specs:
            self.information[each] = filter_in_use.get_req_value(each)

        if filter_in_use.get_type() is FilterTypes.BandReject.value:
            self.__adjust_w__(False)
        elif filter_in_use.get_type() is FilterTypes.BandPass.value:
            self.__adjust_w__(True)

        filter_in_use.load_requirements(self.information)

        self.selectivity = 1/filter_in_use.get_selectivity()  # Chevy 2 es un ansistema y va al reves pq normaliza en la
                                                              # banda de paso
        filter_in_use.selectivity = self.selectivity
        filter_in_use.normalized_freqs = [1/(2*np.pi*self.selectivity), 1/(2*np.pi)]
        return True

    def calculate(self, filter_in_use: Filter, kwargs):
        super().calculate(filter_in_use, kwargs)
        z = []
        p = []
        k = 0
        """ First I calculate the Normalized LowPass, to get the useful w """
        normalized_n, useful_w = signal.cheb2ord(1/self.selectivity, 1, self.information[TemplateInfo.Ap.value],
                                                 self.information[TemplateInfo.Aa.value], analog=True)
        if self.fixed_n > 0:
            normalized_n = self.fixed_n
        elif normalized_n > self.n_max:
            normalized_n = self.n_max

        while True:
            z_norm, p_norm, k_norm = signal.cheby2(normalized_n, self.information[TemplateInfo.Aa.value],
                                                   1, analog=True, output='zpk')

            """ Now check the desnomalization cte """
            w, h = signal.freqs_zpk(z_norm, p_norm, k_norm)
            h = 20 * np.log10(abs(h))
            i = [abs(j + self.information[TemplateInfo.Ap.value]) for j in h]
            fp = w[i.index(min(i))]
            denorm_cte = (fp * (1 - self.denorm / 100) + self.denorm / (100 * self.selectivity))/fp
            _z = z_norm * denorm_cte
            _p = p_norm * denorm_cte
            _k = k_norm * (denorm_cte ** (len(p_norm) - len(z_norm)))
            """" Next we transform the LowPass into the requested filter """

            if filter_in_use.get_type() is FilterTypes.LowPass.value:
                """ And transform the normalized low pass to the desire one """
                z, p, k = signal.lp2lp_zpk(_z, _p, _k, 2*np.pi*self.information[TemplateInfo.fa.value])
                filter_in_use.load_z_p_k(z, p, k)

            elif filter_in_use.get_type() is FilterTypes.HighPass.value:
                z, p, k = signal.lp2hp_zpk(_z, _p, _k, 2*np.pi**self.information[TemplateInfo.fa.value])
                filter_in_use.load_z_p_k(z, p, k)

            elif filter_in_use.get_type() is FilterTypes.BandPass.value:
                Awa = self.information[TemplateInfo.fa_.value] - self.information[TemplateInfo.fa__.value]
                w0 = np.sqrt(self.information[TemplateInfo.fa_.value] * self.information[TemplateInfo.fa__.value])

                z, p, k = signal.lp2bp_zpk(_z, _p, _k, 2*np.pi*w0, 2*np.pi*Awa)  # Desnormalizado
                filter_in_use.load_z_p_k(z, p, k)

            elif filter_in_use.get_type() is FilterTypes.BandReject.value:
                Awp = self.information[TemplateInfo.fp_.value] - self.information[TemplateInfo.fp__.value]
                w0 = np.sqrt(self.information[TemplateInfo.fa_.value] * self.information[TemplateInfo.fa__.value])

                z, p, k = signal.lp2bs_zpk(_z, _p, _k, 2*np.pi*w0, 2*np.pi**Awp)  # Desnormalizado
                filter_in_use.load_z_p_k(z, p, k)

            else:
                print("Chevy2.py: Invalid filter type passed to Inverse Chebyshev aproximation")
                return
            if self.q_max < 0 or self.q_max >= filter_in_use.get_max_q() or normalized_n == self.n_max or self.fixed_n > 0:
                break
            normalized_n = normalized_n + 1
        # filter_in_use.load_normalized_z_p_k(z_norm, p_norm, k_norm)
        filter_in_use.load_normalized_z_p_k(_z, _p, _k)
        filter_in_use.load_z_p_k(z, p, k)