class PoleTesting:
    def __init__(self, p: complex, used = False):
        self.p = p
        self.used = used
        self.fo = abs(self.p)
        if abs(p.imag) > 1e-9:
            self.q = self.fo / (2 * self.p.real)
        else:
            self.q = -1

    def get_msg(self):
        aux = ""
        if self.q > 0:
            aux += " - Q: " + str(self.q)
        if self.used:
            aux += " (used)"
        return "fo: " + str(self.fo) + aux
