from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .preprocessing import valid_string, valid_movement, valid_int
from .sparqlservice import SparqlService

import math

sparql_service = SparqlService()


@csrf_exempt
@require_http_methods(["GET", "POST"])
def index(request):
    context = dict()
    context['movements'] = sparql_service.get_movements()
    context['filters'] = []

    limit = None
    offset = None
    name = None
    movement = None
    year = None
    if request.method == "POST":
        name = request.POST.get('search')
        if valid_string(name):
            context['filters'].append(name)

        movement = request.POST.get('movements')
        if valid_movement(movement):
            context['filters'].append(movement)
        try:
            year = int(request.POST.get('year', '-1'))
        except Exception:
            year = None

        if valid_int(year):
            context['filters'].append(year)

        try:
            offset = max(int(request.POST.get('offset', '-1')), 0)
        except Exception:
            offset = 0

    context["results"] = sparql_service.search_artists(
        name, movement, year, limit=limit, offset=offset)

    context["more"] = dict()
    if name is not None:
        context["more"]["name"] = name
    if movement is not None:
        context["more"]["movement"] = movement
    if year is not None:
        context["more"]["year"] = year
    if offset is not None:
        context["more"]["offset"] = offset
    else:
        context["more"]["offset"] = 0

    return render(request, 'arkapp/index.html', context)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def movements(request):
    context = dict()
    # context['movements'] = sparql_service.get_movements()
    context['filters'] = []

    name = None
    if request.method == "POST":
        if 'search' in request.POST:
            name = request.POST['search']
            if valid_string(name):
                context['filters'].append(name)
    r = sparql_service.get_movements(name=name)
    context["results"] = r
    print(r)
    return render(request, 'arkapp/movements.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def view_artist(request):
    context = dict()
    name = request.GET['name']
    print(name)
    r = sparql_service.get_artist(name)
    print(r)
    if len(r) == 0:
        return render(request, 'arkapp/not_found.html', context)

    context["results"] = r
    context["depth"] = []
    context["hist"] = {}
    if 'BirthDate' in r and valid_string(r['BirthDate']):
        death_date = r.get('DeathDate', None)
        birth_date = r['BirthDate']
        r2 = sparql_service.get_artists_depth(ts=birth_date, te=death_date)
        histogram = dict()
        for ind in range(len(r2)):
            if 'Movements' in r2[ind]:
                movs = r2[ind]['Movements'].split(', ')
                for m in movs:
                    if m in histogram:
                        histogram[m]['Value'] += 1
                    else:
                        histogram[m] = {
                            'Value': 1,
                            'Movement': m
                        }
        print(histogram)
        context["depth"] = r2
        context["hist"] = histogram
    context["movements"] = r["Movements"].split(", ")
    recommend = sparql_service.get_recommend_artist(name)
    context["recommend"] = recommend
    return render(request, 'arkapp/artist.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def view_movement(request):
    context = {"results": sparql_service.get_movement(request.GET['name'])}
    return render(request, 'arkapp/movement.html', context)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def visualize(request):
    context = dict()
    context["depth"] = []
    context["hist"] = {}

    start = '1500-0'
    end = '1620-0'

    try:
        if request.method == "POST":
            if 'startYear' in request.POST:
                if valid_string(request.POST['startYear']):
                    start = str(int(request.POST['startYear'])) + '-0'
            if 'endYear' in request.POST:
                if valid_string(request.POST['endYear']):
                    end = str(int(request.POST['endYear'])) + '-0'
    except Exception:
        pass

    context["start_year"] = int(start.split('-')[0])
    context["end_year"] = int(end.split('-')[0])

    try:
        r2 = sparql_service.get_artists_depth(ts=start, te=end)

        all_movs_dict = {}
        arr_ind = 0
        for res in r2:
            if 'Movements' in res:
                movs = res['Movements'].split(', ')
                for mov in movs:
                    if mov not in all_movs_dict:
                        all_movs_dict[mov] = arr_ind
                        arr_ind += 1

        histogram = dict()
        num_movs = len(all_movs_dict)

        context["movements"] = all_movs_dict


        for ind in range(len(r2)):
            if 'Movements' in r2[ind] and 'MeanYears' in r2[ind]:
                meanYears = r2[ind]['MeanYears']

                movs = r2[ind]['Movements'].split(', ')

                for key in histogram:
                    distance = math.sqrt((meanYears - int(key))**2)
                    if distance < 20:
                        for m in movs:
                            mi = all_movs_dict[m]
                            histogram[key][mi] += 1
                        break
                else:
                    histogram[meanYears] = [0] * num_movs
                    for m in movs:
                        mi = all_movs_dict[m]
                        histogram[meanYears][mi] = 1

        context["depth"] = r2
        context["hist"] = histogram
    except Exception as e:
        print(e, type(e))
    return render(request, 'arkapp/visualize.html', context)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def view_artworks(request):
    context = dict()
    context['filters'] = []
    name = None
    author = None
    limit = None
    offset = None
    if request.method == "POST":
        if 'search' in request.POST:
            name = request.POST['search']
            if name is not None:
                if isinstance(name, str) is True and len(name) > 0:
                    context['filters'].append(name)
        if 'author' in request.POST:
            author = request.POST['author']
            if author is not None:
                if isinstance(author, str) is True and len(author) > 0:
                    context['filters'].append(author)
        if 'offset' in request.POST:
            offset = request.POST['offset']
            offset = int(offset)
            if offset < 0:
                offset = 0
    r = sparql_service.get_artworks(name, author, limit, offset)
    context["results"] = r
    context["more"] = dict()
    if name is not None:
        context["more"]["name"] = name
    if author is not None:
        context["more"]["author"] = author
    if offset is not None:
        context["more"]["offset"] = offset
    else:
        context["more"]["offset"] = 0
    return render(request, 'arkapp/artworks.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def view_artwork(request):
    context = dict()
    name = request.GET['name']
    print(name)
    r = sparql_service.get_artwork(name)
    context["results"] = r
    recommend = sparql_service.get_recommend_artwork(name)
    context["recommend"] = recommend
    return render(request, 'arkapp/artwork.html', context)
