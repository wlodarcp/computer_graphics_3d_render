from math import cos, sin, pi
import numpy as np
from enum import Enum, auto
import pygame, sys
from pygame.locals import *
from pygame.gfxdraw import *
from matplotlib import colors


class WybranaMetoda(Enum):
    MIN_MAX = auto()
    NAKLADANIE_PUNKTOW = auto()


ZMIANA_OGNISKOWEJ = 0.1
KROK_PRZESUNIECIA = 1
WSPOLCZYNNIK_OBROTU = pi / 180.
OGNISKOWA = 1
WYSOKOSC_OKNA = 800
SZEROKOSC_OKNA = 1300
KROK_FILTRU_NA_OBRAZIE = 20
METODA = WybranaMetoda.MIN_MAX


class Kierunek(Enum):
    GORA = auto()
    DOL = auto()
    PRAWO = auto()
    LEWO = auto()
    PRZOD = auto()
    TYL = auto()
    BLIZEJ = auto()
    DALEJ = auto()
    PRZECIWNIE_DO_WSKAZOWEK = auto()
    ZGODNIE_ZE_WSKAZOWKAMI = auto()


pygame.init()
screen = pygame.display.set_mode([SZEROKOSC_OKNA, WYSOKOSC_OKNA])


def stworzDroge(poczatek, dlugosc, szerokosc):
    return [[poczatek + np.array([szerokosc, 0, 0]), poczatek, poczatek + np.array([0, dlugosc, 0]), poczatek + np.array([szerokosc, dlugosc, 0]), 'orange']]


def stworzProstopadloscian(poczatek, dlugosc, szerokosc, wysokosc, color):
    return [
        [poczatek + np.array([wysokosc, 0, 0]), poczatek, poczatek + np.array([0, szerokosc, 0]), poczatek + np.array([wysokosc, szerokosc, 0]), color],
        [poczatek + np.array([wysokosc, 0, dlugosc]), poczatek + np.array([0, 0, dlugosc]), poczatek + np.array([0, szerokosc, dlugosc]),
         poczatek + np.array([wysokosc, szerokosc, dlugosc]), color],
        [poczatek + np.array([wysokosc, 0, 0]), poczatek + np.array([wysokosc, 0, dlugosc]), poczatek + np.array([0, 0, dlugosc]), poczatek, color],
        [poczatek + np.array([wysokosc, 0, 0]), poczatek + np.array([wysokosc, szerokosc, 0]), poczatek + np.array([wysokosc, szerokosc, dlugosc]),
         poczatek + np.array([wysokosc, 0, dlugosc]), color],
        [poczatek + np.array([0, szerokosc, 0]), poczatek + np.array([0, szerokosc, dlugosc]), poczatek + np.array([0, 0, dlugosc]), poczatek, color],
        [poczatek + np.array([0, szerokosc, 0]), poczatek + np.array([0, szerokosc, dlugosc]), poczatek + np.array([wysokosc, szerokosc, dlugosc]),
         poczatek + np.array([wysokosc, szerokosc, 0]), color]
    ]


wektoryFigur = [
    [[300, 750, 0], [-300, 750, 0], [-300, 2500, 0], [300, 2500, 0], 'orange'],
    [[550., 1200., 0.], [400., 1200., 0.], [400., 2000., 0.], [550., 2000., 0.], 'green'],
    [[550., 1200., 400.], [400., 1200., 400.], [400., 2000., 400.], [550., 2000., 400.], 'green'],
    [[550., 1200., 0.], [550., 1200., 400.], [400., 1200., 400.], [400., 1200., 0.], 'green'],
    [[550., 1200., 0.], [550., 2000., 0.], [550., 2000., 400.], [550., 1200., 400.], 'green'],
    [[400., 2000., 0.], [400., 2000., 400.], [400., 1200., 400.], [400., 1200., 0.], 'green'],
    [[400., 2000., 0.], [400., 2000., 400.], [550., 2000., 400.], [550., 2000., 0.], 'green'],

    [[-550., 800., 0.], [-400., 800., 0.], [-400., 1500., 0.], [-550., 1500., 0.], 'red'],
    [[-550., 800., 200.], [-400., 800., 200.], [-400., 1500., 200.], [-550., 1500., 200.], 'red'],
    [[-550., 800., 0.], [-550., 1500., 0.], [-550., 1500., 200.], [-550., 800., 200.], 'red'],
    [[-400., 800., 0.], [-400., 1500., 0.], [-400., 1500., 200.], [-400., 800., 200.], 'red'],
    [[-550., 800., 0.], [-400., 800., 0.], [-400., 800., 200.], [-550., 800., 200.], 'red'],
    [[-550., 1500., 0.], [-400., 1500., 0.], [-400., 1500., 200.], [-550., 1500., 200.], 'red']
]


