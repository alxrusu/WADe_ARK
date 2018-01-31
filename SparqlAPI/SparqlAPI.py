from flask import Flask, request, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed
from adnotations import artist_adnotation, artist_list_adnotation,\
    movement_list_adnotation, artwork_adnotation, movement_adnotation,\
    artwork_list_adnotation
from gevent.wsgi import WSGIServer

app = Flask(__name__)


@app.route('/artists')
def getArtists():

    limit = 15
    offset = 0

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?ArtistLabel ?Depiction ?Description where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label ?ArtistLabel.
?Artist foaf:depiction ?Depiction.
?Artist dct:description ?Description.
?Painting dbo:author ?Artist.
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
FILTER (lang(?ArtistLabel) = "en").
FILTER (lang(?Description) = "en").
"""

    for key in request.args:
        if key == 'limit':
            limit = request.args[key]
        elif key == 'offset':
            offset = request.args[key]
        elif key == 'name':
            query += """FILTER (contains (lcase(?ArtistLabel), "%s")).\n""" % (request.args[key].lower())
        elif key == 'movement':
            query += """?Artist dbo:movement ?Movement.\n?Movement rdfs:label "%s"@en\n""" % (request.args[key])
        elif key == 'year':
            query += """?Artist dbo:birthDate ?BirthDate.
?Artist dbo:deathDate ?DeathDate.
FILTER (?BirthDate < "%s-1-1"^^xsd:date)
FILTER (?DeathDate > "%s-1-1"^^xsd:date)\n""" % (request.args[key], request.args[key])
        else:
            return "Unknown Parameter", 400

    query += """} ORDER BY ?ArtistLabel LIMIT %s OFFSET %s""" % (limit, offset)

    #print (query)

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery (query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except QueryBadFormed as e:
        return "Invalid Parameters", 400

    response = list()

    for result in results["results"]["bindings"]:
        entity = dict()
        entity["Name"] = result["ArtistLabel"]["value"]
        entity["Picture"] = result["Depiction"]["value"]
        entity["Description"] = result["Description"]["value"]
        response.append(entity)

    return jsonify(artist_list_adnotation(response))


@app.route('/artist')
def getArtist():

    if 'name' not in request.args or len(request.args) != 1:
        return "Invalid Parameters", 400

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?Depiction ?Abstract (group_concat(DISTINCT ?MovementLabel; separator = ", ") as ?Movements)
MIN(?BirthDate) as ?RealBirthDate MIN(?DeathDate) as ?RealDeathDate where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label "%s"@en.
?Artist foaf:depiction ?Depiction.
?Artist dbo:abstract ?Abstract.
FILTER (lang(?Abstract) = "en").
OPTIONAL {
?Artist dbo:birthDate ?BirthDate.
}.
OPTIONAL {
?Artist dbo:deathDate ?DeathDate.
}.
OPTIONAL {
?Artist dbo:movement ?Movement.
?Movement rdfs:label ?MovementLabel.
FILTER (lang(?MovementLabel) = "en").
}.
} GROUP BY ?ArtistLabel ?Depiction ?Abstract LIMIT 1
""" % (request.args['name'])

    print (query)

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery (query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except QueryBadFormed as e:
        return "Invalid Parameters", 400

    if len(results["results"]["bindings"]) < 1:
        return "No results", 400

    result = results["results"]["bindings"][0]
    response = dict()
    artworks = list()
    response["Name"] = request.args["name"]
    response["Picture"] = result["Depiction"]["value"]
    response["Abstract"] = result["Abstract"]["value"]
    if "RealBirthDate" in result:
        response["BirthDate"] = result["RealBirthDate"]["value"]
    else:
        response["BirthDate"] = ""
    if "RealDeathDate" in result:
        response["DeathDate"] = result["RealDeathDate"]["value"]
    else:
        response["DeathDate"] = ""
    response["Movements"] = result["Movements"]["value"]
    response["Artworks"] = artworks

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select ?ArtworkLabel ?Depiction where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label "%s"@en.
?Artwork dbo:author ?Artist.
?Artwork <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Artwork rdfs:label ?ArtworkLabel.
?Artwork foaf:depiction ?Depiction.
FILTER (lang(?ArtworkLabel) = "en").
} LIMIT 6
""" % (request.args['name'])

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        entity = dict()
        entity["Author"] = request.args["name"]
        entity["Name"] = result["ArtworkLabel"]["value"]
        entity["Picture"] = result["Depiction"]["value"]
        artworks.append(entity)

    return jsonify(artist_adnotation(response))


@app.route('/movements')
def getMovements():

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?MovementLabel as ?Label ?Depiction where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Painting dbo:author ?Artist.
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Artist dbo:movement ?Movement.
?Movement rdfs:label ?MovementLabel.
?Movement dbo:abstract ?Abstract.
?Movement foaf:depiction ?Depiction.
FILTER (lang(?MovementLabel) = "en").
"""

    if 'name' in request.args:
        query += """FILTER (contains (lcase(?MovementLabel), "%s")).\n""" % (request.args['name'].lower())

    query += """} ORDER BY ?MovementLabel"""

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    response = list()

    for result in results["results"]["bindings"]:
        entity = dict()
        entity["Name"] = result["Label"]["value"]
        entity["Picture"] = result["Depiction"]["value"]
        response.append(entity)

    return jsonify(movement_list_adnotation(response))


