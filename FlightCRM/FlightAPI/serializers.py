from rest_framework import serializers
from .models import Airport,Customer,FlightBooking,Passenger,Ticket,Payment
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date

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

class FlightSearchRoundTrip(serializers.Serializer):
    source_iata = serializers.CharField(max_length=3)  # Departure Airport IATA
    destination_iata = serializers.CharField(max_length=3)  # Arrival Airport IATA
    outbound = serializers.DateField(format="%Y-%m-%d")  # Flight Date (YYYY-MM-DD)
    inbound = serializers.DateField(format="%Y-%m-%d")
    adults = serializers.IntegerField(min_value=1, max_value=9, default=1)  # Adult passengers (Default 1)
    children = serializers.IntegerField(min_value=0, max_value=9, default=0)  # Children (0-12 yrs)
    infants = serializers.IntegerField(min_value=0, max_value=9, default=0)  # Infants (0-2 yrs)
    ticket_class = serializers.ChoiceField(choices=["Economy", "Premium_Economy", "Business", "First"], default="Economy")

    def validate_ticket_class(self, value):
        valid_classes = ["Economy", "Premium_Economy", "Business", "First"]
        if value not in valid_classes:
            raise serializers.ValidationError("Invalid ticket class. Please choose from: Economy, Premium Economy, Business, First.")
        return value
    
    def validate(self, data):
        # Custom validation logic if needed
        if data['outbound'] >= data['inbound']:
            raise serializers.ValidationError("Return date must be after departure date.")
        return data

class FlightBookingCreateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15,required=True)
    email = serializers.EmailField(required=True)
    date = serializers.DateTimeField(required=True)
    flight_name = serializers.CharField(max_length=200,required=True)
    departure_iata = serializers.CharField(max_length=4,required=True)
    arrival_iata = serializers.CharField(max_length=4,required=True)
    departure_date = serializers.DateTimeField(required=True)
    arrival_date = serializers.DateTimeField(required=True)
    return_departure_iata = serializers.CharField(max_length=4, required=False, allow_null=True, allow_blank=True)
    return_arrival_iata = serializers.CharField(max_length=4, required=False, allow_null=True, allow_blank=True)
    return_departure_date = serializers.DateTimeField(required=False, allow_null=True)
    return_arrival_date = serializers.DateTimeField(required=False, allow_null=True)
    passengers = serializers.ListField(
        child=serializers.DictField(), required=True
    )

    payment = serializers.DictField(required=True)

    flight_cancellation_protection = serializers.BooleanField(default=False)
    sms_support = serializers.BooleanField(default=False)
    baggage_protection = serializers.BooleanField(default=False)
    premium_support = serializers.BooleanField(default=False)
    total_refund_protection = serializers.BooleanField(default=False)
    payble_amount = serializers.FloatField(required=True)

    def create(self, validated_data):
        """
        Create customer, passengers, payment, and flight booking in one transaction.
        """
        # Create or get the Customer
        customer, created = Customer.objects.get_or_create(
            email=validated_data['email'],
            defaults={
                'phone_number': validated_data['phone_number'],
                'date': validated_data['date']
            }
        )

        # Create Passengers
        passenger_instances = []
        for passenger_data in validated_data['passengers']:
            passenger_instances.append(Passenger.objects.create(customer=customer, **passenger_data))

        # Create Payment
        payment_data = validated_data['payment']
        payment = Payment.objects.create(customer=customer, **payment_data)

        # Create Flight Booking
        booking = FlightBooking.objects.create(
            customer=customer,
            payment=payment,
            flight_name=validated_data['flight_name'],
            departure_iata=validated_data['departure_iata'],
            arrival_iata=validated_data['arrival_iata'],
            departure_date=validated_data['departure_date'],
            arrival_date=validated_data['arrival_date'],
            return_departure_iata=validated_data.get('return_departure_iata', None),
            return_arrival_iata=validated_data.get('return_arrival_iata', None),
            return_departure_date=validated_data.get('return_departure_date', None),
            return_arrival_date=validated_data.get('return_arrival_date', None),
            flight_cancellation_protection=validated_data['flight_cancellation_protection'],
            sms_support=validated_data['sms_support'],
            baggage_protection=validated_data['baggage_protection'],
            premium_support=validated_data['premium_support'],
            total_refund_protection=validated_data['total_refund_protection'],
            payble_amount=validated_data['payble_amount']
        )
        booking.passengers.set(passenger_instances)  # Link passengers to the booking
        booking.save()
        return {
            "customer_id": customer.id,
            "booking_id": booking.id,
            "payment_id": payment.id,
            "passenger_ids": [p.id for p in passenger_instances],
        }



class PassengerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    ticket_details = serializers.SerializerMethodField()  # New field for ticket information

    class Meta:
        model = Passenger
        fields = ['name', 'dob', 'gender', 'age', 'ticket_details']  # Added 'ticket_details'

    def get_name(self, obj):
        return f"{obj.first_name} {obj.middle_name} {obj.last_name}".replace("  ", " ")

    def get_age(self, obj):
        today = date.today()
        return today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))

    def get_ticket_details(self, obj):
        # Fetch the related ticket details if available
        try:
            ticket = obj.tickets.first()  # Assuming each passenger has one ticket
            if ticket:
                return {
                    "e_ticket_number": ticket.e_ticket_number,
                    "airline_confirmation_number": ticket.airline_confirmation_number
                }
        except Exception:
            pass
        return None  # If no ticket data exists


class PaymentSerializer(serializers.ModelSerializer):
    card_number_last4 = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['cardholder_name', 'card_number_last4']

    def get_card_number_last4(self, obj):
        return obj.card_number[-4:]

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['email', 'phone_number']

class FlightBookingSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(many=True, source='passengers')
    contact_billings = serializers.SerializerMethodField()
    orderings = serializers.SerializerMethodField()
    return_flight = serializers.SerializerMethodField()  # Added for return flight data
    TicketStatus = serializers.SerializerMethodField()  # Added for Ticket Status

    class Meta:
        model = FlightBooking
        fields = [
            'flight_name', 
            'departure_iata', 
            'arrival_iata', 
            'departure_date', 
            'arrival_date', 
            'return_flight',  # New field
            'passenger', 
            'contact_billings', 
            'orderings', 
            'TicketStatus'  # New field
        ]

    def get_contact_billings(self, obj):
        customer = obj.customer
        payment = obj.payment
        return {
            "Email": customer.email,
            "phone_number": customer.phone_number,
            "cardholder_name": payment.cardholder_name,
            "card_number": payment.card_number[-4:]
        }

    def get_orderings(self, obj):
        return {
            "payble_amount": obj.payble_amount,
            "flight_cancellation_protection": 15 if obj.flight_cancellation_protection else 0,
            "sms_support": 2 if obj.sms_support else 0,
            "baggage_protection": 15 if obj.baggage_protection else 0,
            "premium_support": 5 if obj.premium_support else 0,
            "total_refund_protection": 100 if obj.total_refund_protection else 0,
            "total_amount": obj.payble_amount + (15 if obj.flight_cancellation_protection else 0) + 
                             (2 if obj.sms_support else 0) + (15 if obj.baggage_protection else 0) + 
                             (5 if obj.premium_support else 0) + (100 if obj.total_refund_protection else 0)
        }

    def get_return_flight(self, obj):
        # Check if return flight data exists, otherwise return None
        if obj.return_departure_iata and obj.return_arrival_iata and obj.return_departure_date and obj.return_arrival_date:
            return {
                "return_departure_iata": obj.return_departure_iata,
                "return_arrival_iata": obj.return_arrival_iata,
                "return_departure_date": obj.return_departure_date,
                "return_arrival_date": obj.return_arrival_date
            }
        return None

    def get_TicketStatus(self, obj):
        # Check the status and return the TicketStatus value
        if obj.status.lower() in ['confirmed']:
            return "Confirmed"
        elif obj.status.lower() in ['cancelled']:
            return "Cancelled"
        else:
            return "Pending"
