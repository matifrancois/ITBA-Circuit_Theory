from FrontEnd.UIs.UIConfigurations.ParameterLayout import ApproximationParameterLayout, DefaultSlider, \
    DefaultComboBox, DefaultNumberEdit, DefaultSliderWithSpinBox


class UIApproximation:
    def __init__(self,approximation, approx_name_list = []):
        self.name = approximation.name
        self.parameter_list = []
        self.approximation_list = approx_name_list
        dict_of_features = approximation.dict
        self.extra_combos = approximation.extra_combos
        for i in range(0, len(self.extra_combos)):
            self.parameter_list.append(ApproximationParameterLayout("Approx " + str(i+1), DefaultComboBox(self.extra_combos[i]), False))
        for feature in dict_of_features:
            if isinstance(dict_of_features[feature][0][3] ,float ):
                self.parameter_list.append(ApproximationParameterLayout(feature, DefaultSliderWithSpinBox(dict_of_features[feature][0][0],
                                                                                  dict_of_features[feature][0][1],
                                                                                  dict_of_features[feature][1]), dict_of_features[feature][0][2]))

            elif isinstance(dict_of_features[feature][0][3],int):
                self.parameter_list.append(ApproximationParameterLayout(feature, DefaultSlider(dict_of_features[feature][0][0],
                                                                                   dict_of_features[feature][0][1],
                                                                                   dict_of_features[feature][1]),dict_of_features[feature][0][2]))
    def make_approx_dict(self):
        dict = {}
        for parameter in self.parameter_list:
            if not parameter.toggleable or not parameter.auto:
                dict[parameter.name] = [[parameter.get_min(), parameter.get_max(), parameter.toggleable], parameter.get_value()]
            else:
                dict[parameter.name] = [[parameter.get_min(), parameter.get_max(), parameter.toggleable],
                                      None]


        return dict
