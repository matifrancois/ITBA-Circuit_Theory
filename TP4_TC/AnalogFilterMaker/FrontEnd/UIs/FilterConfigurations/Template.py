from matplotlib import patches

from BackEnd.Output.Dot import INFINITE


class Template:
    def __init__(self, name, squares=[], enabled=True):
        self.squares = []
        self.squares = squares
        self.enabled = enabled
        self.name = name

    def find_axes_limits(self):
        max_x_dot = 0
        min_x_dot = INFINITE
        max_y_dot = 0
        min_y_dot = INFINITE
        for square in self.squares:
            for dot in square.dots:
                if dot.x_value != INFINITE and dot.x_value > max_x_dot:
                    max_x_dot = dot.x_value
                if dot.y_value != INFINITE and dot.y_value > max_y_dot:
                    max_y_dot = dot.y_value
                if dot.x_value != 0 and dot.x_value < min_x_dot:
                    min_x_dot = dot.x_value
                if dot.y_value != -INFINITE and dot.y_value < min_y_dot:
                    min_y_dot = dot.y_value
        x_bound = [min_x_dot/10, max_x_dot*10]
        y_bound = [0, max_y_dot + max_y_dot * 0.5]
        return [x_bound, y_bound]

    def get_matplotlib_squares(self):
        mpl_squares = []
        for square in self.squares:
            x_0 = square.dot_bot_left.get_tuple()
            height = abs(square.dot_upp_left.y_value - square.dot_bot_left.y_value)
            width = abs(square.dot_bot_right.x_value - square.dot_bot_left.x_value)
            mpl_squares.append(patches.Rectangle((x_0[0], x_0[1]), width, height, alpha = 0.5))
        return mpl_squares
