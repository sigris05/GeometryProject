import sys
from math import sqrt

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import Qt, QPoint
from window import Ui_GeometryProblem

from PlaneClass import Plane, extractNumbers
from WideAngleClass import WideAngle, create_equation, check_pos
from CircleClass import Circle


class GeometryWidget(QMainWindow, Ui_GeometryProblem):
    def __init__(self):
        super().__init__()
        # uic.loadUi("window.ui", self)
        self.setupUi(self)
        self.max_x, self.max_y, self.min_x, self.min_y = 799, 449, 199, 1
        self.plane = Plane(500, 225)
        self.LeftBut.clicked.connect(lambda: self.rotatePlane("left"))
        self.RightBut.clicked.connect(lambda: self.rotatePlane("right"))
        self.DownBut.clicked.connect(lambda: self.rotatePlane("down"))
        self.UpBut.clicked.connect(lambda: self.rotatePlane("up"))
        self.ScaleSlider.valueChanged[int].connect(self.scalePlane)
        self.DrawBut.clicked.connect(self.update)
        self.LoadFileBut.clicked.connect(self.loadFromFile)
        self.ClearBut.clicked.connect(self.clearPlane)
        self.AddAngleBut.clicked.connect(self.addAdngle)
        self.AddCircleBut.clicked.connect(self.addCicle)
        self.CalculateBut.clicked.connect(self.solveProblem)

    def mousePressEvent(self, event):
        s = self.plane.scale
        coord = (event.x(), event.y())
        if self.min_x < coord[0] < self.max_x and self.min_y < coord[1] < self.max_y:
            coord = ((event.x() - self.plane.center[0] + s - 1) // s,
                     (-event.y() + self.plane.center[1]) // s)
            self.plane.add(coord)
            self.update()

    def keyPressEvent(self, event):
        if int(event.modifiers()) == Qt.ControlModifier:
            if event.key() == Qt.Key_Left:
                self.rotatePlane("left")
            if event.key() == Qt.Key_Right:
                self.rotatePlane("right")
            if event.key() == Qt.Key_Down:
                self.rotatePlane("down")
            if event.key() == Qt.Key_Up:
                self.rotatePlane("up")

    def addCicle(self):
        firstCoords = self.CenterCoordCircle.toPlainText()
        secondCoords = self.SecondCoordCircle.toPlainText()
        if firstCoords == "" or secondCoords == "":
            # считывание с мышки
            try:
                firstCoords = self.plane.dots.popleft()
                secondCoords = self.plane.dots.popleft()
                circle = Circle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1])
                self.plane.add(circle)
                self.WarningLabel.setText("")
            except:
                self.WarningLabel.setText("Недостаточно\nточек!")
        else:
            firstCoords = extractNumbers(firstCoords)
            secondCoords = extractNumbers(secondCoords)
            circle = Circle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1])
            self.plane.add(circle)
            self.CenterCoordCircle.setPlainText("")
            self.SecondCoordCircle.setPlainText("")
        self.update()

    def addAdngle(self):
        firstCoords = self.FirstCoordAngle.toPlainText()
        secondCoords = self.SecondCoordAngle.toPlainText()
        thirdCoords = self.ThirdCoordAngle.toPlainText()
        if firstCoords == "" or secondCoords == "" or thirdCoords == "":
            # считывание с мышки
            try:
                firstCoords = self.plane.dots.popleft()
                secondCoords = self.plane.dots.popleft()
                thirdCoords = self.plane.dots.popleft()
                angle = WideAngle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1],
                                  thirdCoords[0], thirdCoords[1])
                self.plane.add(angle)
                self.WarningLabel.setText("")
            except:
                self.WarningLabel.setText("Недостаточно\nточек!")
        else:
            firstCoords = extractNumbers(firstCoords)
            secondCoords = extractNumbers(secondCoords)
            thirdCoords = extractNumbers(thirdCoords)
            angle = WideAngle(firstCoords[0], firstCoords[1], secondCoords[0], secondCoords[1],
                              thirdCoords[0], thirdCoords[1])
            self.plane.add(angle)
            self.FirstCoordAngle.setPlainText("")
            self.SecondCoordAngle.setPlainText("")
            self.ThirdCoordAngle.setPlainText("")
        self.update()

    def clearPlane(self):
        self.plane.clear()
        self.textBrowser.setText("")
        self.update()

    def solveProblem(self):
        area = self.plane.calculateCross()
        self.textBrowser.setText(str(area) if area != 0 else "")
        self.update()

    def loadFromFile(self):
        try:
            fname = QFileDialog.getOpenFileName(self, "Выбрать файл с точками", "",
                                                "Текстовый файл (*.txt)")[0]
            self.plane.addFromFile(fname)
        except:
            self.WarningLabel.setText("Выбран\nнекорректный\nфайл!")
        self.update()

    def scalePlane(self, value):
        self.plane.scale = max(value // 5, 1)
        self.update()

    def rotatePlane(self, command):
        const = 10 * self.plane.scale
        if command == "left":
            self.plane.center = (self.plane.center[0] + const, self.plane.center[1])
        elif command == "right":
            self.plane.center = (self.plane.center[0] - const, self.plane.center[1])
        elif command == "up":
            self.plane.center = (self.plane.center[0], self.plane.center[1] + const)
        elif command == "down":
            self.plane.center = (self.plane.center[0], self.plane.center[1] - const)
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.drawShapes(painter)  # рисует все фигуры
        self.drawFrame(painter)  # рисует рамку координатной плоскости
        self.drawBoards(painter)  # закрашивает поле вне координатной плоскости
        painter.end()

    def drawShapes(self, painter):
        self.drawGrid(painter)  # рисует сетку координат
        painter.setPen(QPen(Qt.black, 1))
        for a in self.plane.circles:
            self.drawCircle(painter, a)  # рисует все окружности
        for a in self.plane.angles:
            self.drawAngle(painter, a)  # рисует все "широкие" углы
        my_circle, my_angle = self.plane.my_circle, self.plane.my_angle
        if my_circle is not None and my_angle is not None:
            self.drawCross(painter, my_circle, my_angle)
        self.drawDots(painter)

    def drawGrid(self, painter):
        # рисует сетку координат
        c_x, c_y = self.plane.center
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(self.min_x, c_y, self.max_x, c_y)
        painter.drawLine(c_x, self.min_y, c_x, self.max_y)
        # рисует стрелочки
        xArrow = [QPoint(self.max_x - 10, c_y - 5), QPoint(self.max_x - 1, c_y),
                  QPoint(self.max_x - 10, c_y + 5)]
        yArrow = [QPoint(c_x - 5, self.min_y + 10), QPoint(c_x, self.min_y + 1),
                  QPoint(c_x + 5, self.min_y + 10)]
        painter.drawPolygon(QPolygon(xArrow))
        painter.drawPolygon(QPolygon(yArrow))

    def drawAngle(self, painter, a):
        # рисует угол
        c_x, c_y = self.plane.center
        s = self.plane.scale
        x1, y1, x2, y2 = a.mainSegment[0] * s, -a.mainSegment[1] * s, a.mainSegment[2] * s, - \
            a.mainSegment[3] * s
        x4, y4, x5, y5 = a.firstSegment[2] * s, -a.firstSegment[3] * s, a.secondSegment[2] * s, - \
            a.secondSegment[3] * s
        # Знак Y меняется, т.к. система координат в окне
        # зеркально отражена привычной Декартовой системе.
        painter.drawLine(x1 + c_x, y1 + c_y, x2 + c_x, y2 + c_y)
        painter.drawLine(x1 + c_x, y1 + c_y, x4 + c_x, y4 + c_y)
        painter.drawLine(x2 + c_x, y2 + c_y, x5 + c_x, y5 + c_y)

    def drawCircle(self, painter, a):
        # рисует окружность
        c_x, c_y = self.plane.center
        s = self.plane.scale
        x, y = round(c_x + (a.center[0] - a.radius) * s), round(c_y - (a.center[1] + a.radius) * s)
        painter.drawEllipse(x, y, round(a.radius * s) * 2, round(a.radius * s) * 2)

    def drawDots(self, painter):
        # рисует точки
        painter.setPen(QPen(Qt.gray, 5))
        c_x, c_y = self.plane.center
        s = self.plane.scale
        for coord in self.plane.dots:
            painter.drawEllipse(c_x + coord[0] * s, c_y - coord[1] * s, 1, 1)

    def drawFrame(self, painter):
        # рисует рамку
        painter.setPen(QPen(Qt.black, 3))
        frame = [QPoint(self.max_x, self.max_y), QPoint(self.max_x, self.min_y),
                 QPoint(self.min_x, self.min_y),
                 QPoint(self.min_x, self.max_y)]
        painter.drawPolygon(QPolygon(frame))

    def drawBoards(self, painter):
        # рисует белое поле вне координатной плоскости, чтобы убрать выходящие за границы элементы
        painter.setBrush(Qt.white)
        points = [QPoint(0, 0), QPoint(self.min_x - 2, 0), QPoint(self.min_x - 2, self.max_y + 2)]
        points += [QPoint(self.width(), self.max_y + 2), QPoint(self.width(), self.height())]
        points += [QPoint(0, self.height())]
        painter.drawPolygon(QPolygon(points))

    def drawCross(self, painter, circle, angle):
        # выделяет две фигуры и закрашивает их пересечение
        c_x, c_y = self.plane.center
        s = self.plane.scale
        x0, y0, r = circle.center[0] * s, circle.center[1] * s, round(circle.radius * s)
        x1, y1, x2, y2 = angle.mainSegment[0] * s, angle.mainSegment[1] * s, angle.mainSegment[
            2] * s, angle.mainSegment[3] * s
        x4, y4, x5, y5 = angle.firstSegment[2] * s, angle.firstSegment[3] * s, angle.secondSegment[
            2] * s, angle.secondSegment[3] * s
        if angle.vertical:
            points = pointsVertical(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s,
                                    circle.radius)
        elif angle.horizontal:
            points = pointsHorizontal(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s,
                                      circle.radius)
        else:
            points = pointsElse(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s,
                                circle.radius, angle.pos)
        painter.setPen(QPen(QColor("#fc0fc0"), 1))
        painter.drawPolygon(QPolygon(points))
        painter.setPen(QPen(Qt.green, 3))
        self.drawAngle(painter, angle)
        self.drawCircle(painter, circle)


def pointsVertical(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s, radius):
    points = list()
    k1, b1 = create_equation(x1, y1, x4, y4)
    k2, b2 = create_equation(x2, y2, x5, y5)
    for x in range(x0 - r, x0 + r - 1):
        dy = round(sqrt(abs((radius * s) ** 2 - (x - x0) ** 2)))
        for y in [y0 + dy, y0 - dy]:
            if min(y1, y2) <= y <= max(y1, y2) and min(x1, x4) <= x <= max(x1, x4):
                points.append(QPoint(x + c_x, -y + c_y))
        y, yo = y0 + dy, y0 - dy
        if x == x1:
            for Y in range(max(min(y1, y2), yo), min(max(y1, y2), y)):
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x1, x4) <= x <= max(x1, x4):
            Y = round(k1 * x + b1)
            if yo <= Y <= y:
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x2, x5) <= x <= max(x2, x5):
            Y = round(k2 * x + b2)
            if yo <= Y <= y:
                points.append(QPoint(x + c_x, -Y + c_y))
    return points


