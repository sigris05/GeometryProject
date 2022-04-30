from CircleClass import Circle
from WideAngleClass import WideAngle, create_equation, check_pos

from collections import deque
from math import sqrt, pi, acos, sin


class Plane:
    def __init__(self, center_x, center_y, scale=1):
        self.scale = round(scale)
        self.dots = deque()  # очередь всех точек
        self.circles = list()  # список всех окружностей
        self.angles = list()  # список всех "лучей"
        self.my_circle = None  # окружность из искомой пары
        self.my_angle = None  # "луч" з искомой пары
        self.center = (center_x, center_y)  # координаты центра поля

    def clear(self):  # очищает все массивы и искомую пару
        self.circles.clear()
        self.angles.clear()
        self.dots.clear()
        self.my_circle = None
        self.my_angle = None

    def add(self, obj):  # добавляет объекты в массивы в зависимости от типа
        try:
            if obj.type == "Circle":
                self.circles.append(obj)
            elif obj.type == "Angle":
                self.angles.append(obj)
        except:  # точка передаётся как tuple, у которого нет метода type
            # из-за чего возникает ошибка и мы понимаем, что нам пихают точку
            self.dots.append(obj)

    def addFromFile(self, fname):  # добавление из файла
        txt = open(fname, mode="r")  # открываем файл
        # вытаскиваем массив всех строчек, считая, что каждая строчка отвечает за отдельную фигуру
        str = txt.readlines()
        for s in str:  # перебираем все строки из списка
            points = extractNumbers(s)  # магической функцией выделяем из строки числа
            # если точек достаточно, чтобы построить окружность, но не достаточно для "луча"
            if 3 < len(points) < 6:
                self.circles.append(Circle(points[0], points[1], points[2], points[3]))
            elif 6 <= len(points):
                self.angles.append(
                    WideAngle(points[0], points[1], points[2], points[3], points[4], points[5]))
        txt.close()  # закрываем файл

    def calculateCross(self):  # считаем наибольшую площадь
        max_area = 0
        # перебираем все пары окружностей и "широких" лучей
        for angle in self.angles:
            for circle in self.circles:
                area, r = 0, circle.radius
                # ищем точки со всем отрезками
                firstPoints, mainPoints, secondPoints, inAngle = findCrossPoints(angle, circle)
                # количество точек пересечения
                countOfPoints = len(firstPoints) + len(mainPoints) + len(secondPoints)
                x1, y1, x2, y2 = angle.mainSegment[0], angle.mainSegment[1], \
                                 angle.mainSegment[2], angle.mainSegment[3]
                x0, y0 = circle.center[0], circle.center[1]
                if countOfPoints < 2:
                    area = pi * (r ** 2) if inAngle else 0
                elif countOfPoints < 4:
                    if len(firstPoints) == 1 and len(secondPoints) == 1:
                        # случай с прямоугольной трапецией (пересекает два луча)
                        x4, y4, x5, y5 = firstPoints[0][0], firstPoints[0][1], secondPoints[0][0], \
                                         secondPoints[0][1]
                        h = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)  # высота трапеции
                        # стороны трапеции
                        a = sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2)
                        b = sqrt((x2 - x5) ** 2 + (y2 - y5) ** 2)
                        area += h * (a + b) / 2  # площадь трапеции
                        # ищем площадь сегмента
                        area += roundSegmentArea(x4, y4, x5, y5, x0, y0, r)
                    elif len(mainPoints) == 1:
                        # когда пересекает главный отрезок
                        Points = list()
                        if len(firstPoints) == 1:
                            Points = firstPoints if firstPoints != mainPoints else Points
                        if len(secondPoints) == 1:
                            Points = secondPoints if secondPoints != mainPoints else Points
                        x4, y4, x5, y5 = mainPoints[0][0], mainPoints[0][1], Points[0][0], \
                                         Points[0][1]
                        # расстояние от центра окружности до точки x1, y1
                        a = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
                        if a < r:  # точка лежит в окружности
                            x, y = x1, y1
                        else:
                            x, y = x2, y2
                        # x, y = точка, которая лежит внутри окружности
                        a = sqrt((x - x4) ** 2 + (y - y4) ** 2)
                        b = sqrt((x - x5) ** 2 + (y - y5) ** 2)
                        area += a * b / 2
                        area += roundSegmentArea(x4, y4, x5, y5, x0, y0, r)
                    else:
                        # когда пересекает только один луч
                        if len(firstPoints) == 2:
                            Points = firstPoints
                        elif len(secondPoints) == 2:
                            Points = secondPoints
                        else:
                            Points = mainPoints
                        x4, y4, x5, y5 = Points[0][0], Points[0][1], Points[1][0], Points[1][1]
                        area += roundSegmentArea(x4, y4, x5, y5, x0, y0, r)
                        if inAngle:
                            area = pi * (r ** 2) - area
                elif countOfPoints < 6:
                    if len(firstPoints) == 2 and len(secondPoints) == 2:
                        # пересекает сразу два луча
                        area = pi * r ** 2
                        area -= roundSegmentArea(firstPoints[0][0], firstPoints[0][1],
                                                 firstPoints[1][0], firstPoints[1][1], x0, y0, r)
                        area -= roundSegmentArea(secondPoints[0][0], secondPoints[0][1],
                                                 secondPoints[1][0], secondPoints[1][0], x0, y0, r)
                    elif len(mainPoints) == 2:
                        # пересекает основной отрезок в двух точках и один из лучей
                        if len(firstPoints) == 2:
                            Points = firstPoints
                        elif len(secondPoints) == 2:
                            Points = secondPoints
                        area = pi * r ** 2
                        area -= roundSegmentArea(Points[0][0], Points[0][1], Points[1][0],
                                                 Points[1][1], x0, y0, r)
                        area -= roundSegmentArea(mainPoints[0][0], mainPoints[0][1],
                                                 mainPoints[1][0], mainPoints[1][1], x0, y0, r)
                    else:
                        # пересекает главный отрезок в одной точке, один
                        # из лучей в двух, другой луч в одной
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
                        area += roundSegmentArea(x4, y4, x5, y5, x0, y0, r)
                else:
                    # есть точек пересечения (пересекает все отрезки в двух точках)
                    area = pi * r ** 2
                    area -= roundSegmentArea(mainPoints[0][0], mainPoints[0][1], mainPoints[1][0],
                                             mainPoints[1][1], x0, y0, r)
                    area -= roundSegmentArea(firstPoints[0][0], firstPoints[0][1],
                                             firstPoints[1][0], firstPoints[1][1], x0, y0, r)
                    area -= roundSegmentArea(secondPoints[0][0], secondPoints[0][1],
                                             secondPoints[1][0], secondPoints[1][1], x0, y0, r)
                if area > max_area:  # если площадь данной пары больше максимальной
                    max_area = area
                    # меняем пару
                    self.my_circle = circle
                    self.my_angle = angle
        return round(max_area / 10, 2)


