"""Intro.
Так получилось, что при проектировании смешались понятия "широкий угол" и "широкий луч",
поэтому на протяжении всего кода встречается WideAngle и Angle. Несмотря на то, что это
переводиться, как "угол", подразумевается луч."""

import sys
from math import sqrt

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import Qt, QPoint
from design.window import Ui_GeometryProblem

from PlaneClass import Plane, extractNumbers
from WideAngleClass import WideAngle, create_equation, check_pos
from CircleClass import Circle


class GeometryWidget(QMainWindow, Ui_GeometryProblem):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.max_x, self.max_y, self.min_x, self.min_y = 799, 449, 199, 1  # границы рамки
        self.plane = Plane(500, 225)  # создаём поле с центром в точке (500, 225)
        # присваиваем функции кнопкам
        self.LeftBut.clicked.connect(lambda: self.rotatePlane("left"))
        self.RightBut.clicked.connect(lambda: self.rotatePlane("right"))
        self.DownBut.clicked.connect(lambda: self.rotatePlane("down"))
        self.UpBut.clicked.connect(lambda: self.rotatePlane("up"))
        self.ScaleSlider.valueChanged[int].connect(self.scalePlane)
        self.DrawBut.clicked.connect(self.update)
        self.LoadFileBut.clicked.connect(self.loadFromFile)
        self.ClearBut.clicked.connect(self.clearPlane)
        self.AddAngleBut.clicked.connect(self.addAngle)
        self.AddCircleBut.clicked.connect(self.addCircle)
        self.CalculateBut.clicked.connect(self.solveProblem)

    def paintEvent(self, event):  # функция, которая отвечает за рисование
        painter = QPainter()  # создаём Painter
        painter.begin(self)
        self.drawShapes(painter)  # рисует все фигуры
        self.drawFrame(painter)  # рисует рамку координатной плоскости
        self.drawBoards(painter)  # закрашивает поле вне координатной плоскости
        painter.end()  # выключаем Painter

    def mousePressEvent(self, event):  # считывание точек с мышки
        s = self.plane.scale  # масштаб
        coord = (event.x(), event.y())  # получаем координаты клика
        # проверяем был ли клик внутри рамки
        if self.min_x < coord[0] < self.max_x and self.min_y < coord[1] < self.max_y:
            # преобразуем полученные координаты в нужный для вычислений "формат"
            coord = ((event.x() - self.plane.center[0] + s - 1) // s,
                     (-event.y() + self.plane.center[1]) // s)
            # *меняем знак y, т.к. система координат окна не совпадает с привычной декартовой
            # системой
            self.plane.add(coord)  # добавляем точку на plane
            self.update()  # заново отрисовываем

    def keyPressEvent(self, event):  # регистрируем нажатие на клавиатуру
        if int(event.modifiers()) == Qt.ControlModifier:
            if event.key() == Qt.Key_Left:  # стрелочка влево
                self.rotatePlane("left")
            if event.key() == Qt.Key_Right:  # стрелочка вправо
                self.rotatePlane("right")
            if event.key() == Qt.Key_Down:  # стрелочка вниз
                self.rotatePlane("down")
            if event.key() == Qt.Key_Up:  # стрелочка вверх
                self.rotatePlane("up")

    def loadFromFile(self):  # загрузка точек из файла
        try:
            # открываем диалоговое окно для выбора файла
            fname = QFileDialog.getOpenFileName(self, "Выбрать файл с точками", "",
                                                "Текстовый файл (*.txt)")[0]
            # передаём путь к файлу встроенной в plane функции
            self.plane.addFromFile(fname)
        except:  # если возникли какие-то проблемы со считыванием из файла (из-за недостатка
            # координат или неверного формата) информируем пользователя
            self.WarningLabel.setText("Выбран\nнекорректный\nфайл!")
        self.update()  # всё отрисовываем

    def addCircle(self):  # добавляем окружность на plane
        # получаем координаты из соответствующих полей
        firstCoords = self.CenterCoordCircle.toPlainText()
        secondCoords = self.SecondCoordCircle.toPlainText()
        if firstCoords == "" or secondCoords == "":
            # если хотя бы одно из полей пустое, пытаемся взять точки из начала очереди
            try:
                firstCoords = self.plane.dots.popleft()
                secondCoords = self.plane.dots.popleft()
                circle = Circle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1])
                self.plane.add(circle)
                self.WarningLabel.setText("")
            except:  # если в очереди недостаточно точек, выводим предупреждение
                self.WarningLabel.setText("Недостаточно\nточек!")
        else:
            # с помощью "магической" функции достаём числа из строки
            firstCoords = extractNumbers(firstCoords)
            secondCoords = extractNumbers(secondCoords)
            # создаём объект класса Circle с полученными ранее параметрами
            circle = Circle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1])
            # добавляем окружность на plane
            self.plane.add(circle)
            # очищаем поля ввода
            self.CenterCoordCircle.setPlainText("")
            self.SecondCoordCircle.setPlainText("")
        self.update()  # всё отрисовываем

    def addAngle(self):  # добавляем "луч" на plane
        # получаем координаты из соответствующих полей
        firstCoords = self.FirstCoordAngle.toPlainText()
        secondCoords = self.SecondCoordAngle.toPlainText()
        thirdCoords = self.ThirdCoordAngle.toPlainText()
        if firstCoords == "" or secondCoords == "" or thirdCoords == "":
            # если хотя бы одно из полей пустое, пытаемся взять точки из начала очереди
            try:
                firstCoords = self.plane.dots.popleft()
                secondCoords = self.plane.dots.popleft()
                thirdCoords = self.plane.dots.popleft()
                angle = WideAngle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1],
                                  thirdCoords[0], thirdCoords[1])
                self.plane.add(angle)
                self.WarningLabel.setText("")
            except:  # если в очереди недостаточно точек, выводим предупреждение
                self.WarningLabel.setText("Недостаточно\nточек!")
        else:
            # с помощью "магической" функции достаём числа из строки
            firstCoords = extractNumbers(firstCoords)
            secondCoords = extractNumbers(secondCoords)
            thirdCoords = extractNumbers(thirdCoords)
            # создаём объект класса WideAngle с полученными ранее параметрами
            angle = WideAngle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1],
                              thirdCoords[0], thirdCoords[1])
            # добавляем "луч" на plane
            self.plane.add(angle)
            # очищаем поля ввода
            self.FirstCoordAngle.setPlainText("")
            self.SecondCoordAngle.setPlainText("")
            self.ThirdCoordAngle.setPlainText("")
        self.update()  # всё отрисовываем

    def solveProblem(self):  # считаем наибольшую площадь
        area = self.plane.calculateCross()  # функция класса plane, которая ищет наибольшую площадь,
        # а сами фигуры записывает в plane.my_circle и plane.my_angle
        self.textBrowser.setText(str(area) if area != 0 else "")  # выводим значение площади
        self.update()  # всё отрисовываем

    def scalePlane(self, value):  # преобразует и передаёт значение ползунка внутренней переменной
        self.plane.scale = max(value // 5, 1)
        self.update()  # всё отрисовываем

    def rotatePlane(self, command):  # перемещение по полю
        const = 10 * self.plane.scale  # некоторая константа, на которую сдвигаемся
        # меняем положение в зависимости от команды
        if command == "left":
            self.plane.center = (self.plane.center[0] + const, self.plane.center[1])
        elif command == "right":
            self.plane.center = (self.plane.center[0] - const, self.plane.center[1])
        elif command == "up":
            self.plane.center = (self.plane.center[0], self.plane.center[1] + const)
        elif command == "down":
            self.plane.center = (self.plane.center[0], self.plane.center[1] - const)
        self.update()  # всё отрисовываем

    def drawShapes(self, painter):  # рисуем фигуры
        self.drawGrid(painter)  # рисуем сетку координат
        painter.setPen(QPen(Qt.black, 1))
        for a in self.plane.circles:
            self.drawCircle(painter, a)  # рисуем все окружности
        for a in self.plane.angles:
            self.drawAngle(painter, a)  # рисуем все "широкие" лучи
        # получаем пару с наибольшим пересечением
        my_circle, my_angle = self.plane.my_circle, self.plane.my_angle
        if my_circle is not None and my_angle is not None:  # если пара вообще есть
            # выделяем фигуры и закрашиваем пересечение
            self.drawCross(painter, my_circle, my_angle)
        self.drawDots(painter)  # рисуем все точки

    def drawGrid(self, painter):
        # рисует сетку координат
        c_x, c_y = self.plane.center
        painter.setPen(QPen(Qt.black, 2))  # выбираем цвет
        painter.drawLine(self.min_x, c_y, self.max_x, c_y)  # рисуем горизонтальную линию
        painter.drawLine(c_x, self.min_y, c_x, self.max_y)  # рисуем вертикальную линию
        # определяем точки для многоугольника "стрелочка"
        xArrow = [QPoint(self.max_x - 10, c_y - 5), QPoint(self.max_x - 1, c_y),
                  QPoint(self.max_x - 10, c_y + 5)]
        yArrow = [QPoint(c_x - 5, self.min_y + 10), QPoint(c_x, self.min_y + 1),
                  QPoint(c_x + 5, self.min_y + 10)]
        # рисуем стрелочки
        painter.drawPolygon(QPolygon(xArrow))
        painter.drawPolygon(QPolygon(yArrow))

    def drawAngle(self, painter, a):
        # рисует луч
        c_x, c_y = self.plane.center  # центр сетки координат
        s = self.plane.scale  # масштаб
        # вершины отрезков:
        x1, y1, x2, y2 = a.mainSegment[0] * s, -a.mainSegment[1] * s, a.mainSegment[2] * s, - \
            a.mainSegment[3] * s
        x4, y4, x5, y5 = a.firstSegment[2] * s, -a.firstSegment[3] * s, a.secondSegment[2] * s, - \
            a.secondSegment[3] * s
        # Знак Y меняется, т.к. система координат в окне
        # зеркально отражена привычной Декартовой системе.
        # рисуем отрезки по точкам
        painter.drawLine(x1 + c_x, y1 + c_y, x2 + c_x, y2 + c_y)
        painter.drawLine(x1 + c_x, y1 + c_y, x4 + c_x, y4 + c_y)
        painter.drawLine(x2 + c_x, y2 + c_y, x5 + c_x, y5 + c_y)

    def drawCircle(self, painter, a):
        # рисует окружность
        c_x, c_y = self.plane.center  # центр сетки координат
        s = self.plane.scale  # масштаб
        # определяем верхнюю левую вершину
        x, y = round(c_x + (a.center[0] - a.radius) * s), round(c_y - (a.center[1] + a.radius) * s)
        painter.drawEllipse(x, y, round(a.radius * s) * 2, round(a.radius * s) * 2)

    def drawDots(self, painter):
        # рисует точки
        painter.setPen(QPen(Qt.gray, 5))  # выбираем цвет
        c_x, c_y = self.plane.center  # центр сетки координат
        s = self.plane.scale  # масштаб
        for coord in self.plane.dots:
            painter.drawEllipse(c_x + coord[0] * s, c_y - coord[1] * s, 1, 1)

    def drawFrame(self, painter):
        # рисует рамку
        painter.setPen(QPen(Qt.black, 3))  # выбираем цвет
        # список точек
        frame = [QPoint(self.max_x, self.max_y), QPoint(self.max_x, self.min_y),
                 QPoint(self.min_x, self.min_y),
                 QPoint(self.min_x, self.max_y)]
        painter.drawPolygon(QPolygon(frame))  # рисуем прямоугольник

    def drawBoards(self, painter):
        # рисует белое поле вне координатной плоскости, чтобы убрать выходящие за границы элементы
        painter.setBrush(Qt.white)
        points = [QPoint(0, 0), QPoint(self.min_x - 2, 0), QPoint(self.min_x - 2, self.max_y + 2)]
        points += [QPoint(self.width(), self.max_y + 2), QPoint(self.width(), self.height())]
        points += [QPoint(0, self.height())]
        painter.drawPolygon(QPolygon(points))

    def drawCross(self, painter, circle, angle):
        # выделяет две фигуры и закрашивает их пересечение
        c_x, c_y = self.plane.center  # центр сетки координат
        s = self.plane.scale  # масштаб
        # вершины отрезков:
        x0, y0, r = circle.center[0] * s, circle.center[1] * s, round(circle.radius * s)
        x1, y1, x2, y2 = angle.mainSegment[0] * s, angle.mainSegment[1] * s, angle.mainSegment[
            2] * s, angle.mainSegment[3] * s
        x4, y4, x5, y5 = angle.firstSegment[2] * s, angle.firstSegment[3] * s, angle.secondSegment[
            2] * s, angle.secondSegment[3] * s
        # ищем точки многоугольника, который является пересечением с помощью соответствующих функций
        if angle.vertical:
            points = pointsVertical(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s,
                                    circle.radius)
        elif angle.horizontal:
            points = pointsHorizontal(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s,
                                      circle.radius)
        else:
            points = pointsElse(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s,
                                circle.radius, angle.pos)
        painter.setPen(QPen(QColor("#fc0fc0"), 1))  # выбираем цвет
        painter.drawPolygon(QPolygon(points))  # рисуем многоугольник
        painter.setPen(QPen(Qt.green, 3))  # выбираем цвет
        self.drawAngle(painter, angle)  # рисуем "широкий" угол
        self.drawCircle(painter, circle)  # рисуем окружность

    def clearPlane(self):  # очистка окна
        self.plane.clear()  # очистка plane
        self.textBrowser.setText("")  # очистка поля с ошибками
        self.update()  # всё отрисовываем


def pointsVertical(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s, radius):
    # получаем все точки многоугольника, если "луч" вертикальный
    points = list()  # список всех точек многоугольника
    k1, b1 = create_equation(x1, y1, x4, y4)
    k2, b2 = create_equation(x2, y2, x5, y5)
    for x in range(x0 - r, x0 + r - 1):  # перебираем все x лежащие в окружности
        # считаем дельта y от центра до точки лежащей на окружности
        dy = round(sqrt(abs((radius * s) ** 2 - (x - x0) ** 2)))
        for y in [y0 + dy, y0 - dy]:  # перебираем два возможных значения y
            if min(y1, y2) <= y <= max(y1, y2) and min(x1, x4) <= x <= max(x1, x4):
                # если точка лежит в "широком" луче мы просто её добавляем
                points.append(QPoint(x + c_x, -y + c_y))
        y, yo = y0 + dy, y0 - dy  # перебираем два возможных значения y
        if x == x1:  # если x совпадает с главным отрезком
            # перебираем все точки на главном отрезки и добавляем их в многоугольник
            for Y in range(max(min(y1, y2), yo), min(max(y1, y2), y)):
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x1, x4) <= x <= max(x1, x4):  # проверяем "первому" принадлежность отрезку по x
            Y = round(k1 * x + b1)  # высчитываем точку на "первом" отрезке для данного x
            if yo <= Y <= y:  # проверяем попала ли точка в окружность
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x2, x5) <= x <= max(x2, x5):  # проверяем принадлежность "второму" отрезку по x
            Y = round(k2 * x + b2)  # высчитываем точку на "втором" отрезке для данного x
            if yo <= Y <= y:  # проверяем попала ли точка в окружность
                points.append(QPoint(x + c_x, -Y + c_y))
    return points


