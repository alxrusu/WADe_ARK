import requests


class SparqlService:
    def __init__(self):
        self.url = "http://127.0.0.1:5000"

    def search_artists(self, term):
        url = self.url + '/artists'
        res = requests.get(url)
        print(res.status_code)
        print(res.text)
        r = res.json()
        return r
