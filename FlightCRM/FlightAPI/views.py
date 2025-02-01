from django.shortcuts import render, HttpResponse
from rest_framework import viewsets
from .models import Airport
from .serializers import AirportSerializer
from rest_framework.renderers import JSONRenderer

def home(request):
    return render(
        request,
        "index.html"
    ) 

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    renderer_classes = [JSONRenderer]  # Specify JSONRenderer only