def findCrossPoints(angle, circle):  # поиск точек пересечения
    x1, y1, x2, y2 = angle.mainSegment[0], angle.mainSegment[1], angle.mainSegment[
        2], angle.mainSegment[3]
    x4, y4, x5, y5 = angle.firstSegment[2], angle.firstSegment[3], \
                     angle.secondSegment[2], angle.secondSegment[3]
    x0, y0, r = circle.center[0], circle.center[1], circle.radius
    inAngle = False  # лежит ли центр окружности в "широком" угле
    mainPoints, firstPoints, secondPoints = list(), list(), list()
    # списки точек пересечения с соответствующими отрезками
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
        if check_pos(x1, y1, x2, y2, x0, y0) == angle.pos and check_pos(
                x1, y1, x4, y4, x0, y0) != check_pos(x2, y2, x5, y5, x0, y0):
            # если центр окружности и лучи лежат по одну сторону от главного отрезка
            # и по разные стороны от двух оставшихся сегментов
            inAngle = True
        m_k, m_b = create_equation(x1, y1, x2, y2)
        k1, b1 = create_equation(x1, y1, x4, y4)
        k2, b2 = create_equation(x2, y2, x5, y5)
        """решаем систему уравнений:
        y = kx + b
        (x - x0) ** 2 + (y - y0) ** 2 = r ** 2
        """
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


def extractNumbers(string):  # "вытаскивает" числа из строки
    points = list()  # массив чисел
    x = ""  # идущее сейчас "число"
    for i in range(len(string)):  # перебираем все символы строки
        if string[i].isdigit():  # если символ - цифра, то добавляем его к идущему сейчас "числу"
            x += string[i]
        elif x != "":  # иначе добавляем идущее сейчас число в points
            points.append(int(x))
            x = ""
    if x != "":
        points.append(int(x))
    return points  # возвращаем список всех точек


def roundSegmentArea(x1, y1, x2, y2, x0, y0, r):  # ищет площадь фигуры, отсечённую хордой
    a = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    b = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    c = sqrt((x2 - x0) ** 2 + (x2 - y0) ** 2)
    cosa = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
    if cosa < -1:
        cosa = -1
    elif cosa > 1:
        cosa = 1
    a = acos(cosa)
    area = ((r ** 2) / 2) * (a - sin(a))
    return area


def discriminant(x0, b, y0, k, r):  # дискриминант для уравнения пересечения окружности и прямой
    D4 = (k * b - x0 - k * y0) ** 2 - (1 + (k ** 2)) * (
            x0 ** 2 + b ** 2 - 2 * y0 * b + y0 ** 2 - r ** 2)
    return D4