def pointsHorizontal(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s, radius):
    # получаем все точки многоугольника, если "луч" горизонтальный
    points = list()  # список всех точек многоугольника
    m_k, m_b = create_equation(x1, y1, x2, y2)
    for x in range(x0 - r, x0 + r - 1):  # перебираем все x лежащие в окружности
        # считаем дельта y от центра до точки лежащей на окружности
        dy = round(sqrt(abs((radius * s) ** 2 - (x - x0) ** 2)))
        for y in [y0 + dy, y0 - dy]:  # перебираем два возможных значения y
            if min(x1, x2) <= x <= max(x1, x2) and min(y1, y4) <= y <= max(y1, y4):
                # если точка лежит в "широком" луче мы просто её добавляем
                points.append(QPoint(x + c_x, -y + c_y))
        y, yo = y0 + dy, y0 - dy  # перебираем два возможных значения y
        if min(x1, x2) <= x <= max(x1, x2):  # проверяем принадлежность главному отрезку по x
            Y = round(m_k * x + m_b)  # высчитываем точку на главном отрезке для данного x
            if yo <= Y <= y:  # проверяем попала ли точка в окружность
                points.append(QPoint(x + c_x, -Y + c_y))
        if x == x1:
            # перебираем все точки на "первом" отрезки и добавляем их в многоугольник
            for Y in range(max(min(y1, y4), yo), min(max(y1, y4), y)):
                points.append(QPoint(x + c_x, -Y + c_y))
        if x == x2:
            # перебираем все точки на "втором" отрезки и добавляем их в многоугольник
            for Y in range(max(min(y2, y5), yo), min(max(y2, y5), y)):
                points.append(QPoint(x + c_x, -Y + c_y))
    return points


