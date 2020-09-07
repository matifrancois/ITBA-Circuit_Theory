class Square:
    def __init__(self, dot_bot_left, dot_upp_left, dot_upp_right, dot_bot_right):
        self.dot_bot_left = dot_bot_left
        self.dot_bot_right = dot_bot_right
        self.dot_upp_left = dot_upp_left
        self.dot_upp_right = dot_upp_right
        self.dots = [self.dot_bot_left, self.dot_upp_left, self.dot_upp_left, self.dot_bot_right]