def artist_adnotation(artist_json):
    artist_json.update({"@context": {
        "Abstract": "http://schema.org/description",
        "BirthDate": {
            "@id": "http://schema.org/birthDate",
            "@type": "@id"
        },
        "DeathDate": {
            "@id": "http://schema.org/deathDate",
            "@type": "@id"
        },
        "Name": "http://schema.org/name",
        "Author": "http://schema.org/author",
        "Picture": {
            "@id": "http://schema.org/image",
            "@type": "@id"
        },
        "Movement": "http://schema.org/genre",
        "Painting": "http://schema.org/Painting"
    }})
    for artwork in artist_json['Artworks']:
        artwork['@type'] = 'Painting'
    return artist_json


def artist_list_adnotation(artist_list_json):
    artists_json = {
        "@context": {
            "Name": "http://schema.org/name",
            "Picture": {
                "@id": "http://schema.org/image",
                "@type": "@id"
            },
            "Description": "http://schema.org/description",
            "Artists": "http://schema.org/ItemList",
            "Author": "http://schema.org/author"
        },
        "Artists": artist_list_json}

    for artist in artists_json['Artists']:
        artist.update({'@type': 'Author'})
    return artists_json


def artwork_list_adnotation(artwork_list_json):
    artwork_json = {
        "@context": {
            "Name": "http://schema.org/name",
            "Picture": {
                "@id": "http://schema.org/image",
                "@type": "@id"
            },
            "Author": "http://schema.org/author",
            "Painting": "http://schema.org/Painting"
        },
        "Artworks": artwork_list_json}

    for artwork in artwork_json['Artworks']:
        artwork.update({'@type': 'Painting'})
    return artwork_json


def movement_adnotation(movement_json):
    movement_json.update({
        "@context": {
            "Name": "http://schema.org/name",
            "Abstract": "http://schema.org/description",
            "Picture": {
                "@id": "http://schema.org/image",
                "@type": "@id"
            },
            "Description": "http://schema.org/description",
            "Artists": "http://schema.org/ItemList",
        }})
    for artist in movement_json['Artists']:
        artist.update({'@type': 'Author'})
    return movement_json


def movement_list_adnotation(movement_list_json):
    return {
        "@context": {
            "Movements": "http://schema.org/ItemList"
        },
        "Movements": movement_list_json
    }


def artwork_adnotation(artwork_json):
    artwork_json.update({

        "@context": {
            "Abstract": "http://schema.org/description",
            "Dimensions": "http://schema.org/description",
            "Year": {
                "@id": "http://schema.org/Date",
                "@type": "@id"
            },
            "Name": "http://schema.org/name",
            "Author": "http://schema.org/author",
            "Picture": {
                "@id": "http://schema.org/image",
                "@type": "@id"
            },
            "Museum": "http://schema.org/name"
        }
    })
    return artwork_json
