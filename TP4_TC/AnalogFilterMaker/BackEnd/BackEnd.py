# python native modules

# third-party modules

# AFM project modules
from Approximations.Butterworth import Butterworth
from Approximations.Chevy1 import ChevyI
from Approximations.Chevy2 import ChebyII
from Approximations.Cauer import Cauer
from Approximations.Bessel import Bessel
from Approximations.Gauss import Gauss
from Approximations.Legendre import Legendre
from Approximations.Transitional import Transitional

from Filters.Filters import Filter
from Filters.LowPass import LowPass
from Filters.HighPass import HighPass
from Filters.BandPass import BandPass
from Filters.BandReject import BandReject
from Filters.GroupDelay import GroupDelay
from Filters.Filters import FilterTypes
from Filters.Filters import TemplateInfo

from Filters.Filters import GraphTypes


class BackEnd:
    def __init__(self, save_info=None):
        self.lp = LowPass
        self.all_filters = [LowPass(), HighPass(), BandPass(), BandReject(), GroupDelay()]
        self.all_approximations = [Bessel(), Butterworth(), ChevyI(), ChebyII(), Cauer(), Gauss(), Legendre(), Transitional()]
        self.dynamic_filters = save_info if save_info else []
        self.fil_dict = {}
        self.filters_specs = {}
        for fil in self.all_filters:
            approximations = []
            for approx in self.all_approximations:
                if approx.is_available(fil.get_type()):
                    approximations.append(approx)
            self.fil_dict[fil.get_type()] = approximations
            specs = fil.get_requirements()
            useful_dict = {}
            for request in specs:
                useful_dict[request] = [fil.get_limit(request), fil.get_default(request)]
            self.filters_specs[fil.get_type()] = useful_dict
    """ Returns """


    def get_util(self):
        return self.filters_specs, self.fil_dict

    def validate_filter(self, filter) -> (bool, str):  # Recibo [FilterType, data] VER
        my_filter = self._parse_filter(filter)
        return my_filter.validate_requirements()

    def get_template(self, filtro, approximation=None):
        my_filter = self._parse_filter(filtro)
        if approximation is not None:
            if approximation[0] == "Chebyshev II":
                approx_dict = {}
                for key, value in approximation[1].items():
                    if value[1] is not None:
                        approx_dict[key] = value[1]
                for each in self.all_approximations:
                    if each.name is approximation[0]:
                        each.load_information(my_filter)  # Hago que chevy 2 cambie la plantilla normalizada
        return my_filter.get_templates()

    def get_graphics(self, filtro, aproximacion):
        my_filter = self._parse_filter(filtro)
        approx_dict = {}
        for key, value in aproximacion[1].items():
            if value[1] is not None:
                approx_dict[key] = value[1]
        for each in self.all_approximations:
            if each.name is aproximacion[0]:
                each.load_information(my_filter)
                each.calculate(my_filter, approx_dict)
        self.dynamic_filters.append(my_filter)
        return my_filter.get_all_graphs()

    def get_filter(self, id: int):
        return self.dynamic_filters[id]

    def del_filter(self, id: int):
        self.dynamic_filters.pop(id)

    def _parse_filter(self, front_end_filter) -> Filter:
        """ Busco el tipo de filtro que esta seleccionado """
        filters = None
        for fil in self.all_filters:
            if fil.get_type() is front_end_filter[0]:
                """ Creo dinamicamente un filtro del tipo requerido """
                filters = fil.__new__(type(fil))
                filters.__init__()

        specs = {}
        for aspect in front_end_filter[1]:
            specs[aspect] = front_end_filter[1][aspect][1]
        filters.load_requirements(specs)
        return filters

    def get_save_info(self):
        return {"Dynamic filters": self.dynamic_filters}

    def load_save_info(self, save_info):
        self.dynamic_filters = save_info["Dynamic filters"]
        #self.__init__(save_info["Dynamic filters"])

    def reset(self):
        self.__init__()