def inicjujObiekty():
    # droga = stworzDroge(np.array([-300., 750., 0.]), 7000., 600.)
    # prostopadloscian1 = stworzProstopadloscian(np.array([400., 1200., 0.]), 400., 800., 150., 'red')
    # prostopadloscian2 = stworzProstopadloscian(np.array([-400., 800., 0.]), 1000., 200., 150., 'blue')
    # return droga + prostopadloscian1 + prostopadloscian2
    return np.array(wektoryFigur)


def rzutujPunkt3Dna2D(punkt):
    polozenieKamery = [650., 500.]
    stosunek = OGNISKOWA / punkt[1] * 1000
    x = polozenieKamery[0] + stosunek * punkt[0]
    z = polozenieKamery[1] - stosunek * punkt[2]
    return [x, z, punkt[1]]


def czyCalyWektorJestWidoczny(punkt):
    return True


def rzutujObiektyDo2D():
    wektory2D = []
    for wektor in obiekty:
        wektor2d = []
        if czyCalyWektorJestWidoczny(wektor):
            wektor2d = [rzutujPunkt3Dna2D(wektor[0]), rzutujPunkt3Dna2D(wektor[1]), rzutujPunkt3Dna2D(wektor[2]), rzutujPunkt3Dna2D(wektor[3]), wektor[4], [0]]
        wektory2D.append(wektor2d)
    return wektory2D


def wypiszLegende():
    myfont = pygame.font.SysFont("monospace", 15)
    labels = []
    labels.append(myfont.render("← ↑  → ↓ - poruszanie po ekranie lewo/gora/prawo/doł", 1, (255, 255, 0)))
    labels.append(myfont.render("q/e - poruszanie przod/tył;", 1, (255, 255, 0)))
    labels.append(myfont.render("w/s/a/d - rozgladanie po ekranie;", 1, (255, 255, 0)))
    labels.append(myfont.render("z/x - obrot kamery;", 1, (255, 255, 0)))
    labels.append(myfont.render("kolko myszy - zoom", 1, (255, 255, 0)))
    counter = 0
    for label in labels:
        screen.blit(label, (50, 700 + counter))
        counter = counter + 20


def wypiszWybranaMetodeSortowania():
    myfont = pygame.font.SysFont("monospace", 15)
    screen.blit(myfont.render("Aktualna metoda: " + str(METODA.name), 15, (255, 255, 0)), (50, 50))
    screen.blit(myfont.render("Aby zmienić metode kliknij 'm'", 10, (255, 255, 0)), (50, 80))


def zoom(kierunek):
    wKtoraStrone = 1
    if kierunek == Kierunek.DALEJ:
        wKtoraStrone = -1
    global OGNISKOWA
    OGNISKOWA = OGNISKOWA + wKtoraStrone * ZMIANA_OGNISKOWEJ
    uaktualnijPlansze()


