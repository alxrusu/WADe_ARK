import requests


class SparqlService:
    def __init__(self):
        self.url = "http://127.0.0.1:5000"

    def search_artists(self, name=None, movement=None, year=None, limit=None, offset=None):
        url = self.url + '/artists'
        payload = dict()
        if name is not None:
            if len(name) > 0:
                payload['name'] = name
        if movement is not None:
            payload['movement'] = movement
        if year is not None:
            payload['year'] = year
        if limit is not None:
            payload['limit'] = limit
        if offset is not None:
            payload['offset'] = offset
        res = requests.get(url, params=payload)
        print(res.status_code)
        print(res.text)
        r = res.json()
        return r
