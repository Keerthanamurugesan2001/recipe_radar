"""
This module contains all the view of the recipe radar
"""
from django.http import HttpResponse
# Create your views here.


def home(request):
    """Hompe Page View"""
    return HttpResponse("Hello World!")
