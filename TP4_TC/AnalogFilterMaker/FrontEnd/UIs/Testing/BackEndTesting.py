import matplotlib
from matplotlib import patches

from BackEnd.Output.Dot import Dot, INFINITE
from BackEnd.Output.Square import Square
from BackEnd.Output.plots import GraphTypes, GraphValues
from FrontEnd.UIs.Testing.ApproximationTesting import ApproximationTesting


class BackEndTesting:
    def __init__(self):
        self.dict = {}
        self.approx = {}

    def get_util(self):
        self.dict = {
            "Low pass": {"Gain [dB]": [[0, 100], 50],
                         "Attenuation [dB]": [[10, 20], 15],
                         "Fa [Hz]": [[0, 10000000], 1000]},
            "High pass": {"GaAAin [dB]": [[0, 1000], 500],
                          "Attenuation222 [dB]": [[100, 250], 150]}
        }

        # ApproximationTesting vendria a ser la clase Approximation
        self.approx = {
            "Low pass": [ApproximationTesting("Butterworth", {
                "Max Q": [(0, 100, False,int()), 50],
                "n": [[0, 10, True,float()], 5]
            }),
                         ApproximationTesting("Chebyshev", {
                             "MaxQcH": [[0, 57, False, float()], 27],
                             "NChe": [[0, 5, True,float()], 2],
                             "Rango Desn": [[0, 100, False, float()], 50]}),
                         ApproximationTesting("Transicional", {
                             "Max Q": [[0, 100, False, float()], 50],
                             "n": [[0, 10, True, int()], 5]
                         }, [["Chebyshev", "Gauss"], ["Butterworth", "Legendre"]])
                         ###IMPORTANTE, PARA LOS TRANSICIONALES PASAR 2 COMO ULTIMO ARGUMENTO. (COMO ESTA EN EL EJEMPLO) (2 VENDRIAN A SER LOS COMBO BOX EXTRAS)
                         ]
            ,
            "High pass": [ApproximationTesting("Butterworth", {
                "Max Q2": [[0, 100, False,float()], 50],
                "n2": [[0, 10, True,float()], 5]})]
        }
        return self.dict, self.approx

    def validate_filter(self, filter):
        return True, "Error in sdasdadadasdasdasdasdasdasdas  "

    def get_template(self, filter):
        rect1 = Square(Dot(0, -INFINITE), Dot(0, 300), Dot(50000, 300), Dot(50000, -INFINITE))
        rect2 = Square(Dot(300000, 20), Dot(300000, INFINITE), Dot(450000, INFINITE), Dot(450000, 20))
        rect3 = Square(Dot(2000000, -INFINITE), Dot(2000000, 300), Dot(INFINITE, 300), Dot(INFINITE, -INFINITE))
        dict = {"Attenuation Curves": [rect1, rect2, rect3],
                "Poles and Zeros": [rect1, rect3]}
        return dict


    def get_save_info(self):
        return {"hola": [4,5,5]}

    def load_save_info(self, dict):
        a=0


    def get_graphics(self, filter,
                   approximation):  ##IMPORTANTE. SI ES UN TRANSICIONAL. LOS DATOS DE QUE APROXIMACIONES SE USAN SE DEVUELVEN COMO CUALQUIER OTRA COSA. MIN Y MAX SON NONE.
        # EJEMPLO:
        # Approx 1: [[None, None, False], "Cheby"]
        # Approx 2: [[None,None, False, "Butter"]
        # El nombre de los paramatros seria Approx 2, Approx 2 y asi (se puede chequear cuantos son con approximation.extra_combos)
        graph_dict = {}
        graph_dict[GraphTypes.Attenuation.value] = [
            [GraphValues([0, 10, 15, 20, 25, 13000], [50, 100, 2000, 3000, 40000, 25])],
            ["freq", "module"]]

        graph_dict[GraphTypes.GroupDelay.value] = [
            [GraphValues([0, 100, 105, 2000, 2500], [500, 1000, 20000, 30000, 400000], False, False, True)],
            ["freq", "module"]]

        graph_dict[GraphTypes.PolesZeros.value] = [
            [GraphValues([50, 500, 5000, 50000], [10, 100, 1000, 10000], True, False,False, "Zeros",[2,2,1,1]),  # GRAF CEROS
             GraphValues([550000, 555, 10, 550000], [150545, 222222, 888877, 100500], True, True,False, "Poles",[2,3,1,2])],  # GRAF POLOS
            ["Re", "Im"]]
        ####IMPORTANTEE: PARA LOS POLOS Y CEROS AGREGAR UN PARAMETRO "ZEROS" O "POLOS" COMO ESTA EN EL EJEMPLO. ES PARA QUE QUEDEN LAS LEGENDS BIEN
        return graph_dict


    def _parse_filter(self, list):
        return {"hola":2}