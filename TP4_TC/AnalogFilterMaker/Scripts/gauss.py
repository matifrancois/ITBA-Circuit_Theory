# third-party modules
from scipy import signal
from math import factorial
from numpy import unwrap
from numpy import diff
from numpy import where
from numpy import divide
from numpy import prod
import json


###########################
# Gauss Package Functions #
###########################
def calculate_gauss(n_max: int):
    data = {}
    outfile = open("gauss.json", "w")
    for i in range(3, n_max + 1):
        transfer_function = gauss_approximation(i)
        w, mag, phase = transfer_function.bode(n=1500)
        gd = -diff(unwrap(phase)) / diff(w)
        gd = divide(gd, gd[0])
        data[str(i)] = {}
        data[str(i)] = {"w": w.tolist(), "|H(jw)[dB]|": mag.tolist(), "Group delay": gd.tolist()}
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
    :param n: Gauss approximation order. N_MIN = 3!!!!!!!!!!!!
    :return: The Gauss Approximation Zeros, Poles and Gain
    """
    num = [1.]
    den = []
    gamma = 0.995
    for k in range(n+1, 1, -1):
        den.append((-1)**k*gamma**k/factorial(k))
        # den.append(1 / factorial(k))    # normalizamos con gamma=1
        den.append(0)
    den.append(1.)
    transfer_function = signal.TransferFunction(num, den)   # tengo la transferencia al cuadrado
    p = transfer_function.poles
    p = p[where(p.real < 0)]    # me quedo con los polos del semiplano izquierdo
    k = prod(abs(p))                 # para que la ganancia sea 1
    return [], p, k


if __name__ == "__main__":
    calculate_gauss(20)
