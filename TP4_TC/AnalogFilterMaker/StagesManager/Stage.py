from scipy.signal import ZerosPolesGain, TransferFunction

from numpy import pi, log10, conjugate, imag
from BackEnd.Output.plots import GraphValues
from StagesManager import Zero, Pole


class Stage:
    def __init__(self, z: Zero, p: Pole, k):
        self.k = k
        self.z = z
        self.pole = p

    def get_tf_plot(self, i):
        if self.z is not None:
            z = [complex(0, self.z.im), complex(0, -self.z.im)] if self.z.n == 2 else [complex(0, 0)]
        else:
            z = []
        k_correct = abs(self.pole.p)**2*self.k if self.pole.q > 0 else abs(self.pole.p)*self.k
        p = [self.pole.p, conjugate(self.pole.p)] if self.pole.q > 0 else [self.pole.p]
        transfer_function = ZerosPolesGain(z, p, k_correct)
        w, h = transfer_function.freqresp(n=3000)
        f = w/(2*pi)
        mag = 20*log10(h)
        return GraphValues(f, mag, False, False, True, f'Stage {i + 1}')

    def get_tf_tex(self):
        if self.z is not None:
            z = [complex(0, self.z.im), complex(0, -self.z.im)] if self.z.n == 2 else [complex(0, 0)]
        else:
            z = []
        p = [self.pole.p, conjugate(self.pole.p)] if self.pole.q > 0 else self.pole.p
        zpk = ZerosPolesGain(z, p, self.k)
        transfer_function = zpk.to_tf()
        num = transfer_function.num
        den = transfer_function.den
        ret = "$H(s)=\\frac{"
        i=0
        for i in range(len(num)-1, 0-1, -1):
            if abs(num[i]) > 0:
                if i < len(num) - 1:
                    ret += '+'
                ret += f'{num[i]:.1f}'
                if i > 0:
                    ret += f's'
                if i > 1:
                    ret += f'^{i}'
        ret += "}{"
        for i in range(len(den)-1, 0-1, -1):
            if abs(den[i]) > 0:
                if i < len(den) - 1:
                    ret += '+'
                ret += f'{den[i]:.1f}'
                if i > 0:
                    ret += f's'
                if i > 1:
                    ret += f'^{i}'
        ret += "}$\n\n"
        ord = 2 if self.pole.q > 0 else 1
        ret += f'Q={self.pole.q:.2}    n={ord}' if ord == 2 else f'n={ord}'
        return ret

    def set_gain(self, k):
        self.k = k
