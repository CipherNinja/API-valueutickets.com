from rest_framework import serializers
from .models import Airport

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'city', 'airport_name', 'faa', 'iata', 'icao']



class FlightSearchSerializer(serializers.Serializer):
    source_iata = serializers.CharField(max_length=3)  # Departure Airport IATA
    destination_iata = serializers.CharField(max_length=3)  # Arrival Airport IATA
    date = serializers.DateField(format="%Y-%m-%d")  # Flight Date (YYYY-MM-DD)
    
    adults = serializers.IntegerField(min_value=1, max_value=9, default=1)  # Adult passengers (Default 1)
    children = serializers.IntegerField(min_value=0, max_value=9, default=0)  # Children (0-12 yrs)
    infants = serializers.IntegerField(min_value=0, max_value=9, default=0)  # Infants (0-2 yrs)

    ticket_class = serializers.ChoiceField(choices=["Economy", "Premium_Economy", "Business", "First"], default="Economy")

    # def validate(self, data):
    #     adults = data.get('adults', 1)
    #     children = data.get('children', 0)
    #     infants = data.get('infants', 0)
        
    #     total_passengers = adults + children + infants
        
    #     if total_passengers > 9:
    #         raise serializers.ValidationError("Total number of passengers cannot exceed 9.")
        
    #     if infants > adults:
    #         raise serializers.ValidationError("Each adult can carry only one infant.")
        
    #     if children > 8 and adults == 1:
    #         raise serializers.ValidationError("One adult can carry up to 8 children.")
        
    #     return data
    

