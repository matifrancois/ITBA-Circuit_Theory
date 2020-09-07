# python native modules

# third-party modules
from numpy import where

# AFM project modules
from Filters.Filters import *
from BackEnd.Output.Dot import Dot, INFINITE
from BackEnd.Output.Square import Square


class LowPass(Filter):
    def __init__(self):
        super().__init__(FilterTypes.LowPass.value)
        """ Load LowPass requirements for future usage """
        self.requirements = {TemplateInfo.k.value: None,
                             TemplateInfo.Aa.value: None,
                             TemplateInfo.Ap.value: None,
                             TemplateInfo.fa.value: None,
                             TemplateInfo.fp.value: None}

        self.defaults = {
            TemplateInfo.Aa.value: 40, TemplateInfo.Ap.value: 5, TemplateInfo.fa.value: 20000,
            TemplateInfo.fp.value: 2000,
            TemplateInfo.k.value: 0
        }

    def validate_requirements(self) -> (bool, str):
        ret = ""
        for each in self.requirements:
            if self.requirements[each] is None:
                ret = "Please enter a value for " + each[:where(" [")]
                return False, ret  # Check if every spec was loaded

        if self.requirements[TemplateInfo.Aa.value] > self.requirements[TemplateInfo.Ap.value]:
            if self.requirements[TemplateInfo.fa.value] > self.requirements[TemplateInfo.fp.value]:
                self.selectivity = self.requirements[TemplateInfo.fp.value] / self.requirements[TemplateInfo.fa.value]  # K = wp/wa
                self.normalized_freqs = [1/(2*pi), 1 / (2*pi*self.selectivity)]
                return True, ret
            else:
                ret = "fa must be greater than fp"
        else:
            ret = "Aa must be greater than Ap"

        """ If there is something wrong in the attenuations or frequencies I return False"""
        return False, ret

    def get_templates(self):
        fa = self.requirements[TemplateInfo.fa.value]
        fp = self.requirements[TemplateInfo.fp.value]
        Ap = self.requirements[TemplateInfo.Ap.value]
        Aa = self.requirements[TemplateInfo.Aa.value]
        sq1 = Square(Dot(0, Ap), Dot(0, INFINITE), Dot(fp, INFINITE), Dot(fp, Ap))
        sq2 = Square(Dot(fa, -INFINITE), Dot(fa, Aa), Dot(INFINITE, Aa), Dot(INFINITE, -INFINITE))

        sq1_n = Square(Dot(0, Ap), Dot(0, INFINITE), Dot(self.normalized_freqs[0], INFINITE), Dot(self.normalized_freqs[0], Ap))
        sq2_n = Square(Dot(self.normalized_freqs[1], -INFINITE), Dot(self.normalized_freqs[1], Aa), Dot(INFINITE, Aa), Dot(INFINITE, -INFINITE))

        denorm_template, norm_temlate = [sq1, sq2], [sq1_n, sq2_n]
        return {GraphTypes.Attenuation.value: denorm_template,
                GraphTypes.NormalizedAt.value: norm_temlate}
