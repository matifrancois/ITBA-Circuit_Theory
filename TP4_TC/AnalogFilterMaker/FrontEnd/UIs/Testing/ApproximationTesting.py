class ApproximationTesting:
    def __init__(self, name, dict_of_features, list_of_extra_combos = []):
        self.name = name
        self.dict = dict_of_features
        self.extra_combos = list_of_extra_combos  # For transitional approximations (extra_combos would be equal to 2)
