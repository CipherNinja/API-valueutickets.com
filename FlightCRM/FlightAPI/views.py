from django.shortcuts import render
from rest_framework import viewsets
from .serializers import AirportSerializer, FlightSearchSerializer,FlightBookingCreateSerializer,FlightBookingSerializer,FlightSearchRoundTrip
from .models import Airport,Customer,FlightBooking,Passenger,Payment
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import requests
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils.timezone import now

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
            saved_data = serializer.save()
            return Response({
                "message": "Booking successful!",
                "booking_data":[saved_data]
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        booking_id = request.data.get('booking_id')
        
        if not email or not booking_id:
            return Response(
                {"error": "Email and Booking ID are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Fetch the booking by booking_id and match its customer with the email
            booking = FlightBooking.objects.get(booking_id=booking_id, customer__email=email)
        except FlightBooking.DoesNotExist:
            return Response(
                {"error": "No booking found for the provided Booking ID and email."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Serialize the booking details
        serializer = FlightBookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)


        

FLIGHT_KEY = os.getenv("FLIGHT_API_KEY")
class FlightOnewayTrip(APIView):
    def post(self, request):
        serializer = FlightSearchSerializer(data=request.data)
        if serializer.is_valid():
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

     
class FlightRoundTrip(APIView):
    def post(self, request):
        serializer = FlightSearchRoundTrip(data=request.data)
        if serializer.is_valid():
            source = serializer.validated_data.get('source_iata')
            destination = serializer.validated_data.get('destination_iata')
            outbound = serializer.validated_data.get('outbound')
            inbound = serializer.validated_data.get('inbound')
            adults = serializer.validated_data.get('adults')
            children = serializer.validated_data.get('children')
            infants = serializer.validated_data.get('infants')
            ticket_class = serializer.validated_data.get('ticket_class')

            api_url = f"https://api.flightapi.io/roundtrip/{FLIGHT_KEY}/{source}/{destination}/{outbound}/{inbound}/{adults}/{children}/{infants}/{ticket_class}/USD"
            try:
                response = requests.get(api_url)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                return Response({"error": f"HTTP error occurred: {http_err}"}, status=response.status_code)
            except Exception as err:
                return Response({"error": f"An error occurred: {err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if response.status_code == 200:
                data = response.json()
                
                carrier_map = {carrier["id"]: carrier["name"] for carrier in data.get("carriers", [])}
                
                legs_map = {leg["id"]: leg for leg in data.get("legs", [])}
                
                flight_details = []
                for itinerary in data.get("itineraries", []):
                    total_price = itinerary.get("pricing_options", [{}])[0].get("price", {}).get("amount", "Unknown")
                    legs = []
                    for index, leg_id in enumerate(itinerary.get("leg_ids", [])):
                        leg_details = legs_map.get(leg_id, {})
                        departure = leg_details.get("departure", "Unknown")
                        arrival = leg_details.get("arrival", "Unknown")
                        duration = leg_details.get("duration", "Unknown")
                        stop_count = leg_details.get("stop_count", "Unknown")
                        marketing_carrier_id = leg_details.get("marketing_carrier_ids", [None])[0]
                        flight_name = carrier_map.get(marketing_carrier_id, "Unknown")
                        leg_type = "Outbound" if index == 0 else "Inbound"
                        
                        legs.append({
                            "leg_type": leg_type,
                            "flight_name": flight_name,
                            "departure": departure,
                            "arrival": arrival,
                            "duration": duration,
                            "stop_count": stop_count
                        })
                    
                    flight_details.append({
                        "legs": legs,
                        "total_price": total_price
                    })
                
                return Response(flight_details, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to fetch flight data"}, status=response.status_code)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_authentication_email(booking, message):
    """
    Sends an email acknowledgment for customer authentication response.
    """
    # Fetch the associated customer and payment
    customer = booking.customer
    payment = customer.payments.first()  # Assuming the first payment is used for this purpose
    
    # Prepare email data
    email_data = {
        'booking_number': booking.booking_id,
        'auth_status': booking.customer_approval_status.capitalize(),
        'acknowledge_date': booking.customer_approval_datetime.strftime('%b, %d %Y %H:%M:%S') if booking.customer_approval_datetime else 'N/A',
        'total_amount': f"USD ${booking.payble_amount}" if booking.payble_amount else 'N/A',
        'card_holder_name': payment.cardholder_name if payment else 'N/A',
        'card_ending': payment.card_number[-4:] if payment else 'N/A',
        'customer_email': customer.email,
        'pf_number': booking.customer_ip if booking.customer_ip else 'N/A',
        'authorization_text': (
            f"I {payment.cardholder_name if payment else 'the cardholder'} hereby authorize ValueU Tickets./ Air Tickets / Airlines and associated suppliers "
            f"to charge a total of USD ${booking.payble_amount if booking.payble_amount else '0.00'} from my card ending with \"{payment.card_number[-4:] if payment else 'N/A'}\"."
        ),
        'ticket_issuance': 'Ticket will be issued in 4-5 hrs.',
        'response_message': message, 
    }
    
    # Render HTML email content
    html_message = render_to_string('authentication_acknowledgement.html', email_data)
    subject = f"Authentication Acknowledgment - {booking.customer_approval_status.capitalize()} - Valueu Tickets"
    from_email = 'customerservice@valueutickets.com'
    to_email = 'customerservice@valueutickets.com'

    # Send the email
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=[to_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
    except Exception as e:
        # Log email sending errors
        print(f"Failed to send email: {e}")


class CustomerResponseView(APIView):

    def get(self, request, booking_id, email_id, customer_response):
        booking = get_object_or_404(FlightBooking, booking_id=booking_id, customer__email=email_id)
        
        # Retrieve client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
        
        if booking.customer_approval_status in ['approved', 'denied']:
            message = 'Link is Expired !'
            return render(request, 'customerResponse.html', {'message': message})

        if customer_response == 'accept':
            booking.customer_approval_status = 'approved'
            booking.customer_approval_datetime = now()
            booking.customer_ip = ip
            message = 'Authenticated Successfully'
        elif customer_response == 'reject':
            booking.customer_approval_status = 'denied'
            booking.customer_approval_datetime = now()
            booking.customer_ip = ip
            message = 'Authentication Rejected'
        else:
            message = 'Invalid Request & Permission Denied'
            return render(request, 'customerResponse.html', {'message': message})

        # Set a flag to indicate that the signal should skip sending emails
        booking._skip_signal_emails = True
        booking.save()

        # Send the acknowledgment email
        print(f"Authetication Reply: Payment Auth email Initiated for {booking.booking_id}")
        send_authentication_email(booking, message)
        print(f"Authetication Reply: Payment Auth email sent for {booking.booking_id}")

        return render(request, 'customerResponse.html', {'message': message})


def custom_404_view(request, exception):
    return render(request, 'Errors/404_Not_Found.html', status=404)

def custom_500_view(request):
    return render(request, 'Errors/500.html', status=500)

def custom_403_view(request, exception):
    return render(request, 'Errors/403.html', status=403)

def custom_400_view(request, exception):
    return render(request, 'Errors/400_Bad_Request.html', status=400)


from django.db.models import Count, Q

@staff_member_required
def admin_dashboard(request):
    # Determine the agent filter based on the logged-in user
    if request.user.is_superuser:
        agent_filter = {}  # Superusers see all data
    else:
        agent_filter = {'agent': request.user}  # Agents see only their data

    # Total bookings assigned to the agent
    total_bookings = FlightBooking.objects.filter(**agent_filter).count()

    # Confirmed bookings (status: 'send ticket confirmed mail' or 'booking completed ticket not sent')
    confirmed_bookings = FlightBooking.objects.filter(
        Q(status__in=['send ticket confirmed mail', 'booking completed ticket not sent']),
        **agent_filter
    )
    confirmed_count = confirmed_bookings.count()

    # Bookings on hold (status: 'booking incompleted email not sent')
    bookings_on_hold = FlightBooking.objects.filter(
        status='booking incompleted email not sent',
        **agent_filter
    ).count()

    # META Net MCO: Sum of net_mco for confirmed bookings
    meta_net_mco = 0
    for booking in confirmed_bookings:
        if booking.net_mco and booking.net_mco.replace('.', '', 1).lstrip('-').isdigit():
            meta_net_mco += float(booking.net_mco)

    # PPC Net MCO (static as per requirement)
    ppc_net_mco = 0

    total_net_mco = meta_net_mco

    # META MCO: Sum of mco for confirmed bookings
    meta_mco = 0
    for booking in confirmed_bookings:
        if booking.mco and booking.mco.replace('.', '', 1).lstrip('-').isdigit():
            meta_mco += float(booking.mco)

    # PPC MCO (static as per requirement)
    ppc_mco = 0

    # Total MCO: Sum of mco for confirmed bookings (same as meta_mco since ppc_mco is 0)
    total_mco = meta_mco

    # Agent Performance Data (for graph and table)
    agent_performance = User.objects.filter(
        user__isnull=False,  # Using the correct reverse relation 'user'
        **({} if request.user.is_superuser else {'id': request.user.id})
    ).annotate(
        confirmed_count=Count('user', filter=Q(
            user__status__in=['send ticket confirmed mail', 'booking completed ticket not sent']
        ))
    ).values('username', 'confirmed_count')

    # Manually calculate total_mco for each agent since mco is a CharField
    agent_performance_list = []
    for agent in agent_performance:
        agent_bookings = FlightBooking.objects.filter(
            agent__username=agent['username'],
            status__in=['send ticket confirmed mail', 'booking completed ticket not sent']
        )
        total_mco = 0
        for booking in agent_bookings:
            if booking.mco and booking.mco.replace('.', '', 1).lstrip('-').isdigit():
                total_mco += float(booking.mco)
        agent_performance_list.append({
            'username': agent['username'],
            'total_mco': total_mco,
            'confirmed_count': agent['confirmed_count']
        })

    # Prepare data for the graph (agent names and MCOs)
    agent_names = [agent['username'] for agent in agent_performance_list]
    agent_mcos = [float(agent['total_mco']) for agent in agent_performance_list]

    context = {
        "title": "Dashboard",
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_count,
        "bookings_on_hold": bookings_on_hold,
        "meta_net_mco": meta_net_mco,
        "ppc_net_mco": ppc_net_mco,
        "total_net_mco": total_net_mco,
        "meta_mco": meta_mco,
        "ppc_mco": ppc_mco,
        "total_mco": total_mco,
        "agent_performance": agent_performance_list,
        "agent_names": agent_names,
        "agent_mcos": agent_mcos,
    }
    return render(request, "admin/dashboard.html", context)