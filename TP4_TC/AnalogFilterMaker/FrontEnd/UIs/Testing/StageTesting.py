
class StageTesting:
    def __init__(self, i, z, p):
        self.k = i
        self.z = z
        self.pole = p


    def get_tf_tex(self):
        return  '$C_{soil}=(' + str(self.k) + ' - n) C_m + \\theta_w C_w$'

