from secret import STATIC_API_KEY
import requests
import json
import logging


class APIHandler(object):
    def __init__(self, arg):
        self.url_for_image = 'https://static-maps.yandex.ru/v1'
        self.url_for_info = 'https://kudago.com/public-api/v1.4/search/'
        self.static_api_key = STATIC_API_KEY

    def get_image(self, coord, point=(), z=9, n=0):
        """
            Получает изображение с карты по заданным координатам.

            Этот метод формирует запрос к API и получает изображение карты
            с указанными параметрами. Если запрос успешен, возвращает содержимое
            изображения в виде бинарных данных. В противном случае возвращает None.

            Parameters
            ----------
            coord : list
                Широта и долгота точки, для которой нужно
                получить изображение карты.

            point : iterable
                Список дополнительных меток, назначаемых на карту. По умолчанию пустой кортеж.

            z : int
                Масштаб карты. Значение по умолчанию 9.

            n : int
                Смещение для идентификаторов меток в списке точек. Позволяет
                добавлять произвольные метки. Значение по умолчанию 0.

            Returns
            -------
            bytes or None
                Бинарные данные изображения карты, если запрос успешен
                (код 200); иначе возвращается None.
            """
        point = tuple(point)
        params = {
            "apikey": self.static_api_key,
            #"ll": ",".join([str(elem) for elem in coord]),
            'pt': '~'.join([f'{tuple(point)[i]},pm2rdl{i + 1 + n}' for i in range(len(point))]),
        }
        if z is not None:
            params['z'] = z
        if not point:
            params['ll'] = ",".join([str(elem) for elem in coord])

        request = requests.get(
            url=self.url_for_image,
            params=params,
        )

        if request.status_code == 200:
            return request.content
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.critical("get_image critical")
        return None

    def get_info_from_request(self, place, coordinates):
        """Получает информацию о месте по запросу к API.

            Parameters
            ----------
            place : str
                Название места для поиска информации.
            coordinates : list or tuple
                Координаты места в формате (широта, долгота).

            Returns
            ---------------------
            list of dict
                Список словарей с информацией о найденных местах.
            """
        response = requests.get(
            url=self.url_for_info,
            params={
                "q": place,
                "lat": coordinates[1],
                "lon": coordinates[0],
                "radius": 200000,
            },
        )
        result = []
        print(response.json())
        for res in response.json()["results"]:
            try:
                description = json.loads(res["description"])
                description = "\n".join([block["text"] for block in description["blocks"]])
            except Exception as e:
                description = res["description"]
                logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                    format="%(asctime)s %(levelname)s %(message)s")
                logging.critical("get_info_from_request critical")


            try:
                result.append(
                    {
                        "title": res["title"],
                        "url": res["item_url"],
                        "coords": str(res["coords"]["lon"]) + "," + str(res["coords"]["lat"]),
                        "description": description,
                        'address': res['address'],
                    }
                )
            except Exception as e:
                print(res["title"])
                print(res.keys())
                print(e)
                print("- + " * 20)
                logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                    format="%(asctime)s %(levelname)s %(message)s")
                logging.critical("get_info_from_request critical")

        if result is None:
            logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.info("in get_info_from_request result is None")

        return result
