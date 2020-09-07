class Pole:
    def __init__(self, p: complex):
        self.p = p
        self.used = False
        self.fo = abs(self.p)
        if abs(p.imag) > 1e-9:
            self.q = self.fo / (2 * -self.p.real)
        else:
            self.q = -1

    def __eq__(self, other):
        return self.p == other.p

    def get_msg(self):
        aux = ""
        if self.q > 0:
            aux += f" - Q: {self.q:.2f}"
        if self.used:
            aux += " (used)"
        return f"fo:{self.fo:.1f}Hz" + aux


