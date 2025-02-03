from django.shortcuts import render, HttpResponse
from rest_framework import viewsets
from .models import Airport
from .serializers import AirportSerializer, FlightSearchSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import requests
def home(request):
    return HttpResponse(f"THIS IS API DELIVERY SYSTEM")

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    renderer_classes = [JSONRenderer]  # Specify JSONRenderer only



class FlightOnewayTrip(APIView):
    def post(self, request):
        serializer = FlightSearchSerializer(data=request.data)
        if serializer.is_valid():
            FLIGHT_KEY = os.environ.get("FLIGHT_API_KEY")
            source = serializer.validated_data.get('source_iata')
            destination = serializer.validated_data.get('destination_iata')
            date = serializer.validated_data.get('date')
            adults = serializer.validated_data.get('adults')
            children = serializer.validated_data.get('children')
            infant = serializer.validated_data.get('infant')
            ticket_class = serializer.validated_data.get("ticket_class")
            
            
            api_url = f"https://api.flightapi.io/onewaytrip/{FLIGHT_KEY}/{source}/{destination}/{date}/{adults}/{children}/{infant}/{ticket_class}/USD"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Create a mapping from carrier IDs to carrier names
                carrier_map = {carrier["id"]: carrier["name"] for carrier in data.get("carriers", [])}
                
                # Create a mapping from leg IDs to leg details
                legs_map = {leg["id"]: leg for leg in data.get("legs", [])}
                
                # Extract flight details
                flight_details = []
                for itinerary in data.get("itineraries", []):
                    for option in itinerary.get("pricing_options", []):
                        for item in option.get("items", []):
                            marketing_carrier_id = item.get("marketing_carrier_ids", [None])[0]
                            flight_name = carrier_map.get(marketing_carrier_id, "Unknown")
                            flight_price = item.get("price", {}).get("amount", "Unknown")
                            
                            # Fetch leg details using leg IDs
                            for leg_id in itinerary.get("leg_ids", []):
                                leg_details = legs_map.get(leg_id, {})
                                departure = leg_details.get("departure", "Unknown")
                                arrival = leg_details.get("arrival", "Unknown")
                                duration = leg_details.get("duration", "Unknown")
                                stop_count = leg_details.get("stop_count", "Unknown")
                                
                                flight_details.append({
                                    "flight_name": flight_name, 
                                    "price": flight_price,
                                    "departure": departure,
                                    "arrival": arrival,
                                    "duration": duration,
                                    "stop_count": stop_count
                                })
                
                return Response(flight_details, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to fetch flight data"}, status=response.status_code)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)