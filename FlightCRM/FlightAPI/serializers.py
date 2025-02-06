from rest_framework import serializers
from .models import Airport,Customer,FlightBooking,Passenger,Ticket,Payment

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



class FlightBookingCreateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    email = serializers.EmailField()
    date = serializers.DateTimeField()
    flight_name = serializers.CharField(max_length=200)
    departure_iata = serializers.CharField(max_length=4)
    arrival_iata = serializers.CharField(max_length=4)
    departure_date = serializers.DateTimeField()
    arrival_date = serializers.DateTimeField()
    passengers = serializers.ListField(
        child=serializers.DictField(), required=True
    )

    payment = serializers.DictField(required=True)

    flight_cancellation_protection = serializers.BooleanField(default=False)
    sms_support = serializers.BooleanField(default=False)
    baggage_protection = serializers.BooleanField(default=False)
    premium_support = serializers.BooleanField(default=False)
    total_refund_protection = serializers.BooleanField(default=False)
    payble_amount = serializers.FloatField(default=795)

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
            flight_cancellation_protection=validated_data['flight_cancellation_protection'],
            sms_support=validated_data['sms_support'],
            baggage_protection=validated_data['baggage_protection'],
            premium_support=validated_data['premium_support'],
            total_refund_protection=validated_data['total_refund_protection'],
            payble_amount=validated_data['payble_amount']
        )
        booking.passengers.set(passenger_instances)  # Link passengers to the booking

        return {
            "customer_id": customer.id,
            "booking_id": booking.id,
            "payment_id": payment.id,
            "passenger_ids": [p.id for p in passenger_instances],
        }