def przesunSieWWybranymKierunku(kierunek):
    (krok, wspKierunku) = (KROK_PRZESUNIECIA, 0)
    if kierunek == Kierunek.GORA or kierunek == Kierunek.DOL:
        wspKierunku = 2
    if kierunek == Kierunek.PRZOD or kierunek == Kierunek.TYL:
        wspKierunku = 1
    if kierunek == Kierunek.GORA or kierunek == Kierunek.PRAWO or kierunek == Kierunek.PRZOD:
        krok = (-1) * krok
    for wektor in obiekty:
        for i in range(0, 4):
            wektor[i][wspKierunku] += krok
            wektor[i][wspKierunku] += krok
    uaktualnijPlansze()


def rozgladajSieWWybranymKierunku(kierunek):
    (wsp_obrotu, wspDoEdycji1, wspDoEdycji2) = (WSPOLCZYNNIK_OBROTU, 1, 2)
    if kierunek == Kierunek.DOL or kierunek == Kierunek.PRAWO:
        wsp_obrotu = wsp_obrotu * (-1)
    if kierunek == Kierunek.PRAWO or kierunek == Kierunek.LEWO:
        (wspDoEdycji1, wspDoEdycji2) = (0, 1)
    for wektor in obiekty:
        for i in range(0, 4):
            wektor[i][wspDoEdycji1] = wektor[i][wspDoEdycji1] * cos((-1) * wsp_obrotu) - wektor[i][wspDoEdycji2] * sin((-1) * wsp_obrotu)
            wektor[i][wspDoEdycji2] = wektor[i][wspDoEdycji2] * cos((-1) * wsp_obrotu) + wektor[i][wspDoEdycji1] * sin((-1) * wsp_obrotu)
    uaktualnijPlansze()


def obrocJakWZegarze(kierunekObrotu):
    wsp_obrotu = WSPOLCZYNNIK_OBROTU
    if kierunekObrotu == Kierunek.PRZECIWNIE_DO_WSKAZOWEK:
        wsp_obrotu = wsp_obrotu * (-1)
    for wektor in obiekty:
        for i in range(0, 4):
            wektor[i][0] = wektor[i][0] * cos(wsp_obrotu) + wektor[i][2] * sin(wsp_obrotu)
            wektor[i][2] = (-1) * wektor[i][0] * sin(wsp_obrotu) + wektor[i][2] * cos(wsp_obrotu)
            wektor[i][0] = wektor[i][0] * cos(wsp_obrotu) + wektor[i][2] * sin(wsp_obrotu)
            wektor[i][2] = (-1) * wektor[i][0] * sin(wsp_obrotu) + wektor[i][2] * cos(wsp_obrotu)
    uaktualnijPlansze()


def czyPunktJestWFigurze(x, y, obszar):
    result = False
    j = 3
    i = 0
    while i < 4:
        if ((obszar[i][1] > y) != (obszar[j][1] > y)) and (x < (obszar[i][0] + (obszar[j][0] - obszar[i][0]) * (y - obszar[i][1]) / (obszar[j][1] - obszar[i][1]))):
            result = not result
        j = i
        i = i + 1
    return result


def znajdzRamkeOgraniczajacaWidocznoscObiektu(poly):
    extremes = [-999999., -9999999., 99999., 99999.]
    for i in range(0, 4):
        if poly[i][0] > extremes[0]:
            extremes[0] = poly[i][0]
        if poly[i][1] > extremes[1]:
            extremes[1] = poly[i][1]
        if poly[i][0] < extremes[2]:
            extremes[2] = poly[i][0]
        if poly[i][1] < extremes[3]:
            extremes[3] = poly[i][1]
    return [extremes[0] - 4, extremes[1] - 4, extremes[2] + 4, extremes[3] + 4]


def determinant(p):
    return p[0][0] * p[1][1] * p[2][2] + p[1][0] * p[2][1] * p[0][2] + p[2][0] * p[0][1] * p[1][2] - p[0][2] * p[1][1] * p[2][0] - p[1][2] * p[2][1] * p[0][0] - p[2][2] * \
           p[0][1] * p[1][0]


