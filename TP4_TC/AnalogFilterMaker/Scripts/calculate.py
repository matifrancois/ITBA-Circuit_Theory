# third-party modules

from numpy import unwrap
from numpy import diff
import json

# own modules

from Scripts.gauss import gauss_approximation
from Scripts.legendre import legendre_approximation


def calculate_gauss(transfer_calculator: callable, n_max: int, *args):
    data = {}
    outfile = open("gauss.json", "w")
    for i in range(1, n_max + 1):
        transfer_function = transfer_calculator(i, *args)
        w, mag, phase = transfer_function.bode()
        gd = -diff(unwrap(phase)) / diff(w)
        data[str(i)] = {}
        data[str(i)] = {"w": w.tolist(), "|H(jw)[dB]|": mag.tolist(), "Group delay": gd.tolist()}
    json.dump(data, outfile, indent=4)


if __name__== "__main__":
    calculate_approximation(gauss_approximation, 20)
    calculate_approximation(legendre_approximation, 20, 2)
