from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, 'app/index.html')


def album(request):
    return render(request, 'app/album.html')
