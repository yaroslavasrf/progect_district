import requests
import logging
class Llminference():
    def __init__(self):
        self.url = 'https://13fe-188-130-155-167.ngrok-free.app'


    def post(self, text=''):
        #request = requests.post(self.url + 'summarize', json={'input': text})

        #print(request.content)
        # if request.status_code == 200:
        #     return request.json
        # logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
        #                     format="%(asctime)s %(levelname)s %(message)s")
        # logging.warning("summarize warning")
        # return 'Не удалось суммаризировать текст'
        return 'huhkj'

