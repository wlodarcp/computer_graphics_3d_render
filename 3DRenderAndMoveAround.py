from math import cos, sin, pi
import numpy as np
from enum import Enum, auto
import pygame, sys
from pygame.locals import *

ZMIANA_OGNISKOWEJ = 0.1
KROK_PRZESUNIECIA = 1
WSPOLCZYNNIK_OBROTU = pi / 540.
OGNISKOWA = 1
WYSOKOSC_OKNA = 800
SZEROKOSC_OKNA = 1300


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
    ZGODNIE_ZE_WSKAZOWKAMI = ()


pygame.init()
screen = pygame.display.set_mode([SZEROKOSC_OKNA, WYSOKOSC_OKNA])


def stworzDroge(poczatek, dlugosc, szerokosc):
    return [
        [poczatek, poczatek + np.array([szerokosc, 0, 0])],
        [poczatek, poczatek + np.array([0, dlugosc, 0])],
        [poczatek + np.array([0, dlugosc, 0]), poczatek + np.array([szerokosc, dlugosc, 0])],
        [poczatek + np.array([szerokosc, 0, 0]), poczatek + np.array([szerokosc, dlugosc, 0])]
    ]


def stworzProstopadloscian(poczatek, dlugosc, szerokosc, wysokosc):
    return [
        [poczatek, poczatek + np.array([wysokosc, 0, 0])],
        [poczatek, poczatek + np.array([0, szerokosc, 0])],
        [poczatek + np.array([0, szerokosc, 0]), poczatek + np.array([wysokosc, szerokosc, 0])],
        [poczatek + np.array([wysokosc, szerokosc, 0]), poczatek + np.array([wysokosc, 0, 0])],

        [poczatek + np.array([0, 0, dlugosc]), poczatek + np.array([wysokosc, 0, dlugosc])],
        [poczatek + np.array([0, 0, dlugosc]), poczatek + np.array([0, szerokosc, dlugosc])],
        [poczatek + np.array([0, szerokosc, dlugosc]), poczatek + np.array([wysokosc, szerokosc, dlugosc])],
        [poczatek + np.array([wysokosc, szerokosc, dlugosc]), poczatek + np.array([wysokosc, 0, dlugosc])],

        [poczatek, poczatek + np.array([0, 0, dlugosc])],
        [poczatek + np.array([wysokosc, 0, dlugosc]), poczatek + np.array([wysokosc, 0, 0])],

        [poczatek + np.array([0, szerokosc, 0]), poczatek + np.array([0, szerokosc, dlugosc])],
        [poczatek + np.array([wysokosc, szerokosc, 0]), poczatek + np.array([wysokosc, szerokosc, dlugosc])]
    ]


def inicjujObiekty():
    droga = stworzDroge(np.array([-300., 750., 0.]), 7000., 600.)
    prostopadloscian1 = stworzProstopadloscian(np.array([400., 1200., 0.]), 400., 1000., 150.)
    prostopadloscian2 = stworzProstopadloscian(np.array([-750., 1650., 0.]), 1000., 200., 300.)
    prostopadloscian3 = stworzProstopadloscian(np.array([-750., 3000., 0.]), 1000., 1000., 300.)
    prostopadloscian4 = stworzProstopadloscian(np.array([600., 2000., 0.]), 600., 3000., 600.)
    return droga + prostopadloscian1 + prostopadloscian2 + prostopadloscian3 + prostopadloscian4


def rzutujPunkt3Dna2D(punkt):
    polozenieKamery = [650, 500]
    stosunek = OGNISKOWA / punkt[1] * 1000
    x = polozenieKamery[0] + stosunek * punkt[0]
    z = polozenieKamery[1] - stosunek * punkt[2]
    return [x, z]


def czyCalyWektorJestWidoczny(punkt):
    return punkt[0][1] >= OGNISKOWA and punkt[1][1] >= OGNISKOWA


def rzutujObiektyDo2D():
    wektory2D = []
    for wektor in obiekty:
        if czyCalyWektorJestWidoczny(wektor):
            wektory2D.append([rzutujPunkt3Dna2D(wektor[0]), rzutujPunkt3Dna2D(wektor[1])])
    return wektory2D


def rysujLinie(wektor):
    pygame.draw.line(screen, (255, 0, 0), (wektor[0][0], wektor[0][1]), (wektor[1][0], wektor[1][1]))


def rysujLegende():
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


def uaktualnijPlansze():
    screen.fill((0, 0, 0))
    obiektyDoNarysowania = rzutujObiektyDo2D()
    for wektor in obiektyDoNarysowania:
        rysujLinie(wektor)
    rysujLegende()
    pygame.display.flip()


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
        wektor[0][wspKierunku] += krok
        wektor[1][wspKierunku] += krok
    uaktualnijPlansze()


def rozgladajSieWWybranymKierunku(kierunek):
    (wsp_obrotu, wspDoEdycji1, wspDoEdycji2) = (WSPOLCZYNNIK_OBROTU, 1, 2)
    if kierunek == Kierunek.DOL or kierunek == Kierunek.PRAWO:
        wsp_obrotu = wsp_obrotu * (-1)
    if kierunek == Kierunek.PRAWO or kierunek == Kierunek.LEWO:
        (wspDoEdycji1, wspDoEdycji2) = (0, 1)
    for wektor in obiekty:
        wektor[0][wspDoEdycji1] = wektor[0][wspDoEdycji1] * cos((-1) * wsp_obrotu) - wektor[0][wspDoEdycji2] * sin((-1) * wsp_obrotu)
        wektor[0][wspDoEdycji2] = wektor[0][wspDoEdycji2] * cos((-1) * wsp_obrotu) + wektor[0][wspDoEdycji1] * sin((-1) * wsp_obrotu)
        wektor[1][wspDoEdycji1] = wektor[1][wspDoEdycji1] * cos((-1) * wsp_obrotu) - wektor[1][wspDoEdycji2] * sin((-1) * wsp_obrotu)
        wektor[1][wspDoEdycji2] = wektor[1][wspDoEdycji2] * cos((-1) * wsp_obrotu) + wektor[1][wspDoEdycji1] * sin((-1) * wsp_obrotu)
    uaktualnijPlansze()


def obrocJakWZegarze(kierunekObrotu):
    wsp_obrotu = WSPOLCZYNNIK_OBROTU
    if kierunekObrotu == Kierunek.PRZECIWNIE_DO_WSKAZOWEK:
        wsp_obrotu = wsp_obrotu * (-1)
    for wektor in obiekty:
        wektor[0][0] = wektor[0][0] * cos(wsp_obrotu) + wektor[0][2] * sin(wsp_obrotu)
        wektor[0][2] = (-1) * wektor[0][0] * sin(wsp_obrotu) + wektor[0][2] * cos(wsp_obrotu)
        wektor[1][0] = wektor[1][0] * cos(wsp_obrotu) + wektor[1][2] * sin(wsp_obrotu)
        wektor[1][2] = (-1) * wektor[1][0] * sin(wsp_obrotu) + wektor[1][2] * cos(wsp_obrotu)
    uaktualnijPlansze()


def wyswietlaj():
    uaktualnijPlansze()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
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


obiekty = np.array(inicjujObiekty())
wyswietlaj()
