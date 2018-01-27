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
            r = sparql_service.search_artists(request.POST['search'])
            context["results"] = str(r)
    return render(request, 'arkapp/index.html', context)
