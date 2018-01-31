from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .sparqlservice import SparqlService,\
    valid_string, valid_movement, valid_int


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
            year = 0
        if valid_int(year):
            context['filters'].append(year)

        offset = max(int(request.POST.get('offset', '-1')), 0)

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
    return render(request, 'arkapp/movements.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def view_artist(request):
    context = dict()
    name = request.GET['name']
    print(name)
    r = sparql_service.get_artist(name)
    context["results"] = r
    r2 = sparql_service.get_artists_depth(ts=r['BirthDate'], te=r['DeathDate'])
    context["depth"] = r2
    recommend = sparql_service.get_recommend_artist(name)
    context["recommend"] = recommend
    return render(request, 'arkapp/artist.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def view_movement(request):
    context = dict()
    name = request.GET['name']
    print(name)
    r = sparql_service.get_movement(name)
    context["results"] = r
    return render(request, 'arkapp/movement.html', context)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def vizualize(request):
    context = dict()
    context['movements'] = sparql_service.get_movements()
    context['filters'] = []
    if request.method == "POST":
        name = None
        movement = None
        year = None
        limit = None
        offset = None
        if 'search' in request.POST:
            name = request.POST['search']
            if name is not None:
                if isinstance(name, str) is True and len(name) > 0:
                    context['filters'].append(name)
        if 'movements' in request.POST:
            movement = request.POST['movements']
            if movement is not None:
                if isinstance(movement, str) is True and len(movement) > 0 and movement != 'All':
                    context['filters'].append(movement)
        if 'year' in request.POST:
            year = request.POST['year']
            if year is not None:
                if len(year) > 0:
                    year = int(year)
                    if isinstance(year, int) is True and year > 0:
                        context['filters'].append(year)
        r = sparql_service.search_artists_ext(
            name, movement, year, limit=limit, offset=offset)
        context["results"] = r
    else:
        r = sparql_service.search_artists_ext(
            None, None, None, limit=None, offset=None)
        context["results"] = r
    return render(request, 'arkapp/vizualize.html', context)


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