@app.route('/movement')
def getMovement():

    if 'name' not in request.args or len(request.args) != 1:
        return "Invalid Parameters", 400

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?Abstract ?Depiction where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist dbo:movement ?Movement.
?Movement rdfs:label "%s"@en.
?Movement dbo:abstract ?Abstract.
?Movement foaf:depiction ?Depiction.
FILTER (lang(?Abstract) = "en").
} LIMIT 1""" % (request.args['name'])

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except QueryBadFormed as e:
        return "Invalid Parameters", 400

    if len(results["results"]["bindings"]) < 1:
        return "No results", 400

    result = results["results"]["bindings"][0]
    response = dict()
    artists = list()
    response["Name"] = request.args["name"]
    response["Abstract"] = result["Abstract"]["value"]
    response["Picture"] = result["Depiction"]["value"]
    response["Artists"] = artists

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?ArtistLabel ?Depiction ?Description where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label ?ArtistLabel.
?Artist foaf:depiction ?Depiction.
?Artist dct:description ?Description.
?Painting dbo:author ?Artist.
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
FILTER (lang(?ArtistLabel) = "en").
FILTER (lang(?Description) = "en").
?Artist dbo:movement ?Movement.
?Movement rdfs:label "%s"@en.
} LIMIT 6""" % (request.args['name'])

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        entity = dict()
        entity["Name"] = result["ArtistLabel"]["value"]
        entity["Picture"] = result["Depiction"]["value"]
        entity["Description"] = result["Description"]["value"]
        artists.append(entity)

    return jsonify(movement_adnotation(response))


@app.route('/artworks')
def getArtworks():

    limit = 15
    offset = 0

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?PaintingLabel ?Depiction ?AuthorLabel where {
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Painting rdfs:label ?PaintingLabel.
?Painting foaf:depiction ?Depiction.
?Painting dbo:author ?Author.
?Author <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Author rdfs:label ?AuthorLabel.
FILTER (lang(?PaintingLabel) = "en").
FILTER (lang(?AuthorLabel) = "en").
"""

    for key in request.args:
        if key == 'limit':
            limit = request.args[key]
        elif key == 'offset':
            offset = request.args[key]
        elif key == 'name':
            query += """FILTER (contains (lcase(?PaintingLabel), "%s")).\n""" % (request.args[key].lower())
        elif key == 'author':
            query += """FILTER (contains (lcase(?AuthorLabel), "%s")).\n""" % (request.args[key].lower())

    query += """} ORDER BY ?AuthorLabel ?PaintingLabel LIMIT %s OFFSET %s""" % (limit, offset)

    print (query)

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery (query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except QueryBadFormed as e:
        return "Invalid Parameters", 400

    response = list()

    for result in results["results"]["bindings"]:
        entity = dict()
        entity["Name"] = result["PaintingLabel"]["value"]
        entity["Picture"] = result["Depiction"]["value"]
        entity["Author"] = result["AuthorLabel"]["value"]
        response.append(entity)

    return jsonify(artwork_list_adnotation(response))


def queryArtwork(name):

    query = """
