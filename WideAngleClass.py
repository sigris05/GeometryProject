class WideAngle:
    type = "Angle"

    def __init__(self, x1, y1, x2, y2, x3, y3):
        # (x1, y1) и (x2, y2) задают отрезок; (x3, y3) задают сторону, в которую направлены прямые
        self.mainSegment = (x1, y1, x2, y2)
        self.vertical, self.horizontal = False, False
        self.pos = pos = check_pos(x1, y1, x2, y2, x3, y3)
        if x1 == x2:
            x4 = x1 + 10000 if x3 >= x1 else x1 - 10000
            y4 = y1
            self.vertical = True
        elif y1 == y2:
            y4 = y1 + 10000 if y3 - y1 >= 0 else y1 - 10000
            x4 = x1
            self.horizontal = True
        else:
            # переменная pos показывает по какую сторону от отрезка отложены лучи
            k, b = create_equation(x1, y1, x2, y2)
            # y = kx + b
            b1 = x1 / k + y1
            x4 = x1 + 1
            y4 = -x4 / k + b1
            line = ((x4 - x2) * (y1 - y2) - (y4 - y2) * (x1 - x2)) > 0
            if pos == line:
                if abs(y1 - y4) > 1:
                    y4 = y1 + 10000 if y4 > y1 else y1 - 10000
                    x4 = (b1 - y4) * k
                else:
                    x4 = x1 + 10000
                    y4 = -x4 / k + b1
            else:
                if abs(y1 - y4) > 1:
                    y4 = y1 - 10000 if y4 > y1 else y1 + 10000
                    x4 = (b1 - y4) * k
                else:
                    x4 = x1 - 10000
                    y4 = -x4 / k + b1
        self.firstSegment = (x1, y1, round(x4), round(y4))
        x5, y5 = x4 + x2 - x1, y4 + y2 - y1
        self.secondSegment = (x2, y2, round(x5), round(y5))


def check_pos(x1, y1, x2, y2, x3, y3):
    return ((x3 - x2) * (y1 - y2) - (y3 - y2) * (x1 - x2)) >= 0


def create_equation(x1, y1, x2, y2):
    # y = kx + b
    if x1 == x2:
        return None, None
    k = (y2 - y1) / (x2 - x1)
    b = y1 - x1 * (y2 - y1) / (x2 - x1)
    return k, b
