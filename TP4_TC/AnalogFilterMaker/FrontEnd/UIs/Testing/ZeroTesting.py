class ZeroTesting:
    def __init__(self, im, n):
        self.im = im
        self.n = n
        self.used = False

    def get_msg(self):
        using = ""
        if not self.used:
            using = " (used)"
        return "fo: " + str(abs(self.im)) + " - n: "