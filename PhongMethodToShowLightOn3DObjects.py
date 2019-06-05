from math import pow, sqrt
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from aenum import MultiValueEnum

WIDTH = 400
HEIGHT = 400

obiekty = [[], [], [], []]
ip = 1.0
ia = 0.1
positionLX = 100
positionLY = 50
ka = [0.45, 0.8, 0.5, 0.1]
kd = [0.9, 0.9, 0.6, 0.6]
ks = [0.2, 0.01, 0.4, 0.4]
m = [50, 25, 10, 150]
xL = 400
yL = 500
zL = -1600.0
odlegloscOdRzutni = 150
slidersStarting = [xL / 10, yL / 10, (zL + 200) / 24, (100 / 1.4) * (ip - 0.1), (positionLY + 100) / 11, (positionLY + 100) / 11, (100 / 2.6) * (ia + 1.7)]
currentGuiState = [[0] * WIDTH for i in range(HEIGHT)]

app = QApplication(sys.argv)
widget = QWidget()
label = QLabel()
combobox = QComboBox()

class Sliders(QWidget):
    def __init__(self, parent=None):
        super(Sliders, self).__init__(parent)

        grid = QGridLayout()
        grid.addWidget(self.createExampleGroup('Kierunek X źródła światła', changeXL, start=slidersStarting[0]), 0, 0)
        #grid.addWidget(self.createExampleGroup('Kierunek Y źródła światła', changeYL, start=slidersStarting[1]), 1, 0)
        #grid.addWidget(self.createExampleGroup('Kierunek Z źródła światła', changeZL, start=slidersStarting[2]), 2, 0)
        grid.addWidget(self.createExampleGroup('Położenie Y źródła światła', changePLY, start=slidersStarting[4]), 2, 0)
        grid.addWidget(self.createExampleGroup('Położenie X źródła światła', changePLX, start=slidersStarting[5]), 2, 1)
        grid.addWidget(self.createExampleGroup('Natężenie światła punktowego', changeIP, start=slidersStarting[3]), 0, 1)
        grid.addWidget(self.createExampleGroup('Natężenie światła otoczenia', changeIA, start=slidersStarting[6]), 1, 1)
        grid.addWidget(self.createComobox(), 3, 0)
        self.setLayout(grid)
        self.resize(400, 300)

    def getSlider(self, min, max, step, onChange, startingPosition):
        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setSingleStep(step)
        slider.setSliderPosition(startingPosition)
        slider.sliderReleased.connect(lambda: onChange(slider.value()))
        return slider

    def createExampleGroup(self, name, onChange, min=0, max=100, step=1, start=0.):
        groupBox = QGroupBox(name)
        vbox = QVBoxLayout()
        vbox.addWidget(self.getSlider(min, max, step, onChange, startingPosition=int(start)))
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        return groupBox

    def createComobox(self):
        combobox.addItems(["Plastik", "Drewno", "Kreda", "Metal"])
        combobox.currentTextChanged.connect(lambda: changeMaterial(combobox.currentIndex()))
        return combobox


def updatePixel(x, y, r, g, b, a):
    currentGuiState[x][y] = [r, g, b, a]


def sprawdzPunktCzyWPolsfera(x, y):
    a = 1
    b = -2 * odlegloscOdRzutni
    c = pow(x, 2) + pow(y, 2) + pow(odlegloscOdRzutni, 2) - pow(150, 2)
    delta = pow(b, 2) - 4 * a * c
    return delta >= 0


def producePixels(obiekt, material=0):
    for x in range(WIDTH):
        for y in range(HEIGHT):
            fong = ip * bphong([positionLX, positionLY, -obiekt[x][y][0]],
                               [xL - x, yL - y, zL - obiekt[x][y][0]],
                               normalny(x, y, obiekt[x][y][0]),
                               [x, y, obiekt[x][y][0]],
                               m[material],
                               ip,
                               kd[material],
                               ks[material])
            a = ia * ka[material]
            if fong is None:
                fong = 0
            res = fong + a
            colors = getColor(res)
            updatePixel(x, y, colors[0], colors[1], colors[2], 255)


def initPhong():
    for x in range(WIDTH):
        obiekty[0].append([])
        for y in range(HEIGHT):
            if sprawdzPunktCzyWPolsfera(x - WIDTH / 2, y - HEIGHT / 2):
                a = 1
                b = -2 * odlegloscOdRzutni
                c = pow((x - WIDTH / 2), 2) + pow((y - HEIGHT / 2), 2) + pow(odlegloscOdRzutni, 2) - pow(150, 2)
                delta = pow(b, 2) - 4 * a * c
                obiekty[0][x].append([((-b - sqrt(delta)) / 2 * a), 240, 240, 240])
            else:
                obiekty[0][x].append([120, 240, 240, 240])

    producePixels(obiekty[0])


