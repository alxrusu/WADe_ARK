from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .sparqlservice import SparqlService


sparql_service = SparqlService()


@csrf_exempt
@require_http_methods(["GET", "POST"])
def index(request):
    context = dict()
    if request.method == "POST":
        if 'search' in request.POST:
            name = request.POST['search']
            movement = None
            year = None
            limit = None
            offset = None
            r = sparql_service.search_artists(name, movement, year, limit=limit, offset=offset)
            context["results"] = r
    return render(request, 'arkapp/index.html', context)
