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
        entity["Artwork"] = result["ArtworkLabel"]["value"]
        entity["Picture"] = result["Depiction"]["value"]
        artworks.append(entity)

    return jsonify(response)


@app.route('/movements')
def getMovements():

    query = """
select distinct ?MovementLabel where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist dbo:movement ?Movement.
?Movement rdfs:label ?MovementLabel.
FILTER (lang(?MovementLabel) = "en").
} ORDER BY ?MovementLabel"""

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    response = list()

    for result in results["results"]["bindings"]:
        response.append(result["MovementLabel"]["value"])

    return jsonify(response)


@app.route('/movement')
def getMovement():

    if 'name' not in request.args or len(request.args) != 1:
        return "Invalid Parameters", 400

    query = """
select distinct ?Abstract ?Depiction where {
?Artist <http://purl.org/linguistics/gold/hypernym> dbr:Painter.
?Artist dbo:movement ?Movement.
?Movement rdfs:label "%s"@en.
?Movement dbo:abstract ?Abstract.
?Movement foaf:depiction ?Depiction
FILTER (lang(?Abstract) = "en").
}""" % (request.args['name'])

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


if __name__ == '__main__':
    app.run()
