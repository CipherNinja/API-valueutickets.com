from rest_framework import serializers
from .models import Airport,Customer,FlightBooking,Passenger,Payment
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
    flight_name = serializers.CharField(max_length=200, required=True)
    departure_iata = serializers.CharField(max_length=4, required=True)
    arrival_iata = serializers.CharField(max_length=4, required=True)
    departure_date = serializers.DateTimeField(required=True)
    arrival_date = serializers.DateTimeField(required=True)
    return_departure_iata = serializers.CharField(max_length=4, required=False, allow_null=True, allow_blank=True)
    return_arrival_iata = serializers.CharField(max_length=4, required=False, allow_null=True, allow_blank=True)
    return_departure_date = serializers.DateTimeField(required=False, allow_null=True)
    return_arrival_date = serializers.DateTimeField(required=False, allow_null=True)
    passenger = serializers.ListField(
        child=serializers.DictField(), required=True
    )
    contact_billings = serializers.DictField(required=True)
    orderings = serializers.DictField(required=True)

    def create(self, validated_data):
        """
        Parse and create customer, passengers, and flight booking records with return flight data.
        """
        # Step 1: Extract and handle contact details
        contact_details = validated_data['contact_billings']
        # Step 1: Create a new customer (not using get_or_create)
        customer = Customer.objects.create(
            email=contact_details['Email'],
            phone_number=contact_details['phone_number']
        )


        # Step 2: Create passengers linked to the customer
        passenger_instances = []
        for passenger_data in validated_data['passenger']:
            passenger_instances.append(Passenger.objects.create(customer=customer, **passenger_data))

        # Step 3: Handle orderings and create the flight booking
        orderings = validated_data['orderings']
        booking = FlightBooking.objects.create(
            customer=customer,
            flight_name=validated_data['flight_name'],
            departure_iata=validated_data['departure_iata'],
            arrival_iata=validated_data['arrival_iata'],
            departure_date=validated_data['departure_date'],
            arrival_date=validated_data['arrival_date'],
            return_departure_iata=validated_data.get('return_departure_iata', None),
            return_arrival_iata=validated_data.get('return_arrival_iata', None),
            return_departure_date=validated_data.get('return_departure_date', None),
            return_arrival_date=validated_data.get('return_arrival_date', None),
            payble_amount=orderings['payble_amount'],
            flight_cancellation_protection=bool(orderings.get('flight_cancellation_protection', 0)),
            sms_support=bool(orderings.get('sms_support', 0)),
            baggage_protection=bool(orderings.get('baggage_protection', 0)),
            premium_support=bool(orderings.get('premium_support', 0)),
            total_refund_protection=bool(orderings.get('total_refund_protection', 0)),
        )

        # Step 4: Return Results
        return {
            "customer_id": customer.id,
            "booking_id": booking.id,
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
    passenger = serializers.SerializerMethodField()  # Passenger details including ticket details
    contact_billings = serializers.SerializerMethodField()
    orderings = serializers.SerializerMethodField()
    return_flight = serializers.SerializerMethodField()
    TicketStatus = serializers.SerializerMethodField()
    flight_data = serializers.SerializerMethodField()

    class Meta:
        model = FlightBooking
        fields = [
            'flight_name',
            'departure_iata',
            'arrival_iata',
            'departure_date',
            'arrival_date',
            'return_flight',
            'passenger',
            'contact_billings',
            'orderings',
            'TicketStatus',
            'flight_data'
        ]

    def to_representation(self, instance):
        """
        Dynamically adjust the output based on pnr_decoded_data availability.
        If pnr_decoded_data exists, exclude one-way and round-trip flight details.
        Also remove fields with null values.
        """
        representation = super().to_representation(instance)
        
        # Check if pnr_decoded_data is available and not empty
        if instance.pnr_decoded_data and instance.pnr_decoded_data.strip():
            # Remove one-way and round-trip flight details if pnr_decoded_data exists
            fields_to_exclude = [
                'flight_name',
                'departure_iata',
                'arrival_iata',
                'departure_date',
                'arrival_date',
                'return_flight'
            ]
            for field in fields_to_exclude:
                representation.pop(field, None)
        
        # Remove keys where the value is null
        return {key: value for key, value in representation.items() if value is not None}

    def get_passenger(self, obj):
        # Retrieve passenger details including ticket information
        passengers = obj.customer.passengers.all()
        passenger_list = []
        for passenger in passengers:
            passenger_list.append({
                "name": f"{passenger.first_name} {passenger.middle_name or ''} {passenger.last_name}".strip(),
                "dob": passenger.dob,
                "gender": passenger.gender,
                "age": self.calculate_age(passenger.dob),
                "ticket_details": {
                    "e_ticket_number": passenger.e_ticket_number,
                    "airline_confirmation_number": passenger.airline_confirmation_number
                } if passenger.e_ticket_number or passenger.airline_confirmation_number else None
            })
        return passenger_list

    def calculate_age(self, dob):
        # Helper method to calculate age from date of birth
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def get_contact_billings(self, obj):
        customer = obj.customer
        payment = customer.payments.first()
        if payment:
            return {
                "Email": customer.email,
                "phone_number": customer.phone_number,
                "cardholder_name": payment.cardholder_name,
                "card_number": payment.card_number[-4:]
            }
        return {
            "Email": customer.email,
            "phone_number": customer.phone_number,
            "cardholder_name": None,
            "card_number": None
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
        if obj.return_departure_iata and obj.return_arrival_iata and obj.return_departure_date and obj.return_arrival_date:
            return {
                "return_departure_iata": obj.return_departure_iata,
                "return_arrival_iata": obj.return_arrival_iata,
                "return_departure_date": obj.return_departure_date,
                "return_arrival_date": obj.return_arrival_date
            }
        return None

    def get_TicketStatus(self, obj):
        status_mapping = {
            'send ticket confirmed mail': "Confirmed",
            'send ticket cancelled mail': "Cancelled",
            'send flight information mail': "Pending"
        }
        return status_mapping.get(obj.status.lower(), "Pending")

    def get_flight_data(self, obj):
        # Return pnr_decoded_data if it exists, otherwise None
        if obj.pnr_decoded_data and obj.pnr_decoded_data.strip():
            return obj.pnr_decoded_data
        return None