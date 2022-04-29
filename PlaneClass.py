from CircleClass import Circle
from WideAngleClass import WideAngle, create_equation, check_pos

from collections import deque
from math import sqrt, pi, acos, sin


class Plane:
    def __init__(self, center_x, center_y, scale=1):
        self.scale = round(scale)
        self.dots = deque()
        self.circles = list()
        self.angles = list()
        self.my_circle = None
        self.my_angle = None
        self.center = (center_x, center_y)

    def clear(self):
        self.circles.clear()
        self.angles.clear()
        self.my_circle = None
        self.my_angle = None

    def add(self, obj):
        try:
            if obj.type == "Circle":
                self.circles.append(obj)
            elif obj.type == "Angle":
                self.angles.append(obj)
        except:
            self.dots.append(obj)

    def addFromFile(self, fname):
        txt = open(fname, mode="r")
        str = txt.readlines()
        for s in str:
            points = extractNumbers(s)
            if len(points) == 4:
                self.circles.append(Circle(points[0], points[1], points[2], points[3]))
            else:
                self.angles.append(
                    WideAngle(points[0], points[1], points[2], points[3], points[4], points[5]))
        txt.close()

    def calculateCross(self):
        max_area = 0
        for angle in self.angles:
            for circle in self.circles:
                area, r = 0, circle.radius
                firstPoints, mainPoints, secondPoints, inAngle = findCrossPoints(angle, circle)
                countOfPoints = len(firstPoints) + len(mainPoints) + len(secondPoints)
                x1, y1, x2, y2 = angle.mainSegment[0], angle.mainSegment[1], \
                                 angle.mainSegment[2], angle.mainSegment[3]
                x0, y0 = circle.center[0], circle.center[1]
                if countOfPoints < 2:
                    area = pi * (r ** 2) if inAngle else 0
                elif countOfPoints < 4:
                    if len(firstPoints) == 1 and len(secondPoints) == 1:
                        # случай с прямоугольной трапецией
                        x4, y4, x5, y5 = firstPoints[0][0], firstPoints[0][1], secondPoints[0][0], \
                                         secondPoints[0][1]
                        h = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)  # высота трапеции
                        # стороны трапеции
                        a = sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2)
                        b = sqrt((x2 - x5) ** 2 + (y2 - y5) ** 2)
                        area += h * (a + b) / 2  # площадь трапеции
                        # ищем площадь сегмента
                        area += roundSegmentArea(x4, y4, x5, y5, r)
                    elif len(mainPoints) == 1:
                        Points = list()
                        if len(firstPoints) == 1:
                            Points = firstPoints if firstPoints != mainPoints else Points
                        if len(secondPoints) == 1:
                            Points = secondPoints if secondPoints != mainPoints else Points
                        x4, y4, x5, y5 = mainPoints[0][0], mainPoints[0][1], Points[0][0], \
                                         Points[0][1]
                        # x, y = точка, которая лежит внутри окружности
                        a = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
                        if a < r:
                            x, y = x1, y1
                        else:
                            x, y = x2, y2
                        a = sqrt((x - x4) ** 2 + (y - y4) ** 2)
                        b = sqrt((x - x5) ** 2 + (y - y5) ** 2)
                        area += a * b / 2
                        area += roundSegmentArea(x4, y4, x5, y5, r)
                    else:
                        if len(firstPoints) == 2:
                            Points = firstPoints
                        elif len(secondPoints) == 2:
                            Points = secondPoints
                        else:
                            Points = mainPoints
                        x4, y4, x5, y5 = Points[0][0], Points[0][1], Points[1][0], Points[1][1]
                        area += roundSegmentArea(x4, y4, x5, y5, r)
                        if inAngle:
                            area = pi * (r ** 2) - area
                elif countOfPoints < 6:
                    if len(firstPoints) == 2 and len(secondPoints) == 2:
                        area = pi * r ** 2
                        area -= roundSegmentArea(firstPoints[0][0], firstPoints[0][1],
                                                 firstPoints[1][0], firstPoints[1][1], r)
                        area -= roundSegmentArea(secondPoints[0][0], secondPoints[0][1],
                                                 secondPoints[1][0], secondPoints[1][0], r)
                    elif len(mainPoints) == 2:
                        if len(firstPoints) == 2:
                            Points = firstPoints
                        elif len(secondPoints) == 2:
                            Points = secondPoints
                        area = pi * r ** 2
                        area -= roundSegmentArea(Points[0][0], Points[0][1], Points[1][0],
                                                 Points[1][1], r)
                        area -= roundSegmentArea(mainPoints[0][0], mainPoints[0][1],
                                                 mainPoints[1][0], mainPoints[1][1], r)
                    else:
                        if len(secondPoints) == 2:
                            firstPoints, secondPoints = secondPoints, firstPoints
                            x1, y1, x2, y2 = x2, y2, x1, y1
                        x4, y4 = mainPoints[0][0], mainPoints[0][1]
                        x7, y7 = secondPoints[0][0], secondPoints[0][1]
                        x5, y5, x6, y6 = firstPoints[0][0], firstPoints[0][1], firstPoints[1][0], \
                                         firstPoints[1][1]
                        AB = sqrt((x1 - x5) ** 2 + (y1 - y5) ** 2)
                        CB = sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2)
                        b = sqrt((x1 - x6) ** 2 + (y1 - y6) ** 2)
                        if AB > b:
                            AB, b = b, AB
                            x5, y5, x6, y6 = x6, y6, x5, y5
                        a = sqrt((x2 - x7) ** 2 + (y2 - y7) ** 2)
                        h = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                        area += h * (a + b) / 2
                        area -= AB * CB / 2
                        area += roundSegmentArea(x4, y4, x5, y5, r)
                else:
                    area = pi * r ** 2
                    area -= roundSegmentArea(mainPoints[0][0], mainPoints[0][1], mainPoints[1][0],
                                             mainPoints[1][1], r)
                    area -= roundSegmentArea(firstPoints[0][0], firstPoints[0][1],
                                             firstPoints[1][0], firstPoints[1][1], r)
                    area -= roundSegmentArea(secondPoints[0][0], secondPoints[0][1],
                                             secondPoints[1][0], secondPoints[1][1], r)
                if area > max_area:
                    max_area = area
                    self.my_circle = circle
                    self.my_angle = angle
        return round(max_area / 10, 2)


