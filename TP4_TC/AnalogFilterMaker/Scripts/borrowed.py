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

from math import factorial
from numpy import unwrap
from numpy import diff
from numpy import where
from numpy import divide
from numpy import prod
from numpy import log

from numpy import polymul
from numpy import polyadd
from numpy import polyint
from numpy import polyval
from numpy import polysub
from numpy import poly1d
from numpy import sqrt
from numpy import log10

from matplotlib import pyplot

import json

###############################
# Legendre Package Exceptions #
###############################


###########################
# General Usage Functions #
###########################
def match_filter_template(
        transfer_calculator: callable,
        ap: float, aa: float, wa: float,
        *args):
    """
    Iterates the order of the transfer function recalculating it until it matches with the template
    :param transfer_calculator: Callback to calculate the TransferFunction
    :param ap: Maximum pass band attenuation in dB
    :param aa: Minimum stop band attenuation in dB
    :param wa: Stop band normalized frequency
    :param args: Additional/Optional arguments to call transfer_calculator with other than using the order and ap
    :return: Transfer function from the scipy signal package
    """
    n_min = 1
    n_max = 30
    for n in range(n_min, n_max + 1):
        transfer_function = transfer_calculator(n, ap, *args)
        if verifies_filter_template(transfer_function, ap, aa, wa):
            return transfer_function
    else:
        return None


def verifies_filter_template(transfer, ap: float, aa: float, wa: float) -> bool:
    """
    Returns whether the normalized transfer function verifies or not the given normalized template.
    :param transfer: TransferFunction from the Scipy Signal package
    :param ap: Maximum pass band attenuation
    :param aa: Minimum stop band attenuation
    :param wa: Normalized stop band rad/sec frequency
    :return: boolean False or True
    """
    w, h = signal.freqresp(transfer, [1, wa])
    h = 20 * log10(abs(h))
    return h[0] >= -ap and h[1] <= -aa


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


###########################
# Gauss Package Functions #
###########################
def calculate_gauss(n_max: int):
    data = {}
    outfile = open("gauss.json", "w")
    for i in range(2, n_max + 1):
        transfer_function = gauss_approximation(i)
        #transfer_function = gauss_approximation(n_max)
        w, mag, phase = transfer_function.bode(n=1500)
        gd = -diff(unwrap(phase)) / diff(w)
        # pyplot.semilogx(w[:-1], gd, label=("Denormalized group delay n= "+str(n_max)))
        gd = divide(gd, gd[0])
        data[str(i)] = {}
        data[str(i)] = {"w": w.tolist(), "|H(jw)[dB]|": mag.tolist(), "Group delay": gd.tolist()}
        pyplot.semilogx(w[:-1], gd, label=("Normalized group delay n= "+str(i)))
        # pyplot.semilogx(w, mag, label=("Bode magnitude n= " + str(i)))
        # pyplot.plot(w, phase, label=("Bode phase n= " + str(n_max)))
        #pyplot.xlim(0, 5)
        #pyplot.ylim(-15, 0)
    json.dump(data, outfile, indent=4)
    outfile.close()


def gauss_approximation(n: int):
    """
    Returns the normalized transfer function of the Gauss Approximation
    :param n: Order of the gauss polynomial
    :return: Scipy signal transfer function
    """
    z, p, k = gauss_approximation_zpk(n)
    transfer_function = signal.ZerosPolesGain(z, p, k)
    return transfer_function


def gauss_approximation_zpk(n: int):
    """
    :param n: Gauss approximation order
    :return: The Gauss Approximation Zeros, Poles and Gain
    """
    num = [1.]
    den = []
    #gamma = log(2)
    gamma = 1
    for k in range(n+1, 1, -1):
        den.append((-gamma)**k/factorial(k))
        # den.append(1 / factorial(k))
        den.append(0)
    den.append(1.)
    transfer_function = signal.TransferFunction(num, den)   # tengo la transferencia al cuadrado
    p = transfer_function.poles
    print("n= " + str(n))
    print("All poles: " + str(p))
    p = p[where(p.real < -1e-10)]    # me quedo con los polos del semiplano izquierdo
    #print("n= " + str(n))
    print("Left poles: " + str(p))
    k = prod(abs(p))                 # para que la ganancia sea 1
    return [], p, k


if __name__ == "__main__":
    # ap = float(sys.argv[1])
    # aa = float(sys.argv[2])
    # wa = float(sys.argv[3])

    # transfer = match_filter_template(legendre_approximation, ap, aa, wa)
    # w, module, phase = transfer.bode(n=1000)
    pyplot.figure()
    calculate_gauss(10)
    # pyplot.semilogx(w, module)
    pyplot.xlabel('w [rad/seg]')
    pyplot.ylabel('Tau')
    pyplot.title('Gauss Approximation')
    pyplot.legend()
    pyplot.show()

    input("Press any key to exit the program...")