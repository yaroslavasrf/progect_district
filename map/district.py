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
        """
        Инициализирует объект District. Загружает пользовательский интерфейс
        и настраивает обработчики событий для взаимодействия с элементами
        управления.
        """
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
        """
        Создает и отображает диалоговое окно с избранными местами

        Returns
        -------
        None
        """
        self.dialog = FavouriteListWindow()
        self.dialog.show()



    def link(self, url):
        """
        Открывает заданный URL в системном браузере.

        Parameters
        ----------
        url : str
              URL-адрес данного места

        Returns
        -------+
        None
        """
        url = QUrl(url)
        QDesktopServices.openUrl(url)

    def summarize(self):
        """
        Суммаризирует описание текущего места и обновляет
        соответствующий элемент интерфейса (QLabel с именем description)

        Returns
        -------
        None
        """
        text = self.description
        res = Llminference().post(text=text)
        self.widget.description.appendPlainText('СУММАРИЗИРОВАННЫЙ ТЕКСТ:' + str(res))

    def keyPressEvent(self, event):
        """
        Обрабатывает нажатия клавиш
        (при нажатии клавиши Enter запускается функция self.input_text())

        Parameters
        ----------
        event : QKeyEvent

        Returns
        -------
        None

        """
        if event.key() == Qt.Key.Key_Enter:
            self.input_text()




    def openWindow(self, item):
        """
        Открывает новое окно с информацией о выбранном элементе из списка.

        Parameters
        ----------
        item : QListWidgetItem

        Returns
        -------
        None
        """
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
        self.widget.description.appendPlainText(self.description)
        self.widget.adress.setText('Адрес: ' + self.adress)
        self.widget.link_button.clicked.connect(lambda: self.link(self.url))
        self.widget.summarization.clicked.connect(self.summarize)
        self.res_summarize = self.widget.description.toPlainText()
        self.widget.fav_button.clicked.connect(self.add_fav)
        self.widget.distance.setText(self.res_distance)

        self.widget.verticalSlider.setMinimum(2)
        self.widget.verticalSlider.setMaximum(21)
        self.widget.verticalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.widget.verticalSlider.setTickInterval(1)
        self.widget.verticalSlider.valueChanged.connect(self.display)

        self.widget.show()

    def display(self):
        """
            Изменяет размер карты в зависимости от значения слайдера.

            Returns
            -------
            None
            """
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

    def add_distance(self):
        """
            Вычисляет расстояние от текущих координат пользователя до заданного места.

            Returns
            -------
            str
                Строка с информацией о расстоянии до места
            """
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
        """
            Добавляет текущее место и информацию о нем в БД favourite_places_

            В случае успешного добавления места в избранное, кнопка
            интерфейса обновляется, чтобы показать, что место уже в избранном.

            Returns
            -------
            None
            """
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
        """
            Добавляет место в ListWidget на основе заданного местоположения.

            Returns
            ----------
            place : str
                Название места, информацию о котором необходимо получить.

            locate : int
                Координаты места в формате (широта, долгота). Если 0,
                координаты пользователя получаются автоматически с помощью функции self.locate_user(). По умолчанию 0.

            z int or None:
                Масштаб карты. По умолчанию None.

            Returns
            -------
            None
            """
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
        self.get_image_(locate=0, p=True, z=z)
        #print(self.places_for_listWidget)
        for index, elem in enumerate(self.places_for_listWidget[:], 1):
            self.listWidget.addItem(str(index) + ". " + elem["title"])

    def get_image_(self, locate=0, p=False, z=None):
        """
            Получает изображение по заданному местоположению и показывает его
            в виджете.

            Параметры
            ----------
            locate : int or tuple
                Координаты местоположения в формате (широта, долгота). Если
                0, координаты будут получены автоматически. По умолчанию 0.

            p : bool, optional
                Флаг, указывающий, следует ли использовать список координат
                из объектов places_for_listWidget для получения изображения.
                По умолчанию False.

            z : любой, optional
                Дополнительный параметр, который может использоваться в
                процессе получения изображения. По умолчанию None.

            Returns
            -------
            None
            """
        if locate == 0:
            locate = self.locate_user()
        if locate is None:
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error("coordinate error")
            self.geolocation_input.setText("Не удалось получить координаты")
            return
        if p:
            image = APIHandler.get_image(self, locate, point=(elem['coords'] for elem in self.places_for_listWidget), z=z)
        else:
            print(locate, z)
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
        """
            Получает текущие координаты пользователя.

            Returns
            -------
            coordinates : tuple of float or None
                Текущие координаты пользователя в формате (широта, долгота),
                если они были успешно получены. В противном случае возвращается
                None, и соответствующее сообщение выводится в текстовом поле.
            """
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
        """
        Метод сначала пытается получить координаты из текстового поля,
        разделяя их по запятой. Если это удается, вызываются методы
        для получения изображения и добавления места с указанными
        координатами. Если возникла ошибка (например, если ввод некорректен),
        метод попытается использовать сервис Nominatim для получения координат
        по текстовому описанию. Если и это не удастся, в журнал ошибок
        записывается соответствующее сообщение, и текстовое поле для изображения
        обновляется соответствующим сообщением об ошибке.

        Returns
        -------
        None
        """
        text = self.geolocation_input.text()
        try:
            text = [float(el) for el in text.split(',')]
            print(text)
            self.get_image_(locate=text, z=10)
            self.add_place(place='достопримечательность', locate=text, z=10)
        except:
            loc = Nominatim(user_agent="ya.sarafanova@gmail.com")
            getLoc = loc.geocode(text)
            try:
                text = [getLoc.latitude, getLoc.longitude]
                self.get_image_(locate=text, z=10)
                self.add_place(place='достопримечательность', locate=text, z=10)
            except:
                logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                    format="%(asctime)s %(levelname)s %(message)s")
                logging.error("image error")
                self.image.setText('Не удалось получить изображение')


    def get_current_gps_coordinates(self):
        """
        Получить текущие GPS-координаты устройства на основе IP-адреса.
        Этот метод использует библиотеку `geocoder` для определения
        геолокации по IP-адресу.

        Returns
        -------
        list of float or None
            Список с двумя элементами: [широта, долгота], если координаты
            были успешно получены; иначе возвращается None.
        """
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