def findCrossPoints(angle, circle):
    x1, y1, x2, y2 = angle.mainSegment[0], angle.mainSegment[1], angle.mainSegment[
        2], angle.mainSegment[3]
    x4, y4, x5, y5 = angle.firstSegment[2], angle.firstSegment[3], \
                     angle.secondSegment[2], angle.secondSegment[3]
    x0, y0, r = circle.center[0], circle.center[1], circle.radius
    inAngle = False
    mainPoints, firstPoints, secondPoints = list(), list(), list()
    if angle.vertical:
        if min(y1, y2) <= y0 <= max(y1, y2) and min(x1, x4) <= x0 <= max(x1, x4):
            inAngle = True
        # Точки пересечения окружности с главным сегментом (x = const)
        y = r ** 2 - (x1 - x0) ** 2
        if y >= 0:
            y, yo = y0 + sqrt(y), y0 - sqrt(y)
            if min(y1, y2) <= y <= max(y1, y2):
                mainPoints.append((x1, y))
            if min(y1, y2) <= yo <= max(y1, y2):
                mainPoints.append((x1, yo))
        # Точки пересечения с "первым" сегментом (y = const)
        x = r ** 2 - (y1 - y0) ** 2
        if x >= 0:
            x, xo = x0 + sqrt(x), x0 - sqrt(x)
            if min(x1, x4) <= x <= max(x1, x4):
                firstPoints.append((x, y1))
            if min(x1, x4) <= xo <= max(x1, x4):
                firstPoints.append((xo, y1))
        # Точки пересечения со "вторым" сегментом (y = const)
        x = r ** 2 - (y2 - y0) ** 2
        if x >= 0:
            x, xo = x0 + sqrt(x), x0 - sqrt(x)
            if min(x2, x5) <= x <= max(x2, x5):
                secondPoints.append((x, y2))
            if min(x2, x5) <= xo <= max(x2, x5):
                secondPoints.append((xo, y2))
    elif angle.horizontal:
        if min(x1, x2) <= x0 <= max(x1, x2) and min(y1, y4) <= y0 <= max(y1, y4):
            inAngle = True
        # Точки пересечения окружности с главным сегментом (y = const)
        x = r ** 2 - (y1 - y0) ** 2
        if x >= 0:
            x, xo = x0 + sqrt(x), x0 - sqrt(x)
            if min(x1, x2) <= x <= max(x1, x2):
                mainPoints.append((x, y1))
            if min(x1, x2) <= xo <= max(x1, x2):
                mainPoints.append((xo, y1))
        # Точки пересечения с "первым" сегментом (x = const)
        y = r ** 2 - (x1 - x0) ** 2
        if y >= 0:
            y, yo = y0 + sqrt(y), y0 - sqrt(y)
            if min(y1, y4) <= y <= max(y1, y4):
                firstPoints.append((x1, y))
            if min(y1, y4) <= yo <= max(y1, y4):
                firstPoints.append((x1, yo))
        # Точки пересечения со "вторым" сегментом (x = const)
        y = r ** 2 - (x2 - x0) ** 2
        if y >= 0:
            y, yo = y0 + sqrt(y), y0 - sqrt(y)
            if min(y2, y5) <= y <= max(y2, y5):
                secondPoints.append((x1, y))
            if min(y2, y5) <= yo <= max(y2, y5):
                secondPoints.append((x1, yo))
    else:
        m_k, m_b = create_equation(x1, y1, x2, y2)
        k1, b1 = create_equation(x1, y1, x4, y4)
        k2, b2 = create_equation(x2, y2, x5, y5)
        if check_pos(x1, y1, x2, y2, x0, y0) == angle.pos and check_pos(
                x1, y1, x4, y4, x0, y0) != check_pos(x2, y2, x5, y5, x0, y0):
            inAngle = True
        # Точки пересечения окружности с главным сегментом
        D4 = discriminant(x0, m_b, y0, m_k, r)
        if D4 >= 0:
            x = (x0 - m_k * m_b + m_k * y0 + sqrt(D4)) / (1 + m_k ** 2)
            xo = (x0 - m_k * m_b + m_k * y0 - sqrt(D4)) / (1 + m_k ** 2)
            if min(x1, x2) < x < max(x1, x2):
                y = m_k * x + m_b
                mainPoints.append((x, y))
            if min(x1, x2) < xo < max(x1, x2):
                y = m_k * xo + m_b
                mainPoints.append((xo, y))
        # Точки пересечения с "первым" сегментом
        D4 = discriminant(x0, b1, y0, k1, r)
        if D4 >= 0:
            x = (x0 - k1 * b1 + k1 * y0 + sqrt(D4)) / (1 + k1 ** 2)
            xo = (x0 - k1 * b1 + k1 * y0 - sqrt(D4)) / (1 + k1 ** 2)
            if min(x1, x4) < x < max(x1, x4):
                y = k1 * x + b1
                firstPoints.append((x, y))
            if min(x1, x4) < xo < max(x1, x4):
                y = k1 * xo + b1
                firstPoints.append((xo, y))
        # Точки пересечения со "вторым" сегментом
        D4 = discriminant(x0, b2, y0, k2, r)
        if D4 >= 0:
            x = (x0 - k2 * b2 + k2 * y0 + sqrt(D4)) / (1 + k2 ** 2)
            xo = (x0 - k2 * b2 + k2 * y0 - sqrt(D4)) / (1 + k2 ** 2)
            if min(x5, x2) < x < max(x5, x2):
                y = k2 * x + b2
                secondPoints.append((x, y))
            if min(x5, x2) < xo < max(x5, x2):
                y = k2 * xo + b2
                secondPoints.append((xo, y))
    return firstPoints, mainPoints, secondPoints, inAngle


def extractNumbers(string):
    points = list()
    x = ""
    for i in range(len(string)):
        if string[i].isdigit():
            x += string[i]
        elif x != "":
            points.append(int(x))
            x = ""
    if x != "":
        points.append(int(x))
    return points


def roundSegmentArea(x1, y1, x2, y2, r):
    l = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    a = acos((2 * r ** 2 - l ** 2) / (2 * r ** 2))
    area = ((r ** 2) / 2) * (a - sin(a))
    return area


def discriminant(x0, b, y0, k, r):
    # D4 = -(a ** 2) - (2 * a * k * b) + (2 * a * k * c) - (b ** 2) + (2 * b * c) - (c ** 2)
    # D4 += (r ** 2) + (k ** 2) * (r ** 2) - (2 * (k ** 2) * (a ** 2))
    D4 = (k * b - x0 - k * y0) ** 2 - (1 + (k ** 2)) * (x0 ** 2 + b ** 2 - 2 * y0 * b + y0 ** 2 - r ** 2)
    return D4
