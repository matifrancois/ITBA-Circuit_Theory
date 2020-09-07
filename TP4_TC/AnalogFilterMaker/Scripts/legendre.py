""" Legendre Function for Analog Filters
    The main execution of the program calculates the normalized transfer function to match
    the normalized template given in the order of ap, aa and wa from the command-line arguments.
    Author: Lucas A. Kammann
"""

# python native modules
import sys

# third-party modules
from scipy import special
from scipy import signal

from numpy import polymul
from numpy import polyadd
from numpy import polyint
from numpy import polyval
from numpy import polysub
from numpy import poly1d
from numpy import sqrt

import json


def calculate_legendre(n_max : int, ap: float):
    data = {}
    outfile = open("legendre.json", "w")
    for i in range(1, n_max + 1):
        transfer_function = legendre_approximation(i, ap)
        w, mag, phase = transfer_function.bode()
        data[str(i)] = {}
        data[str(i)] = {"w": w.tolist(), "|H(jw)[dB]|": mag.tolist()}
    json.dump(data, outfile, indent=4)


##############################
# Legendre Package Functions #
##############################
def legendre_approximation(n: int, ap: float):
    """
    Returns the normalized transfer function of the Legendre Approximation
    :param n: Order of the legendre polynomial
    :param ap: Maximum attenuation of the pass band in dB
    :return: The lti transfer function from scipy signals
    """
    poly = legendre_approximation_denominator(n, ap)
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


def legendre_approximation_denominator(n: int, ap: float):
    """
    :param n: Legendre approximation order
    :param ap: Maximum band pass attenuation
    :return: The Legendre Approximation Denominator
    """
    epsilon = legendre_epsilon(ap) ** 2
    ln = legendre_odd_integrated_polynomial(n) if (n % 2) else legendre_even_integrated_polynomial(n)
    ln = epsilon * ln
    return polyadd(poly1d([1]), ln)


def legendre_epsilon(ap: float):
    """
    Returns the legendre epsilon parameter with the given ap in dB
    :param ap: Pass band maximum attenuation in dB
    :return: Epsilon legendre parameter
    """
    return sqrt(10 ** (ap / 10) - 1)


def legendre_even_integrated_polynomial(n: int):
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
        new_poly = bi * legendre_polynomial(i)
        poly = polyadd(poly, new_poly)

    poly = polymul(poly, poly)
    poly = polymul(poly, poly1d([1, 1]))

    # Calculate the indefinite integration and upper/lower limits
    poly = polyint(poly)
    upper = poly1d([2, 0, -1])
    lower = poly1d([-1])

    # Using barrow and returning the result!
    return polysub(polyval(poly, upper), polyval(poly, lower))


def legendre_odd_integrated_polynomial(n: int):
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
        poli = legendre_polynomial(i)
        new_poly = ai * poli
        poly = polyadd(poly, new_poly)

    poly = polymul(poly, poly)


    # Calculate the indefinite integration and upper/lower limits
    poly = polyint(poly)
    upper = poly1d([2, 0, -1])
    lower = poly1d([-1])

    # Using barrow and returning the result!
    return polysub(polyval(poly, upper), polyval(poly, lower))


def legendre_polynomial(n: int):
    """
    Returns the polynomial of n-th order from Legendre.
    :param n: Order of the polynomial
    :return: Pn(x) expressed as poly1d from numpy
    """
    if n < 0:
        raise ValueError("LegendrePolynomial received a negative order!")
    return special.legendre(n)


if __name__== "__main__":
    calculate_legendre(20)