def determinant1(p):
    return p[1][1] * p[2][2] + p[2][1] * p[0][2] + p[0][1] * p[1][2] - p[0][2] * p[1][1] - p[1][2] * p[2][1] - p[2][2] * p[0][1]


def determinant2(p):
    return p[0][0] * p[2][2] + p[1][0] * p[0][2] + p[2][0] * p[1][2] - p[0][2] * p[2][0] - p[1][2] * p[0][0] - p[2][2] * p[1][0]


def determinant3(p):
    return p[0][0] * p[1][1] + p[1][0] * p[2][1] + p[2][0] * p[0][1] - p[1][1] * p[2][0] - p[2][1] * p[0][0] - p[0][1] * p[1][0]


def znajdzFunkcjeObiektu(obszar):
    W = determinant(obszar)
    ax = determinant1(obszar) / W
    ay = determinant2(obszar) / W
    az = determinant3(obszar) / W
    return ax, az, ay


def obliczZ(x, y, poly):
    wspolrzedneFunkcji = znajdzFunkcjeObiektu(poly)
    return (wspolrzedneFunkcji[0] * x + wspolrzedneFunkcji[2] * y - 1) / ((-1) * wspolrzedneFunkcji[1])


def sortujAnalizujacNakladaniePunktow(pierwszy, drugi):
    ekstrema = znajdzRamkeOgraniczajacaWidocznoscObiektu(pierwszy)
    i = ekstrema[2]
    while i <= ekstrema[0]:
        j = ekstrema[3]
        while j <= ekstrema[1]:
            if czyPunktJestWFigurze(i, j, pierwszy) and czyPunktJestWFigurze(i, j, drugi):
                z1 = obliczZ(i, j, pierwszy)
                z2 = obliczZ(i, j, drugi)
                if z1 > z2:
                    return -1
                else:
                    return 1
            j = j + KROK_FILTRU_NA_OBRAZIE
        i = i + KROK_FILTRU_NA_OBRAZIE
    return 0


def sortujMinMax(pierwszy, drugi):
    minPierwszego = min(pierwszy[0][2], pierwszy[1][2], pierwszy[2][2], pierwszy[3][2])
    minDrugiego = min(drugi[0][2], drugi[1][2], drugi[2][2], drugi[3][2])
    if minPierwszego < minDrugiego:
        return 1
    elif minPierwszego > minDrugiego:
        return -1
    else:
        return 0


def sortujWybranaMetodo(pierwszy, drugi):
    if METODA == WybranaMetoda.NAKLADANIE_PUNKTOW:
        return sortujAnalizujacNakladaniePunktow(pierwszy, drugi)
    elif METODA == WybranaMetoda.MIN_MAX:
        return sortujMinMax(pierwszy, drugi)


def rzutujOrazSortujObiekty():
    obiektyDoNarysowania = rzutujObiektyDo2D()
    i = 0
    while i < obiektyDoNarysowania.__len__():
        j = 0
        while j < obiektyDoNarysowania.__len__():
            if j is not i and sortujWybranaMetodo(obiektyDoNarysowania[i], obiektyDoNarysowania[j]) == 1:
                obiektyDoNarysowania[i][5].append(j)
            j = j + 1
        i = i + 1
    return obiektyDoNarysowania


