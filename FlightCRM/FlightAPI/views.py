from django.shortcuts import render, HttpResponse
from rest_framework import viewsets
from .serializers import AirportSerializer, FlightSearchSerializer,FlightBookingCreateSerializer,FlightBookingSerializer
from .models import Airport,Customer,FlightBooking,Passenger,Payment
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    renderer_classes = [JSONRenderer]  # Specify JSONRenderer only


class FlightBookingCreateView(APIView):
    """
    Handles POST requests to create a new flight booking along with associated customer, passengers, and payment details.
    """
    def post(self, request, *args, **kwargs):
        # Initialize the serializer with the incoming data
        serializer = FlightBookingCreateSerializer(data=request.data)
        
        # Validate the data
        if serializer.is_valid():
            
            customer_email = serializer.validated_data['email']
            passengers = serializer.validated_data['passengers']
            flight_details = {
                "flight_name": serializer.validated_data['flight_name'],
                "departure_iata": serializer.validated_data['departure_iata'],
                "arrival_iata": serializer.validated_data['arrival_iata'],
                "departure_date": serializer.validated_data['departure_date'],
                "arrival_date": serializer.validated_data['arrival_date'],
                "payable_amount": serializer.validated_data['payble_amount'],
                "total_passengers": len(passengers),
            }

            # Render the HTML email template with context
            html_content = render_to_string('order_confirmation.html', {
                'company_logo_url': 'path/to/company-logo.png',
                'customer_email': customer_email,
                'flight_name': flight_details['flight_name'],
                'departure_iata': flight_details['departure_iata'],
                'arrival_iata': flight_details['arrival_iata'],
                'departure_date': flight_details['departure_date'],
                'arrival_date': flight_details['arrival_date'],
                'total_passengers': flight_details['total_passengers'],
                'payable_amount': flight_details['payable_amount'],
            })
            text_content = strip_tags(html_content)  # Convert HTML to plain text

            # Create email message
            email = EmailMultiAlternatives(
                subject="Flight Booking Confirmation",
                body=text_content,
                from_email="customerservice@valueutickets.com",
                to=[customer_email],
            )
            email.attach_alternative(html_content, "text/html")

            # Send the email
            email.send()

            return Response({
                "message": "Booking successful!"
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        booking_id = request.data.get('booking_id')
        
        if not email or not booking_id:
            return Response({"error": "Please provide both email and booking ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = Customer.objects.get(email=email)
            booking = FlightBooking.objects.get(booking_id=booking_id, customer=customer)
        except Customer.DoesNotExist:
            return Response({"error": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except FlightBooking.DoesNotExist:
            return Response({"error": "Booking does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FlightBookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

        


class FlightOnewayTrip(APIView):
    def post(self, request):
        serializer = FlightSearchSerializer(data=request.data)
        if serializer.is_valid():
            FLIGHT_KEY = os.getenv("FLIGHT_API_KEY")
            source = serializer.validated_data.get('source_iata')
            destination = serializer.validated_data.get('destination_iata')
            date = serializer.validated_data.get('date')
            adults = serializer.validated_data.get('adults')
            children = serializer.validated_data.get('children')
            infant = serializer.validated_data.get('infant')
            ticket_class = serializer.validated_data.get("ticket_class")

            api_url = f"https://api.flightapi.io/onewaytrip/{FLIGHT_KEY}/{source}/{destination}/{date}/{adults}/{children}/{infant}/{ticket_class}/USD"
            try:
                response = requests.get(api_url)
                response.raise_for_status()  # Raise an HTTPError for bad responses
            except requests.exceptions.HTTPError as http_err:
                return Response({"error": f"HTTP error occurred: {http_err}"}, status=response.status_code)
            except Exception as err:
                return Response({"error": f"An error occurred: {err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class CustomerResponseView(APIView):
    
    def get(self, request, booking_id, email_id, customer_response):
        booking = get_object_or_404(FlightBooking, booking_id=booking_id, customer__email=email_id)
        
        if customer_response == 'accept':
            booking.customer_approval_status = 'approved'
        elif customer_response == 'reject':
            booking.customer_approval_status = 'denied'
        else:
            return HttpResponse(f'HTTP_400_BAD_REQUEST | Permission Denied')
        
        booking.save()
        
        return HttpResponse(f'Booking changes {customer_response}ed successfully')