# python native modules

# third-party modules
from scipy import signal
import numpy as np

# AFM project modules
from Approximations import Chevy1
from Approximations.Approx import Approximation
from Approximations.Butterworth import Butterworth
from Approximations.Cauer import Cauer
from Approximations.Chevy2 import ChebyII
from Approximations.Chevy1 import ChevyI
from Approximations.Legendre import Legendre
from Filters.Filters import FilterTypes
from Filters.Filters import TemplateInfo
from Filters.Filters import Filter


class Transitional(Approximation):

    def __init__(self):
        Approximation.__init__(self, "Transitional")
        self.application = [FilterTypes.HighPass.value, FilterTypes.LowPass.value, FilterTypes.BandPass.value, FilterTypes.BandReject.value]
        self.dict["Denorm."] = [(0, 100, True, int()), 0]
        self.dict["m"] = [(0, 100, False, int()), 50]
        self.approximations = ["Butterworth", "Cauer", "Chebyshev I", "Chebyshev II", "Legendre"]
        self.extra_combos.append(self.approximations)
        self.extra_combos.append(self.approximations)
        self.approx = [None, None]

    def load_information(self, filter_in_use: Filter):

        if filter_in_use.get_type() not in self.application:
            print("Something done wrong, Transitional filters are not valid for ", filter_in_use.get_type())
            return False

        specs = filter_in_use.get_requirements()
        for each in specs:
            self.information[each] = filter_in_use.get_req_value(each)
        return True

    def calculate(self, filter_in_use: Filter, kwargs):
        switcher = {
            "Approx 1": self._set_app1,
            "Approx 2": self._set_app2,
            "m": self._set_m
        }
        for key, value in kwargs.items():
            fun = switcher.get(key, lambda: "Invalid argument")
            lam = lambda: 0
            if type(fun) != type(lam):
                fun(value, filter_in_use)

        self.approx[0].calculate(filter_in_use, kwargs)
        z1, p1, k1, q = filter_in_use.get_z_p_k_q()
        self.approx[1].calculate(filter_in_use, kwargs)
        z2, p2, k2, q = filter_in_use.get_z_p_k_q()
        ord1 = len(p1)
        ord2 = len(p2)
        if ord1 != ord2:  # Me tengo que asegurar que los dos sean del mismo orden
            if ord1 < ord2:  # Si son distintos pongo N fijo y calculo denuevo al de orden menor
                kwargs["N"] = ord2
                if filter_in_use.get_type() == FilterTypes.BandPass.value or filter_in_use.get_type() == FilterTypes.BandReject.value:
                    kwargs["N"] = int(ord2/2)
                self.approx[0].calculate(filter_in_use, kwargs)
                z1, p1, k1, q = filter_in_use.get_z_p_k_q()
            else:
                if filter_in_use.get_type() == FilterTypes.BandPass.value or filter_in_use.get_type() == FilterTypes.BandReject.value:
                    kwargs["N"] = int(ord1 / 2)
                self.approx[1].calculate(filter_in_use, kwargs)
                z2, p2, k2, q = filter_in_use.get_z_p_k_q()

        p = np.multiply(np.power(p1, self.m), np.power(p2, (1 - self.m)))

        if len(z1) < len(z2):  # No esta en nigun lado esto, si anda hago un paper
            z = z1              # Esto anda bien, cuando termine TC hago el paper
        elif len(z1) > len(z2):
            z = z2
        else:
            z = np.multiply(np.power(z1, self.m), np.power(z2, (1 - self.m)))

        k = np.prod(p)/np.prod(z)*pow(10, self.information[TemplateInfo.k.value]/10)
        filter_in_use.load_z_p_k(z, p, k)

    def _set_app1(self, approx: str, filter_in_use: Filter):
        self._set_app(0, approx, filter_in_use)

    def _set_app2(self, approx: str, filter_in_use: Filter):
        self._set_app(1, approx, filter_in_use)

    def _set_app(self, i, approx: str, filter_in_use: Filter):
        switcher = {
            "Butterworth": Butterworth(),
            "Cauer": Cauer(),
            "Chebyshev I": ChevyI(),
            "Chebyshev II": ChebyII(),
            "Legendre": Legendre()
        }
        self.approx[i] = switcher[approx]
        self.approx[i].load_information(filter_in_use)

    def _set_m(self, m, filter_in_use: Filter):
        self.m = m/100