def pointsElse(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s, radius, pos):
    # получаем все точки многоугольника, если "луч" не вертикальный и не горизонтальный
    points = list()  # список всех точек многоугольника
    m_k, m_b = create_equation(x1, y1, x2, y2)
    k1, b1 = create_equation(x1, y1, x4, y4)
    k2, b2 = create_equation(x2, y2, x5, y5)
    for x in range(x0 - r, x0 + r - 1):  # перебираем все x лежащие в окружности
        # считаем дельта y от центра до точки лежащей на окружности
        dy = round(sqrt(abs((radius * s) ** 2 - (x - x0) ** 2)))
        for y in [y0 + dy, y0 - dy]:  # перебираем два возможных значения y
            if check_pos(x1, y1, x2, y2, x, y) == pos and check_pos(
                    x1, y1, x4, y4, x, y) != check_pos(x2, y2, x5, y5, x, y):
                # если точка лежит в "широком" луче мы просто её добавляем
                points.append(QPoint(x + c_x, -y + c_y))
        y, yo = y0 + dy, y0 - dy  # перебираем два возможных значения y
        if min(x1, x2) <= x <= max(x1, x2):  # проверяем принадлежность главному отрезку по x
            Y = round(m_k * x + m_b)  # высчитываем точку на главном отрезке для данного x
            if yo <= Y <= y:  # проверяем попала ли точка в окружность
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x1, x4) <= x <= max(x1, x4):  # проверяем принадлежность "первому" отрезку по x
            Y = round(k1 * x + b1)  # высчитываем точку на "первом" отрезке для данного x
            if yo <= Y <= y:  # проверяем попала ли точка в окружность
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x2, x5) <= x <= max(x2, x5):  # проверяем принадлежность "второму" отрезку по x
            Y = round(k2 * x + b2)  # высчитываем точку на "первом" отрезке для данного x
            if yo <= Y <= y:  # проверяем попала ли точка в окружность
                points.append(QPoint(x + c_x, -Y + c_y))
    return points


# фишка питона, чтобы запускался только этот файл
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GeometryWidget()
    ex.show()
    sys.exit(app.exec_())
