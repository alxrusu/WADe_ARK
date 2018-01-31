import requests


def valid_int(f):
    return f is not None and isinstance(f, int) and f > 0,


def valid_string(f):
    return f is not None and isinstance(f, str) and len(f) > 0


def valid_movement(f):
    return valid_string(f) and f != 'All'


def inflate_payload(fields, values):
    return {field: values[field]
            for field, valid in fields.items()
            if valid(values[field])}


class SparqlService:

    valid_artist_fields = {
        'name': valid_string,
        'movement': valid_movement,
        'year': valid_int,
        'limit': valid_int,
        'offset': valid_int,
    }

    valid_artwork_fields = {
        'name': valid_string,
        'author': valid_string,
        'limit': valid_int,
        'offset': valid_int,
    }

    def __init__(self):

        self.url = "http://127.0.0.1:5000"
        # self.url = "https://sparqlapi-dot-wadeark.appspot.com"
        # self.url = "http://127.0.0.1:5000"

    def search_artists(self, name=None, movement=None, year=None, limit=None, offset=None):
        values = {'name': name, 'movement': movement,
                  'year': year, 'limit': limit, 'offset': offset}
        url = self.url + '/artists'
        payload = inflate_payload(self.valid_artist_fields, values)
        try:
            return requests.get(url, params=payload).json()['Artists']
        except Exception as e:
            # print(e)
            return {}

    def search_artists_ext(self, name=None, movement=None, year=None, limit=None, offset=None):
        r = self.search_artists(name, movement, year, limit, offset)
        # print(r)
        for t in r:
            artist_r = self.get_artist(t['Name'])
            if len(artist_r) > 0:
                new_d = artist_r
                new_d["BirthDate"] = new_d["BirthDate"].split('-')[0]
                new_d["DeathDate"] = new_d["DeathDate"].split('-')[0]
                t.update(new_d)
        # print(r)
        return r

    def _get_year(self, date_str):
        return int(date_str.split('-')[0])

    def get_artists_depth(self, ts=None, te=None):
        url = self.url + '/artists/interval'
        if ts is None or te is None:
            return {}

        ts = self._get_year(ts)
        te = self._get_year(te)

        payload = {
            'start': ts,
            'end': te,
            'movements': True
        }
        try:
            return requests.get(url, params=payload).json()['Artists']
        except Exception as e:
            return {}

    def get_artworks(self, name=None, author=None, limit=None, offset=None):
        values = {'name': name, 'author': author,
                  'limit': limit, 'offset': offset}
        url = self.url + '/artworks'
        payload = inflate_payload(self.valid_artwork_fields, values)
        res = requests.get(url, params=payload)
        # print(res.status_code)
        try:
            return res.json()['Artworks']
        except Exception:
            return {}

    def get_artist(self, name):
        url = self.url + '/artist'
        payload = {
            "name": name
        }
        res = requests.get(url, params=payload)
        # print(res.status_code)
        if res.status_code == 400:
            return {}
        try:
            # print(res.json())
            return res.json()
        except Exception:
            return {}

    def get_recommend_artist(self, name):
        url = self.url + '/recommend/artist'
        payload = {
            "name": name
        }
        res = requests.get(url, params=payload)
        # print(res.status_code)
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
        # print(res.status_code)
        if res.status_code == 400:
            return {}
        try:
            return res.json()
        except Exception:
            return {}

    def get_recommend_artwork(self, name):
        url = self.url + '/recommend/artwork'
        payload = {
            "name": name
        }
        res = requests.get(url, params=payload)
        # print(res.status_code)
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
        if valid_string(name):
            payload['name'] = name
        res = requests.get(url, params=payload)
        # print(res.json())
        if res.status_code == 400:
            return []
        try:
            return res.json()['Movements']
        except Exception:
            return []

    def get_movement(self, name):
        url = self.url + '/movement'
        payload = {
            "name": name
        }
        res = requests.get(url, params=payload)
        if res.status_code == 400:
            return {"Name": name}
        try:
            return res.json()
        except Exception:
            return {}
