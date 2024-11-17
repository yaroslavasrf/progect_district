from PyQt6 import uic
import sys
from PyQt6 import QtCore, QtWidgets
import sqlite3
from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog


class FavouriteListWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("designs/favourites.ui", self)
        self.add_places()

        self.delete_all.clicked.connect(self.delete_all_places)
    def add_places(self):
        """
        Добавляет названия мест из БД в ListWidget с названием fav_list.

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
        for index, elem in enumerate(res[:], 1):
            self.fav_list.addItem(str(index) + ". " + elem)

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