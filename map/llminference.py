import requests
import logging
class Llminference():
    def __init__(self):
        self.url = 'http://127.0.0.1:8000/'


    def post(self, text=''):
        try:
            request = requests.post(self.url + 'summarize', json={'input': text})
        except:
            return 'Не удалось суммаризировать текст'
        if request.status_code == 200:
            return request.json()['summary']
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.warning("summarize warning")
        return 'Не удалось суммаризировать текст'