select distinct ?Depiction ?AuthorLabel ?Year ?MuseumLabel ?CityLabel ?Height ?Width ?Abstract where {
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Painting rdfs:label "%s"@en.
?Painting foaf:depiction ?Depiction.
?Painting dbo:author ?Author.
?Author <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Author rdfs:label ?AuthorLabel.
FILTER (lang(?AuthorLabel) = "en").
optional {
?Painting dbp:heightMetric ?Height.
?Painting dbp:widthMetric ?Width.
}
optional {
?Painting dbp:year ?Year.
}
optional {
?Painting dbo:museum ?Museum.
?Museum rdfs:label ?MuseumLabel.
FILTER (lang(?MuseumLabel) = "en").
}
optional {
?Painting dbp:city ?City.
?City rdfs:label ?CityLabel.
FILTER (lang(?CityLabel) = "en").
}
optional {
?Painting dbo:abstract ?Abstract.
FILTER (lang(?Abstract) = "en").
}
} Limit 1""" % (name)

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except QueryBadFormed as e:
        return None

    if len(results["results"]["bindings"]) < 1:
        return None

    result = results["results"]["bindings"][0]
    artwork = dict()
    artwork["Name"] = name
    artwork["Picture"] = result["Depiction"]["value"]
    artwork["Author"] = result["AuthorLabel"]["value"]
    if "Year" in result:
        artwork["Year"] = result["Year"]["value"]
    else:
        artwork["Year"] = ""
    artwork["Museum"] = ""
    if "MuseumLabel" in result:
        artwork["Museum"] += result["MuseumLabel"]["value"]
        if "CityLabel" in result:
            artwork["Museum"] += ", "
    if "CityLabel" in result:
        artwork["Museum"] += result["CityLabel"]["value"]
    if "Abstract" in result:
        artwork["Abstract"] = result["Abstract"]["value"]
    else:
        artwork["Abstract"] = ""
    if "Height" in result and "Width" in result:
        artwork["Dimensions"] = "%s cm x %s cm" % (result["Height"]["value"], result["Width"]["value"])
    else:
        artwork["Dimensions"] = ""
        
    return artwork


@app.route('/artwork')
def getArtwork():

    if 'name' not in request.args or len(request.args) != 1:
        return "Invalid Parameters", 400

    response = queryArtwork(request.args["name"])
    if response is None:
        return "No results", 400

    return jsonify(artwork_adnotation(response))


@app.route('/recommend/artwork')
def getRecommendArtwork():

    if 'name' not in request.args or len(request.args) != 1:
        return "Invalid Parameters", 400

    artwork = queryArtwork(request.args["name"])
    if artwork is None:
        return "No results", 400

    recommend = dict()

    queries = ["""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?AuthorLabel ?PaintingLabel ?Depiction where {
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Painting rdfs:label ?PaintingLabel.
?Painting foaf:depiction ?Depiction.
?Painting dbo:author ?Author.
?Author <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Author rdfs:label ?AuthorLabel.
FILTER (lang(?PaintingLabel) = "en").
FILTER (?AuthorLabel = "%s"@en).
""" % (artwork["Author"]),

"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?AuthorLabel ?PaintingLabel ?Depiction where {
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Painting rdfs:label ?PaintingLabel.
?Painting foaf:depiction ?Depiction.
?Painting dbo:author ?Author.
?Author <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Author rdfs:label ?AuthorLabel.
FILTER (lang(?PaintingLabel) = "en").
FILTER (lang(?AuthorLabel) = "en").
?MyAuthor <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?MyAuthor rdfs:label ?MyAuthorLabel.
FILTER (?MyAuthorLabel = "%s"@en).
FILTER (?Author != ?MyAuthor)
?MyAuthor dbo:birthPlace ?MyBirthPlace.
?Author dbo:birthPlace ?BirthPlace.
?MyBirthPlace dbo:country ?Country.
?BirthPlace dbo:country ?Country.
""" % (artwork["Author"]),

"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?AuthorLabel ?PaintingLabel ?Depiction where {
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Painting rdfs:label ?PaintingLabel.
?Painting foaf:depiction ?Depiction.
?Painting dbo:author ?Author.
?Author <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Author rdfs:label ?AuthorLabel.
FILTER (lang(?PaintingLabel) = "en").
FILTER (lang(?AuthorLabel) = "en").
?MyAuthor <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?MyAuthor rdfs:label ?MyAuthorLabel.
FILTER (?MyAuthorLabel = "%s"@en).
FILTER (?Author != ?MyAuthor).
?MyAuthor dbo:movement ?Movement.
?Author dbo:movement ?Movement.
""" % (artwork["Author"])
    ]

    for query in queries:

        try:
            year = int(artwork["Year"])
            query += "?Painting dbp:year ?Year.\nFILTER (datatype(?Year) = xsd:integer).\n} ORDER BY abs(?Year-%d) LIMIT 5" % (year)
        except ValueError:
            query += "} ORDER BY abs(?Year-%s) LIMIT 5"

        print (query)
        try:
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setQuery (query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        except QueryBadFormed as e:
            return "Invalid Parameters", 400

        for result in results["results"]["bindings"]:
            entity = dict()
            entity["Name"] = result["PaintingLabel"]["value"]
            entity["Picture"] = result["Depiction"]["value"]
            entity["Author"] = result["AuthorLabel"]["value"]
            recommend[entity["Name"]] = entity

    recommend.pop(artwork["Name"], None)
    return jsonify(list(recommend.values()))


@app.route('/recommend/artist')
def getRecommendArtist():

    if 'name' not in request.args or len(request.args) != 1:
        return "Invalid Parameters", 400

    recommend = dict()

    queries = ["""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?ArtistLabel ?Depiction ?Description where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label ?ArtistLabel.
?Artist foaf:depiction ?Depiction.
?Artist dct:description ?Description.
?Painting dbo:author ?Artist.
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
FILTER (lang(?ArtistLabel) = "en").
FILTER (lang(?Description) = "en").
?MyArtist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?MyArtist rdfs:label ?MyArtistLabel.
FILTER (?MyArtistLabel = "%s"@en).
FILTER (?Artist != ?MyArtist).
?MyArtist dbo:birthPlace ?MyBirthPlace.
?Artist dbo:birthPlace ?BirthPlace.
?MyBirthPlace dbo:country ?Country.
?BirthPlace dbo:country ?Country.
} LIMIT 6""" % (request.args["name"]),

"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?ArtistLabel ?Depiction ?Description where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label ?ArtistLabel.
?Artist foaf:depiction ?Depiction.
?Artist dct:description ?Description.
?Painting dbo:author ?Artist.
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
FILTER (lang(?ArtistLabel) = "en").
FILTER (lang(?Description) = "en").
?MyArtist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?MyArtist rdfs:label ?MyArtistLabel.
FILTER (?MyArtistLabel = "%s"@en).
FILTER (?Artist != ?MyArtist).
?MyArtist dbo:movement ?Movement.
?Artist dbo:movement ?Movement.
} LIMIT 6""" % (request.args["name"])
    ]

    for query in queries:

        print (query)
        try:
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setQuery (query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        except QueryBadFormed as e:
            return "Invalid Parameters", 400

        for result in results["results"]["bindings"]:
            entity = dict()
            entity["Name"] = result["ArtistLabel"]["value"]
            entity["Picture"] = result["Depiction"]["value"]
            entity["Description"] = result["Description"]["value"]
            recommend[entity["Name"]] = entity

    return jsonify(list(recommend.values()))


@app.route('/artists/interval')
def getInterval():

    if 'start' not in request.args or 'end' not in request.args:
        return "Invalid Parameters", 400

    movements = False
    if 'movements' in request.args:
        try:
            movements = bool(request.args["movements"])
        except ValueError:
            return "Invalid Parameters", 400

    exception = None
    if 'exception' in request.args:
        exception = request.args["exception"]

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?ArtistLabel MIN(?BirthDate) as ?RealBirthDate MIN(?DeathDate) as ?RealDeathDate """

    if movements:
        query += """(group_concat(DISTINCT ?MovementLabel; separator = ", ") as ?Movements) """

    query += """where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label ?ArtistLabel.
FILTER (lang(?ArtistLabel) = "en").
?Artist dbo:birthDate ?BirthDate.
?Artist dbo:deathDate ?DeathDate.
FILTER (?BirthDate > "%s-1-1"^^xsd:date).
FILTER (?DeathDate < "%s-1-1"^^xsd:date).
""" % (request.args["start"], request.args["end"])

    if movements:
        query += """?Artist dbo:movement ?Movement.
?Movement rdfs:label ?MovementLabel.
FILTER (lang(?MovementLabel) = "en").\n"""

    if exception:
        query += """FILTER (?ArtistLabel != "%s"@en)""" % (exception)

    query += """} GROUP BY ?ArtistLabel ORDER BY ?RealBirthDate LIMIT 30"""

    print(query)
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except QueryBadFormed as e:
        return "Invalid Parameters", 400

    response = list()

    for result in results["results"]["bindings"]:
        entity = dict()
        entity["Name"] = result["ArtistLabel"]["value"]
        entity["BirthDate"] = result["RealBirthDate"]["value"]
        entity["DeathDate"] = result["RealDeathDate"]["value"]
        if movements:
            entity["Movements"] = result["Movements"]["value"]
        response.append(entity)

    return jsonify(response)


if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
