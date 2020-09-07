INFINITE = 10000000000


class Dot:
    def __init__(self, x_value, y_value):
        self.x_value = x_value
        self.y_value = y_value

    def get_tuple(self):
        return [self.x_value, self.y_value]