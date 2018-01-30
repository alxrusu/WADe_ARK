import requests


class SparqlService:
    def __init__(self):
        self.url = "https://sparqlapi-dot-wadeark.appspot.com"

    def search_artists(self, name=None, movement=None, year=None, limit=None, offset=None):
        url = self.url + '/artists'
        payload = dict()
        if name is not None:
            if isinstance(name, str) is True and len(name) > 0:
                payload['name'] = name
        if movement is not None:
            if isinstance(movement, str) is True and len(movement) > 0 and movement != 'All':
                payload['movement'] = movement
        if year is not None:
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

    def search_artists_ext(self, name=None, movement=None, year=None, limit=None, offset=None):
        url = self.url + '/artists'
        payload = dict()
        if name is not None:
            if isinstance(name, str) is True and len(name) > 0:
                payload['name'] = name
        if movement is not None:
            if isinstance(movement, str) is True and len(movement) > 0 and movement != 'All':
                payload['movement'] = movement
        if year is not None:
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

        for t in range(len(r)):
            artist_r = self.get_artist(r[t]['Name'])
            if len(artist_r) > 0:
                new_d = artist_r
                bd = new_d["BirthDate"].split('-')[0]
                dd = new_d["DeathDate"].split('-')[0]
                new_d["BirthDate"] = bd
                new_d["DeathDate"] = dd
                r[t].update(new_d)
        return r

    def get_artworks(self, name=None, author=None, limit=None, offset=None):
        url = self.url + '/artworks'
        payload = dict()
        if name is not None:
            if isinstance(name, str) is True and len(name) > 0:
                payload['name'] = name
        if author is not None:
            if isinstance(author, str) is True and len(author) > 0:
                payload['author'] = author
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

    def get_artist(self, name):
        url = self.url + '/artist'
        payload = {
            "name": name
        }
        res = requests.get(url, params=payload)
        print(res.status_code)
        if res.status_code == 400:
            return {}
        try:
            r = res.json()
        except Exception:
            return {}
        return r

    def get_artwork(self, name):
        url = self.url + '/artwork'
        payload = {
            "name": name
        }
        res = requests.get(url, params=payload)
        print(res.status_code)
        if res.status_code == 400:
            return {}
        try:
            r = res.json()
        except Exception:
            return {}
        return r

    def get_movements(self, name=None):
        url = self.url + '/movements'
        payload = dict()
        if name is not None:
            if isinstance(name, str) is True and len(name) > 0:
                payload['name'] = name
        res = requests.get(url, params=payload)
        print(res.status_code)
        if res.status_code == 400:
            return []
        try:
            r = res.json()
        except Exception:
            return []
        return r

    def get_movement(self, name):
        url = self.url + '/movement'
        print(name)
        payload = {
            "name": name
        }
        res = requests.get(url, params=payload)
        print(res.status_code)
        print(res.text)
        if res.status_code == 400:
            return {"Name": name}
        try:
            r = res.json()
        except Exception:
            return {}
        return r