def pointsHorizontal(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s, radius):
    points = list()
    m_k, m_b = create_equation(x1, y1, x2, y2)
    for x in range(x0 - r, x0 + r - 1):
        dy = round(sqrt(abs((radius * s) ** 2 - (x - x0) ** 2)))
        for y in [y0 + dy, y0 - dy]:
            if min(x1, x2) <= x <= max(x1, x2) and min(y1, y4) <= y <= max(y1, y4):
                points.append(QPoint(x + c_x, -y + c_y))
        y, yo = y0 + dy, y0 - dy
        if min(x1, x2) <= x <= max(x1, x2):
            Y = round(m_k * x + m_b)
            if yo <= Y <= y:
                points.append(QPoint(x + c_x, -Y + c_y))
        if x == x1:
            for Y in range(max(min(y1, y4), yo), min(max(y1, y4), y)):
                points.append(QPoint(x + c_x, -Y + c_y))
        if x == x2:
            for Y in range(max(min(y2, y5), yo), min(max(y2, y5), y)):
                points.append(QPoint(x + c_x, -Y + c_y))
    return points


def pointsElse(x0, y0, r, x1, y1, x2, y2, x4, y4, x5, y5, c_x, c_y, s, radius, pos):
    points = list()
    m_k, m_b = create_equation(x1, y1, x2, y2)
    k1, b1 = create_equation(x1, y1, x4, y4)
    k2, b2 = create_equation(x2, y2, x5, y5)
    for x in range(x0 - r, x0 + r - 1):
        dy = round(sqrt(abs((radius * s) ** 2 - (x - x0) ** 2)))
        for y in [y0 + dy, y0 - dy]:
            if check_pos(x1, y1, x2, y2, x, y) == pos and check_pos(
                    x1, y1, x4, y4, x, y) != check_pos(x2, y2, x5, y5, x, y):
                points.append(QPoint(x + c_x, -y + c_y))
        y, yo = y0 + dy, y0 - dy
        if min(x1, x2) <= x <= max(x1, x2):
            Y = round(m_k * x + m_b)
            if yo <= Y <= y:
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x1, x4) <= x <= max(x1, x4):
            Y = round(k1 * x + b1)
            if yo <= Y <= y:
                points.append(QPoint(x + c_x, -Y + c_y))
        if min(x2, x5) <= x <= max(x2, x5):
            Y = round(k2 * x + b2)
            if yo <= Y <= y:
                points.append(QPoint(x + c_x, -Y + c_y))
    return points


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GeometryWidget()
    ex.show()
    sys.exit(app.exec_())
