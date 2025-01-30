from rest_framework import serializers
from .models import Airport

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'city', 'airport_name', 'faa', 'iata', 'icao']
