import requests


class SparqlService:
    def __init__(self):
        self.url = "http://127.0.0.1:5000"

    def search_artists(self, name=None, movement=None, year=None, limit=None, offset=None):
        url = self.url + '/artists'
        payload = dict()
        if name is not None:
            if isinstance(name, str) is True and len(name) > 0:
                payload['name'] = name
        if movement is not None:
            if isinstance(movement, str) is True and len(movement) > 0 and movement != 'ALL':
                payload['movement'] = movement
        if year is not None:
            year = int(year)
            if isinstance(year, int) is True and year > 0:
                payload['year'] = year
        if limit is not None:
            if isinstance(limit, int) is True and limit > 0:
                payload['limit'] = limit
        if offset is not None:
            if isinstance(offset, int) is True and offset > 0:
                payload['offset'] = offset
        res = requests.get(url, params=payload)
        print(res.status_code)
        try:
            r = res.json()
        except Exception:
            r = {}
        return r

    def get_movements(self):
        url = self.url + '/movements'
        res = requests.get(url)
        print(res.status_code)
        print(res.text)
        r = res.json()
        return r
