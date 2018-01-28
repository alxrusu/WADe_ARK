from flask import Flask, request, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

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
            query += """?Artist dbo:birthDate ?BirthDate.\n?Artist dbo:deathDate ?DeathDate.
FILTER (?BirthDate < "%s-01-01"^^xsd:date)
FILTER (?DeathDate > "%s-01-01"^^xsd:date)\n""" % (request.args[key], request.args[key])
        else:
            return "Unknown Parameter", 400

    query += """} LIMIT %s OFFSET %s""" % (limit, offset)

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
        entity["Name"] = result["ArtistLabel"]["value"]
        entity["Picture"] = result["Depiction"]["value"]
        entity["Description"] = result["Description"]["value"]
        response.append(entity)

    return jsonify(response)


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
?Artist dbo:birthDate ?BirthDate.
?Artist dbo:deathDate ?DeathDate.
FILTER (lang(?Abstract) = "en").
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
    response["BirthDate"] = result["RealBirthDate"]["value"]
    response["DeathDate"] = result["RealDeathDate"]["value"]
    response["Movements"] = result["Movements"]["value"]
    response["Artworks"] = artworks

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select ?ArtworkLabel ?Depiction where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist rdfs:label "%s"@en.
?Artwork dbo:author ?Artist.
?Artwork rdfs:label ?ArtworkLabel.
?Artwork foaf:depiction ?Depiction.
FILTER (lang(?ArtworkLabel) = "en").
} LIMIT 5
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

    return jsonify(response)


@app.route('/movements')
def getMovements():

    query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia: <http://dbpedia.org/resource/>
select distinct ?MovementLabel as ?Label where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
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
        response.append(result["Label"]["value"])

    return jsonify(response)


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
    response["Name"] = request.args["name"]
    response["Abstract"] = result["Abstract"]["value"]
    response["Picture"] = result["Depiction"]["value"]

    return jsonify(response)


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

    query += """} LIMIT %s OFFSET %s""" % (limit, offset)

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

    return jsonify(response)


@app.route('/artwork')
def getArtwork():

    if 'name' not in request.args or len(request.args) != 1:
        return "Invalid Parameters", 400

    query = """
select distinct ?Depiction ?AuthorLabel ?MuseumLabel ?CityLabel ?Height ?Width ?Abstract where {
?Painting <http://purl.org/linguistics/gold/hypernym> dbr:Painting.
?Painting rdfs:label "%s"@en.
?Painting foaf:depiction ?Depiction.
?Painting dbo:author ?Author.
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
} Limit 1""" % (request.args['name'])

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
    response["Name"] = request.args["name"]
    response["Picture"] = result["Depiction"]["value"]
    response["Author"] = result["AuthorLabel"]["value"]
    response["Museum"] = ""
    if "MuseumLabel" in result:
        response["Museum"] += result["MuseumLabel"]["value"]
        if "CityLabel" in result:
            response["Museum"] += ", "
    if "CityLabel" in result:
        response["Museum"] += result["CityLabel"]["value"]
    if "Abstract" in result:
        response["Abstract"] = result["Abstract"]["value"]
    else:
        response["Abstract"] = ""
    if "Height" in result and "Width" in result:
        response["Dimensions"] = "%s cm x %s cm" % (result["Height"]["value"], result["Width"]["value"])
    else:
        response["Dimensions"] = ""

    return jsonify(response)


if __name__ == '__main__':
    app.run()