def updatePixels(obiekt, material=0):
    producePixels(obiekt, material)
    update()


def getColor(p):
    v = (255 * p)
    if v < 0:
        v = 0
    elif v > 255:
        v = 255
    return [v, v, v]


def normalny(x, y, z):
    return [x, y, z - odlegloscOdRzutni]


def bphong(wektorV, wektorL, wektorN, wektorP, m, ip, kd, ks):
    kDoNormalizacjiV = 1 / dlugosc(wektorV)
    kDoNormalizacjiL = 1 / dlugosc(wektorL)
    kDoNormalizacjiN = 1 / dlugosc(wektorN)
    wektorV = [wektorV[0] * kDoNormalizacjiV, wektorV[1] * kDoNormalizacjiV, wektorV[2] * kDoNormalizacjiV]
    wektorL = [wektorL[0] * kDoNormalizacjiL, wektorL[1] * kDoNormalizacjiL, wektorL[2] * kDoNormalizacjiL]
    wektorN = [wektorN[0] * kDoNormalizacjiN, wektorN[1] * kDoNormalizacjiN, wektorN[2] * kDoNormalizacjiN]
    wektorH = obliczH(wektorV, wektorL)
    kDoNormalizacjiH = 1 / dlugosc(wektorH)
    wektorH = [wektorH[0] * kDoNormalizacjiH, wektorH[1] * kDoNormalizacjiH, wektorH[2] * kDoNormalizacjiH]
    NdotL = saturate(scalar(wektorN, wektorL))
    NdotH = saturate(scalar(wektorN, wektorH))
    wynik = kd * NdotL * ip + ks * pow(NdotH, m) * ip
    return saturate(wynik)


def dlugosc(wektor):
    return sqrt(wektor[0] * wektor[0] + wektor[1] * wektor[1] + wektor[2] * wektor[2])


def obliczH(naKtorym, zKtorym):
    k = dlugosc(zKtorym) / dlugosc(naKtorym)
    temp = [naKtorym[0] * k, naKtorym[1] * k, naKtorym[2] * k]
    x = [zKtorym[0] - temp[0], zKtorym[1] - temp[1], zKtorym[2] - temp[2]]
    return [temp[0] + x[0] / 2, temp[1] + x[1] / 2, temp[2] + x[2] / 2]


def saturate(x):
    if x < 0:
        return 0
    if x > 1:
        return 1
    return x


def scalar(naKtorym, zKtorym):
    return naKtorym[0] * zKtorym[0] + naKtorym[1] * zKtorym[1] + naKtorym[2] * zKtorym[2]


def changeXL(x):
    global xL
    xL = x * 10
    print('new x: ' + str(xL))
    updatePixels(obiekty[0])


def changeYL(y):
    global yL
    yL = y * 10
    print('new y: ' + str(yL))
    updatePixels(obiekty[0])


def changeZL(z):
    global zL
    zL = -2000 + (z / 100) * 2400
    print('new z: ' + str(zL))
    updatePixels(obiekty[0])


def changeIP(newIp):
    global ip
    ip = 0.1 + (newIp / 100) * 1.4
    print('new ip: ' + str(ip))
    updatePixels(obiekty[0])


def changeIA(newIa):
    global ia
    ia = -1.7 + (newIa / 100) * 2.6
    print('new ia: ' + str(ia))
    updatePixels(obiekty[0])


def changePLX(newplx):
    global positionLX
    positionLX = -100 + (newplx / 100) * 1100
    print('new PLX: ' + str(positionLX))
    updatePixels(obiekty[0])


def changePLY(newply):
    global positionLY
    positionLY = -100 + (newply / 100) * 1100
    print('new PLY: ' + str(positionLY))
    updatePixels(obiekty[0])


def changeMaterial(material):
    updatePixels(obiekty[0], material)


def getCurrentPixelMap():
    img = QImage(WIDTH, HEIGHT, QImage.Format_RGB32)
    img.fill(Qt.white)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            pixel = currentGuiState[x][y]
            img.setPixel(x, y, QColor(pixel[0], pixel[1], pixel[2], pixel[3]).rgba())
    return QPixmap(img)


def update():
    label.setPixmap(getCurrentPixelMap())
    label.setGeometry(5, 5, WIDTH, HEIGHT)
    label.repaint()


if __name__ == '__main__':
    initPhong()
    label.setPixmap(getCurrentPixelMap())
    label.setGeometry(5, 5, WIDTH, HEIGHT)
    layout = QHBoxLayout()
    layout.addWidget(label)
    layout.addWidget(Sliders())
    widget.setLayout(layout)
    widget.setWindowTitle('Phong')
    widget.show()
    app.exec_()
