from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .sparqlservice import SparqlService


sparql_service = SparqlService()


@csrf_exempt
@require_http_methods(["GET", "POST"])
def index(request):
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
                if isinstance(movement, str) is True and len(movement) > 0 and movement != 'ALL':
                    context['filters'].append(movement)
        if 'year' in request.POST:
            year = request.POST['year']
            if year is not None:
                year = int(year)
                if isinstance(year, int) is True and year > 0:
                    context['filters'].append(year)
        r = sparql_service.search_artists(name, movement, year, limit=limit, offset=offset)
        context["results"] = r
    return render(request, 'arkapp/index.html', context)
