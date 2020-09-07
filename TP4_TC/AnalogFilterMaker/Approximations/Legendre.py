"""
Approximation base class
"""

# python native modules

# third-party modules
import numpy as np
from matplotlib import pyplot as plt

from sympy import *
from scipy import signal
from scipy import special

from numpy import pi
from numpy import polymul
from numpy import polyadd
from numpy import polyint
from numpy import polyval
from numpy import polysub
from numpy import poly1d
from numpy import sqrt
from numpy import where
from numpy import log10

# AFM project modules
from Approximations.Approx import Approximation
from Filters.Filters import FilterTypes
from Filters.Filters import TemplateInfo
from Filters.Filters import Filter


class Legendre(Approximation):

    def __init__(self):
        Approximation.__init__(self, "Legendre")
        self.application = [FilterTypes.HighPass.value, FilterTypes.LowPass.value, FilterTypes.BandPass.value, FilterTypes.BandReject.value]
        self.information = {}
        self.dict["Denorm."] = [(0, 100, True, int()), 0]

    def load_information(self, filter_in_use: Filter):

        if filter_in_use.get_type() not in self.application:
            print("Something done wrong, Legendre is not valid for ", filter_in_use.get_type())
            return False

        specs = filter_in_use.get_requirements()
        for each in specs:
            self.information[each] = filter_in_use.get_req_value(each)

        self.selectivity = filter_in_use.get_selectivity()
        return True

    def calculate(self, filter_in_use: Filter, kwargs):
        super().calculate(filter_in_use, kwargs)
        z = []
        p = []
        k = 0
        n = 0
        """ First I calculate the Normalized LowPass, to get the useful w """

        if self.fixed_n > 0:
            n = self.fixed_n
        else:
            n, useful_w = self._legord(1, 1/self.selectivity,
                                       self.information[TemplateInfo.Ap.value], self.information[TemplateInfo.Aa.value],
                                       self.n_max)

        while True:
            zpk_n = self._get_tf(n)
            z_n, p_n, k_n = zpk_n.zeros, zpk_n.poles, abs(zpk_n.gain)
            """ Now check the desnomalization cte """
            w, h = signal.freqs_zpk(z_n, p_n, k_n)
            h = 20 * log10(abs(h))
            i = [abs(j + self.information[TemplateInfo.Aa.value]) for j in h]
            wa = w[i.index(min(i))]
            denorm_cte = (wa * (1 - self.denorm / 100) + self.denorm / (self.selectivity * 100))/wa
            _z = z_n * denorm_cte
            _p = p_n * denorm_cte
            _k = k_n * (denorm_cte ** (len(p_n) - len(z_n)))
            # _p = [complex(a[0], a[1]) for a in _p]
            """" Next we transform the LowPass into the requested filter """

            if filter_in_use.get_type() is FilterTypes.LowPass.value:
                """ If the approximation support the filter I continue """
                z, p, k = signal.lp2lp_zpk(_z, _p, _k, 2*pi*self.information[TemplateInfo.fp.value])
                filter_in_use.load_z_p_k(z, p, k)

            elif filter_in_use.get_type() is FilterTypes.HighPass.value:
                z, p, k = signal.lp2hp_zpk(_z, _p, _k, (2*pi)**2*self.information[TemplateInfo.fp.value])
                filter_in_use.load_z_p_k(z, p, k)

            elif filter_in_use.get_type() is FilterTypes.BandPass.value:
                Awp = self.information[TemplateInfo.fp_.value] - self.information[TemplateInfo.fp__.value]
                w0 = sqrt(self.information[TemplateInfo.fp_.value] * self.information[TemplateInfo.fp__.value])

                z, p, k = signal.lp2bp_zpk(_z, _p, _k, 2*pi*w0, Awp)
                filter_in_use.load_z_p_k(z, p, k)

            elif filter_in_use.get_type() is FilterTypes.BandReject.value:
                Awp = self.information[TemplateInfo.fp_.value] - self.information[TemplateInfo.fp__.value]
                w0 = sqrt(self.information[TemplateInfo.fp_.value] * self.information[TemplateInfo.fp__.value])

                z, p, k = signal.lp2bs_zpk(_z, _p, _k, 2*pi*w0, (2*pi)**2*Awp)
                filter_in_use.load_z_p_k(z, p, k)
            else:
                print("Legendre.py: Invalid filter type passed to Legendre aproximation")
                return
            if self.q_max >= filter_in_use.get_max_q() or n == self.n_max or self.fixed_n > 0:
                break
            n = n + 1
        # filter_in_use.load_normalized_z_p_k(z_norm, p_norm, k_norm)
        filter_in_use.load_normalized_z_p_k(_z, _p, _k)

    def _legord(self, w_p, w_a, a_p, a_a, n_max: int):
        n = 0
        use_w = 0
        for k in range(1, n_max+1):
            transfer_function = self._get_tf(k)
            w, mag, phase = transfer_function.bode(w=np.logspace(log10(w_p)-1, log10(w_a)+1, num=2000))
            i_p = where(w >= w_p)[0][0]
            mag_p = mag[i_p]
            i_a = where(w >= w_a)[0][0]
            mag_a = mag[i_a]
            if mag_a <= -a_a or k == n_max:
                n = k
                use_w = w[i_p]
                break
        return n, use_w

    def _get_tf(self, n: int):
        """
        Returns the normalized transfer function of the Legendre Approximation
        :param n: Order of the legendre polynomial
        :return: The lti transfer function from scipy signals
        """
        poly = self._den(n)
        gain = sqrt(polyval(poly, 0))
        poles = [
            complex(
                pole.real if abs(pole.real) > 1e-10 else 0,
                pole.imag if abs(pole.imag) > 1e-10 else 0
            )
            for pole in 1j * poly.roots if pole.real < 0
            ]
        for pole in poles:
            gain *= pole
        return signal.lti([], poles, gain)

    def _den(self, n: int):
        """
        :param n: Legendre approximation order
        :return: The Legendre Approximation Denominator
        """
        epsilon = self._epsilon() ** 2
        ln = self._odd_poly(n) if (n % 2) else self._even_poly(n)
        ln = epsilon * ln
        return polyadd(poly1d([1]), ln)

    def _epsilon(self):
        """
        Returns the legendre epsilon parameter with the given ap in dB
        :return: Epsilon legendre parameter
        """
        return sqrt(10 ** (self.information[TemplateInfo.Ap.value] / 10) - 1)

    def _even_poly(self, n: int):
        """
        Returns the integrated Legendre polynomial when the order is even.
        :param n: Even order of the polynomial required
        :return: Ln(x) expressed as poly1d from numpy
        """
        if n % 2:
            raise ValueError("Expecting an even n value for the Legendre polynomial")

        # First, calculate the integration polynomial as a sum of legendre polynomials
        k = n // 2 - 1
        b0 = 1 / sqrt((k + 1)*(k + 2))
        poly = poly1d([b0 if (k % 2) == 0 else 0])

        for i in range(1, k + 1):
            if ((k % 2) == 1 and (i % 2) == 0) or ((k % 2) == 0 and (i % 2) == 1):
                continue
            bi = b0 * (2*i + 1)
            new_poly = bi * self._polynomial(i)
            poly = polyadd(poly, new_poly)

        poly = polymul(poly, poly)
        poly = polymul(poly, poly1d([1, 1]))

        # Calculate the indefinite integration and upper/lower limits
        poly = polyint(poly)
        upper = poly1d([2, 0, -1])
        lower = poly1d([-1])

        # Using barrow and returning the result!
        return polysub(polyval(poly, upper), polyval(poly, lower))

    def _odd_poly(self, n: int):
        """
        Returns the integrated Legendre polynomial when the order is odd.
        :param n: Odd order of the polynomial required
        :return: Ln(x) expressed as poly1d from numpy
        """
        if (n % 2) == 0:
            raise ValueError("Expecting an odd n value for the Legendre polynomial")

        # First, calculate the integration polynomial as a sum of legendre polynomials
        k = (n - 1) // 2
        a0 = 1 / (sqrt(2) * (k + 1))
        poly = poly1d([a0])

        for i in range(1, k + 1):
            ai = a0 * (2*i + 1)
            poli = self._polynomial(i)
            new_poly = ai * poli
            poly = polyadd(poly, new_poly)

        poly = polymul(poly, poly)

        # Calculate the indefinite integration and upper/lower limits
        poly = polyint(poly)
        upper = poly1d([2, 0, -1])
        lower = poly1d([-1])

        # Using barrow and returning the result!
        return polysub(polyval(poly, upper), polyval(poly, lower))

    def _polynomial(self, n: int):
        """
        Returns the polynomial of n-th order from Legendre.
        :param n: Order of the polynomial
        :return: Pn(x) expressed as poly1d from numpy
        """
        if n < 0:
            print("LegendrePolynomial received a negative order!")
        return special.legendre(n)

