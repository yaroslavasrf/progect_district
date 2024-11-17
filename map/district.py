import sys
import geocoder
import logging
import sqlite3
from apihandler import APIHandler
from llminference import Llminference
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QSlider, QApplication
from PyQt6 import QtCore, QtWidgets, QtGui
from geopy.geocoders import Nominatim
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from math import sin, cos, sqrt, atan2, radians
from favourite_places import FavouriteListWindow

class District(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("designs/design.ui", self)
        APIHandler.__init__(self, "District")
        self.listWidget.itemClicked.connect(self.openWindow)

        self.geo_button.setIcon(QtGui.QIcon('pic/location.png'))
        self.geo_button.setIconSize(QtCore.QSize(30, 30))
        self.geo_button.clicked.connect(lambda: self.get_image_(z=13))
        self.geo_button.clicked.connect(lambda: self.add_place(place='достопримечательность'))

        self.search_button.setIcon(QtGui.QIcon('pic/search.png'))
        self.search_button.setIconSize(QtCore.QSize(30, 30))
        self.search_button.clicked.connect(self.input_text)

        self.library_button.clicked.connect(lambda: self.add_place('библиотека'))
        self.museum_button.clicked.connect(lambda: self.add_place('музей'))
        self.theatre_button.clicked.connect(lambda: self.add_place('театр'))
        self.park_button.clicked.connect(lambda: self.add_place('парк'))

        self.favourites.clicked.connect(self.click_fav)

        self.flag_fav_button = False

    def click_fav(self):
        self.dialog = FavouriteListWindow()
        self.dialog.show()


    def link(self, url):
        url = QUrl(url)
        QDesktopServices.openUrl(url)

    def summarize(self):
        text = self.description
        res = Llminference().post(text=text)
        self.widget.description.setText(str(res))
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter:
            self.input_text()



    def openWindow(self, item):
        self.widget = QtWidgets.QWidget()
        self.row = self.listWidget.row(item)
        self.widget.setWindowTitle(f'{self.row}')
        uic.loadUi("designs/places.ui", self.widget)
        self.locate = self.places_for_listWidget[self.row]['coords']
        image = APIHandler.get_image(self, coord=[float(elem) for elem in self.locate.split(',')], point=(self.locate,), z=14,
                                     n=self.row)
        if image is None:
            self.image.setText('Не удалось получить изображение')
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error("image error")
            return

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(image))

        pic = self.widget.photo
        pic.setPixmap(pixmap)
        pic.show()
        if self.flag_fav_button == True:
            self.widget.fav_button.setText('Это место уже в избранном')
        self.description = self.places_for_listWidget[self.row]['description']
        self.title = self.places_for_listWidget[self.row]['title']
        self.coord = [round(float(elem), 2) for elem in self.places_for_listWidget[self.row]['coords'].split(',')]
        self.adress = self.places_for_listWidget[self.row]['address']
        self.url = self.places_for_listWidget[self.row]['url']
        self.res_distance = self.add_distance()

        self.widget.name.setText(self.title)
        self.widget.coordinates.setText('Координаты: ' + str(self.coord[0]) + ', ' + str(self.coord[1]))
        self.widget.description.setText(self.description)
        self.widget.adress.setText('Адрес: ' + self.adress)
        self.widget.link_button.clicked.connect(lambda: self.link(self.url))
        self.widget.summarization.clicked.connect(self.summarize)
        self.res_summarize = self.widget.description.text()
        self.widget.fav_button.clicked.connect(self.add_fav)
        self.widget.distance.setText(self.res_distance)

        self.widget.verticalSlider.setMinimum(2)
        self.widget.verticalSlider.setMaximum(21)
        self.widget.verticalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.widget.verticalSlider.setTickInterval(1)
        self.widget.verticalSlider.valueChanged.connect(self.display)

        self.widget.show()

    def display(self):
        value = self.sender().value()
        self.widget.slider_label.setText(str(value))
        image = APIHandler.get_image(self, coord=[float(elem) for elem in self.locate.split(',')], point=(self.locate,),
                                     z=value, n=self.row)
        if image is None:
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error("image error")
            self.image.setText('Не удалось получить изображение')
            return

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(image))

        pic = self.widget.photo
        pic.setPixmap(pixmap)
        pic.show()


    def link(self, url):
        url = QUrl(url)
        QDesktopServices.openUrl(url)

    def summarize(self):
        text = self.description
        res = Llminference().post(text=text)
        self.widget.description.setText(str(res))

    def add_distance(self):
        R = 6373
        user_coord = self.get_current_gps_coordinates()
        user_longitude = radians(user_coord[0])
        user_width = radians(user_coord[1])
        place_longitude = radians(int(self.coord[0]))
        place_width = radians(int(self.coord[1]))
        d_width = user_width - place_width
        d_longitude = user_longitude - place_longitude
        a = sin(d_longitude / 2) ** 2 + cos (user_longitude) * cos(place_longitude) * sin(d_width / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        result = f'Это место в {str(round(distance))[0]}км от вас'
        return result


    def add_fav(self):
        self.place_inf = {'Название': self.title, 'Описание': self.description, 'Адрес': self.adress,
                          'Координаты': str(self.coord[0]) + ', ' + str(self.coord[1]), 'Ссылка': self.url,
                          'Расстояние': self.res_distance, 'Суммаризация': self.res_summarize}
        try:
            con = sqlite3.connect('favourite_places_.sqlite')
            cur = con.cursor()
            query = """INSERT INTO places(title, description, adress, coord, url, distance, summarize) VALUES(?, ?, ?, ?, ?, ?, ?)"""
            cur.execute(query, (self.title, self.description, self.adress, str(self.coord[0]) + ', ' + str(self.coord[1]),
                                self.url, self.res_distance, self.res_summarize))
            con.commit()
            con.close()
            self.widget.fav_button.setText('Это место уже в избранном')
            self.flag_fav_button = True
        except:
            self.widget.fav_button.setText('Это место уже в избранном')
            self.flag_fav_button = True
        for key, value in self.place_inf.items():
            print(f'{key}: {value}')

    def add_place(self, place, locate=0, z=None):
        self.listWidget.clear()
        if locate == 0:
            locate = self.locate_user()
        if locate is None:
            self.geolocation_input.setText("Не удалось получить координаты")
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error("coordinate error")
            return
        self.places_for_listWidget = APIHandler.get_info_from_request(self, place, locate)
        self.get_image_(locate=0, p=1, z=z)
        #print(self.places_for_listWidget)
        for index, elem in enumerate(self.places_for_listWidget[:], 1):
            self.listWidget.addItem(str(index) + ". " + elem["title"])

    def get_image_(self, locate=0, p=0, z=None):
        if locate == 0:
            locate = self.locate_user()
        if locate is None:
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error("coordinate error")
            self.geolocation_input.setText("Не удалось получить координаты")
            return
        if p == 1:
            image = APIHandler.get_image(self, locate, (elem['coords'] for elem in self.places_for_listWidget), z=z)
        else:
            image = APIHandler.get_image(self, locate, z=z)

        if image is None:
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error("image error")
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
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error("image error")
            self.geolocation_input.setText("Не удалось получить изображение")
            return

        self.geolocation_input.setText(",".join(map(str, coordinates)))
        return coordinates

    def input_text(self):
        text = self.geolocation_input.text()
        try:
            text = [float(el) for el in text.split(',')]
            self.get_image_(locate=text, z=15)
            self.add_place(place='достопримечательность', locate=text, z=15)
        except:
            loc = Nominatim(user_agent="ya.sarafanova@gmail.com")
            getLoc = loc.geocode(text)
            try:
                locate = [getLoc.latitude, getLoc.longitude]
                self.add_place('парк', locate=locate, z=10)
                self.get_image_(locate=locate, p=1, z=5)
            except:
                logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                    format="%(asctime)s %(levelname)s %(message)s")
                logging.error("image error")
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