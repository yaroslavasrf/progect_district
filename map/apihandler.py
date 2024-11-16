from secret import STATIC_API_KEY
import requests
import json


class APIHandler(object):
    def __init__(self, arg):
        self.url_for_image = 'https://static-maps.yandex.ru/v1'
        self.url_for_info = 'https://kudago.com/public-api/v1.4/search/'
        self.static_api_key = STATIC_API_KEY

    def get_image(self, coord, point=(), z=9, n=0):
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
        print(request.status_code)

        if request.status_code == 200:
            return request.content

        return None

    def get_info_from_request(self, place, coordinates):
        print(place, coordinates)
        response = requests.get(
            url=self.url_for_info,
            params={
                "q": place,
                "lat": coordinates[1],
                "lon": coordinates[0],
                "radius": 20000,
            },
        )
        print(response.status_code)

        result = []
        for res in response.json()["results"]:
            try:
                description = json.loads(res["description"])
                description = "\n".join([block["text"] for block in description["blocks"]])
            except Exception as e:
                description = res["description"]

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

        print(result)
        return result
