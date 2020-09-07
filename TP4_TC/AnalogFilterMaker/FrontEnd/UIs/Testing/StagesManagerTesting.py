
from BackEnd.Output.plots import GraphValues
from FrontEnd.UIs.Testing.PoleTesting import PoleTesting
from FrontEnd.UIs.Testing.StageTesting import StageTesting
from FrontEnd.UIs.Testing.ZeroTesting import ZeroTesting



class StagesManagerTesting(object):

    def __init__(self):
        a = 0

    def auto_max_rd(self, vi_min, vi_max):
        a = 0

    def get_stages(self):
        return [StageTesting(1,2,5), StageTesting(4,4,8), StageTesting(3,2,1), StageTesting(4,4,8), StageTesting(3,2,1)]

    def add_stage(self, p_str: str, z_str: str) -> (bool, str):
        a = 0

    def shift_stages(self, indexes: list, left):
        a = 0

    def delete_stages(self, indexes: list):
        a = 0

    def calc_rd(self):
        return 60

    def set_gain(self, i, k) -> (bool, str):
        return False, "Ganancia no"

    def get_z_p_plot(self):
        return [
            [GraphValues([50, 500, 5000, 50000], [10, 100, 1000, 100], True, False,False, "Zeros",[2,2,1,1]),  # GRAF CEROS
             GraphValues([550000, 555, 10, 55], [155, 222, 887, 100], True, True,False, "Poles",[2,3,1,2])],  # GRAF POLOS
            ["Re", "Im"]]

    def get_z_p_dict(self):
        """ Returns a dictionary with all zeros and poles:
         { "Poles": {"1st order": [Poles], "2nd order": [Poles]}
           "Zeros": {"1st order": [Zeros], "2nd order": [Zeros]} } """
        dict = { "Poles": {"1st order": [PoleTesting(10, True), PoleTesting(5, True)], "2nd order": [PoleTesting(4), PoleTesting(3), PoleTesting(2)]},
           "Zeros": {"1st order": [ZeroTesting(2,3), ZeroTesting(1,2)], "2nd order": [ZeroTesting(20,1)]} }
        return dict

    def load_filter(self, filter):
        a =0

    def get_stages_plot(self, i , s):
        return [
            [GraphValues([0, 100, 105, 2000, 2500], [500, 1000, 20000, 30000, 400000], False, False, True),
             GraphValues([0, 151, 1000, 2011, 2800], [600, 1500, 20500, 45000, 800000], False, False, True)],
            ["freq", "module"]]

    def get_dr(self, vi_min, vo_max):
        return True, 60

    def get_const_data(self, i, vi_min, vo_max):
        dict = {
            "Q": ["10", ""]
            ,
            "Feq": ["100", "Hz"]
            ,
            "Fo": ["1000", "Hz"]
            ,
            "DR": ["10", "Hz"]
        }
        return dict