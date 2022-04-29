from math import sqrt


class Circle:
    type = "Circle"

    def __init__(self, x1, y1, x2, y2):
        # (x1, y1) - центр окружности; (x2, y2) - точка на окружности
        self.center = (x1, y1)  # координаты центра окружности
        self.radius = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)  # длина радиуса
