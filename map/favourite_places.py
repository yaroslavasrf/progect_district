from PyQt6 import uic
import sys
from PyQt6 import QtCore, QtWidgets
import sqlite3
from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog
flag = True


class FavouriteListWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("designs/favourites.ui", self)
        self.add_places()

        self.delete_all.clicked.connect(self.delete_all_places)
        self.fav_list.itemClicked.connect(self.openWindowDelete)
        self.fav_list.itemClicked.connect(self.num_func)
    def add_places(self):
        """
        Добавляет названия мест из БД в fav_list.

        Returns
        -------
        None
        """
        con = sqlite3.connect('favourite_places_.sqlite')
        cur = con.cursor()
        query = """SELECT title FROM places"""
        res = cur.execute(query).fetchall()
        con.close()
        res = [str(*elem) for elem in res]
        for elem in res[:]:
            self.fav_list.addItem(elem)

    def delete_all_places(self):
        """
        Удаляет все названия мест из fav_list

        Returns
        -------
        None
        """
        self.fav_list.clear()
        con = sqlite3.connect('favourite_places_.sqlite')
        cur = con.cursor()
        query = """DELETE FROM places WHERE id > 0"""
        res = cur.execute(query).fetchall()
        con.commit()
        con.close()
        global flag
        flag = False
    def openWindowDelete(self, clickedItem):
        self.widget = QtWidgets.QWidget()
        uic.loadUi("designs/delete.ui", self.widget)
        self.widget.yes_button.clicked.connect(self.del_object)
        self.widget.no_button.clicked.connect(self.close_window)
        self.del_text = clickedItem.text()
        self.widget.show()
    def num_func(self, item):
        self.row = self.fav_list.row(item)

    def del_object(self, item):
        con = sqlite3.connect('favourite_places_.sqlite')
        cur = con.cursor()
        query = """DELETE FROM places WHERE title = ?"""
        res = cur.execute(query, (self.del_text,))
        con.commit()
        con.close()
        self.fav_list.takeItem(self.row)
        self.widget.close()
        global flag
        flag = False

    def close_window(self):
        self.widget.close()