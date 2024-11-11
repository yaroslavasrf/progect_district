import sys
from secret import STATIC_API_KEY
import requests
import geocoder
import json
from apihandler import APIHandler

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6 import QtCore, QtWidgets, QtGui
from geopy.geocoders import Nominatim
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

class District(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("designs/design.ui", self)
        # get_info_from_request('парк', [55.769964061133756, 37.33026865917969])
        self.listWidget.itemClicked.connect(self.openWindow)

        #self.geo_button.setIcon(QtGui.QIcon('location.png'))
        #self.geo_button.setIconSize(QtCore.QSize(20, 20))
        self.geo_button.clicked.connect(self.get_image_)
        self.geo_button.clicked.connect(self.locate_user)

        #self.search_button.setIcon(QtGui.QIcon('search.png'))
        #self.search_button.setIconSize(QtCore.QSize(20, 20))

        self.library_button.clicked.connect(lambda: self.add_place('библиотека'))
        self.museum_button.clicked.connect(lambda: self.add_place('музей'))
        self.theatre_button.clicked.connect(lambda: self.add_place('театр'))
        self.park_button.clicked.connect(lambda: self.add_place('парк'))

        self.search_button.clicked.connect(self.input_text)

    def openWindow(self, item):
        # self.widget = QtWidgets()
        # row = self.listWidget.row(item)
        # self.widget.setWindowTitle(f'{row + 1}')
        # self.widget.resize(400, 100)
        # title = 'title'
        # coords = 'coords'
        # description = 'description'
        # url = 'url'
        print(self.places_for_listWidget)
        # text = (f'{self.places_for_listWidget[row][title]}\n{self.places_for_listWidget[row][coords]}\n{self.places_for_listWidget[row][description]}\n{self.places_for_listWidget[row][url]}')
        # self.widget.setText(text)
        # print(self.places_for_listWidget[row])
        # uic.loadUi("place.ui", self.widget)
        # self.widget.show()
        self.widget = QtWidgets.QWidget()
        row = self.listWidget.row(item)
        self.widget.setWindowTitle(f'{row}')
        uic.loadUi("designs/places.ui", self.widget)
        locate = self.places_for_listWidget[row]['coords']
        print(locate, type(locate))
        image = APIHandler.get_image(coord=[float(elem) for elem in locate.split(',')], point=(locate,), z=14, n=row)
        if image is None:
            print("Не удалось получить изображение")
            self.image.setText('Не удалось получить изображение')
            return

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(image))

        pic = self.widget.photo
        pic.setPixmap(pixmap)
        pic.show()
        self.widget.name.setText(self.places_for_listWidget[row]['title'])
        self.widget.coordinates.setText(self.places_for_listWidget[row]['coords'])
        #self.widget.adress.setText(self.places_for_listWidget[row]['coords'])
        self.widget.description.setText(self.places_for_listWidget[row]['description'])
        self.widget.adress.setText(self.places_for_listWidget[row]['address'])
        self.widget.link_button.clicked.connect(lambda: self.link(self.places_for_listWidget[row]['url']))
        self.widget.show()

    def link(self, url):
        url = QUrl(url)
        QDesktopServices.openUrl(url)


    def add_place(self, place, locate=0, z=None):
        self.listWidget.clear()
        if locate == 0:
            locate = self.locate_user()
        if locate is None:
            self.geolocation_input.setText("Не удалось получить координаты")
            return
        self.places_for_listWidget = APIHandler.get_info_from_request(place, locate)
        self.get_image_(locate=0, p=1, z=z)
        print(self.places_for_listWidget)
        for index, elem in enumerate(self.places_for_listWidget[:], 1):
            self.listWidget.addItem(str(index) + ". " + elem["title"])

    def get_image_(self, locate=0, p=0, z=None):
        if locate == 0:
            locate = self.locate_user()
        if locate is None:
            print("Не удалось получить координаты")
            self.geolocation_input.setText("Не удалось получить координаты")
            return
        if p == 1:
            image = APIHandler.get_image(locate, (elem['coords'] for elem in self.places_for_listWidget), z=z)
        else:
            image = APIHandler.get_image(locate, z=z)

        if image is None:
            print("Не удалось получить изображение")
            self.image.setText('Не удалось получить изображение')
            return

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(image))

        pic = self.image
        pic.setPixmap(pixmap)
        pic.show()

    def locate_user(self):
        coordinates = self.get_current_gps_coordinates()

        if not coordinates:
            self.geolocation_input.setText("Не удалось получить координаты")
            return

        self.geolocation_input.setText(",".join(map(str, coordinates)))
        return coordinates

    def input_text(self):
        text = self.geolocation_input.text()
        try:
            text = [float(el) for el in text.split(', ')]
            self.get_image_(locate=text, z=18)
            self.add_place('парк', locate=text)
        except:
            loc = Nominatim(user_agent="ya.sarafanova@gmail.com")
            getLoc = loc.geocode(text)
            try:
                locate = [getLoc.longitude, getLoc.latitude]
                self.get_image_(locate=locate, z=20)
                self.add_place('достопримечательность', locate=locate, z=15)
            except:
                self.image.setText('Не удалось получить изображение')

    def get_current_gps_coordinates(self):
        g = geocoder.ip('me')
        if g.latlng is not None:
            return g.latlng[::-1]
        return None


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    ex = District()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