def uaktualnijPlansze():
    obiektyDoNarysowania = rzutujOrazSortujObiekty()

    screen.fill((0, 0, 0))

    koniec = 0
    licznik = 0
    ileElementowZ1 = 0
    i = 0
    while i <= obiektyDoNarysowania.__len__():
        if i == obiektyDoNarysowania.__len__():
            i = 0
            koniec = 0
            licznik = licznik + 1
            if licznik == 10:
                licznik = 0
                ileElementowZ1 = ileElementowZ1 + 1
            if ileElementowZ1 == 6:
                break
        if obiektyDoNarysowania[i][5].__len__() == ileElementowZ1 and obiektyDoNarysowania[i][5].__len__() > 0:
            if obiektyDoNarysowania[i][5][0] != 'end':
                block = obiektyDoNarysowania[i]
                pygame.gfxdraw.filled_polygon(screen, [(block[0][0], block[0][1]), (block[1][0], block[1][1]), (block[2][0], block[2][1]), (block[3][0], block[3][1])],
                                              np.array(colors.to_rgb(block[4])) * 255)
                pygame.draw.line(screen, (220, 255, 30), (block[0][0], block[0][1]), (block[1][0], block[1][1]), 5)
                pygame.draw.line(screen, (220, 255, 30), (block[1][0], block[1][1]), (block[2][0], block[2][1]), 5)
                pygame.draw.line(screen, (220, 255, 30), (block[2][0], block[2][1]), (block[3][0], block[3][1]), 5)
                pygame.draw.line(screen, (220, 255, 30), (block[3][0], block[3][1]), (block[0][0], block[0][1]), 5)
                j = 0
                while j < obiektyDoNarysowania.__len__():
                    obiektyDoNarysowania[j][5] = list(filter(lambda val: val != i, obiektyDoNarysowania[j][5]))
                    j = j + 1
                obiektyDoNarysowania[i][5] = ['end']
        if obiektyDoNarysowania[i][5].__len__() > 0:
            if obiektyDoNarysowania[i][5][0] == 'end':
                koniec = koniec + koniec
        if koniec == obiektyDoNarysowania.__len__():
            break
        i = i + 1

    wypiszLegende()
    wypiszWybranaMetodeSortowania()
    pygame.display.flip()


def wyswietlaj():
    uaktualnijPlansze()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    global METODA
                    global KROK_PRZESUNIECIA
                    if METODA == WybranaMetoda.MIN_MAX:
                        METODA = WybranaMetoda.NAKLADANIE_PUNKTOW
                        KROK_PRZESUNIECIA = 10
                    elif METODA == WybranaMetoda.NAKLADANIE_PUNKTOW:
                        METODA = WybranaMetoda.MIN_MAX
                        KROK_PRZESUNIECIA = 1
                    uaktualnijPlansze()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom(Kierunek.BLIZEJ)
                elif event.button == 5:
                    zoom(Kierunek.DALEJ)
        if pygame.key.get_pressed()[pygame.K_w]:
            rozgladajSieWWybranymKierunku(Kierunek.GORA)
        elif pygame.key.get_pressed()[pygame.K_w]:
            rozgladajSieWWybranymKierunku(Kierunek.GORA)
        elif pygame.key.get_pressed()[pygame.K_s]:
            rozgladajSieWWybranymKierunku(Kierunek.DOL)
        elif pygame.key.get_pressed()[pygame.K_a]:
            rozgladajSieWWybranymKierunku(Kierunek.LEWO)
        elif pygame.key.get_pressed()[pygame.K_d]:
            rozgladajSieWWybranymKierunku(Kierunek.PRAWO)
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            przesunSieWWybranymKierunku(Kierunek.PRAWO)
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            przesunSieWWybranymKierunku(Kierunek.LEWO)
        elif pygame.key.get_pressed()[pygame.K_UP]:
            przesunSieWWybranymKierunku(Kierunek.GORA)
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            przesunSieWWybranymKierunku(Kierunek.DOL)
        elif pygame.key.get_pressed()[pygame.K_q]:
            przesunSieWWybranymKierunku(Kierunek.PRZOD)
        elif pygame.key.get_pressed()[pygame.K_e]:
            przesunSieWWybranymKierunku(Kierunek.TYL)
        elif pygame.key.get_pressed()[pygame.K_z]:
            obrocJakWZegarze(Kierunek.ZGODNIE_ZE_WSKAZOWKAMI)
        elif pygame.key.get_pressed()[pygame.K_x]:
            obrocJakWZegarze(Kierunek.PRZECIWNIE_DO_WSKAZOWEK)


if __name__ == "__main__":
    obiekty = inicjujObiekty()
    wyswietlaj()
