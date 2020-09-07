"""
GraphPlots Class
"""

# python-native modules
from enum import Enum


# third-party modules

# project modules


class GraphTypes(Enum):
    """ GraphTypes """
    Attenuation = "Attenuation Curves"
    PolesZeros = "Poles and Zeros"
    GroupDelay = "Group Delay"
    MaxQ = "Maximum Q"
    #Agregar el restooo


class GraphValues:
    """ GraphValues """

    def __init__(self, x_values, y_values, scattered=False, x_marks=False, log=False, extra_information="", n_array = []):
        self.x_values = x_values
        self.y_values = y_values
        self.scattered = scattered
        self.x_marks = x_marks
        self.extra_information = extra_information
        self.log = log
        self.n_array = n_array
