from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
class Airport(models.Model):
    city = models.CharField(max_length=255)
    airport_name = models.CharField(max_length=255) 
    faa = models.CharField(max_length=3, blank=True, null=True)
    iata = models.CharField(max_length=3, blank=True, null=True)
    icao = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return self.airport_name



class Customer(models.Model):
    phone_number = models.CharField(max_length=15,unique=True,blank=False)
    email = models.EmailField(unique=True,blank=False)
    date = models.DateTimeField()

    def __str__(self):
        return self.email  # This will display the email address instead of the customer ID


class Passenger(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        # Format the full name with middle name only if it exists
        full_name = f"{self.first_name} {self.middle_name} {self.last_name}".replace("  ", " ")
        return f"{full_name} - {self.customer.email}"

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    card_number = models.CharField(max_length=16)
    card_expiry_month = models.IntegerField()
    card_expiry_year = models.IntegerField()
    cvv = models.IntegerField()
    cardholder_name = models.CharField(max_length=100)

    def __str__(self):
        return self.cardholder_name

class FlightBooking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    passengers = models.ManyToManyField(Passenger, related_name='flights')
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT,verbose_name="payment by")
    flight_cancellation_protection = models.BooleanField(default=False)
    sms_support = models.BooleanField(default=False)
    baggage_protection = models.BooleanField(default=False)
    premium_support = models.BooleanField(default=False)
    total_refund_protection = models.BooleanField(default=False)
    payble_amount = models.FloatField(verbose_name="Payable amt.($)")
    flight_name = models.CharField(max_length=200)
    departure_iata = models.CharField(max_length=4)
    arrival_iata = models.CharField(max_length=4)
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()
    agent = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user",default=1)
    def __str__(self):
        passenger_names = ', '.join([f"{p.first_name} {p.middle_name} {p.last_name}".replace("  ", " ") for p in self.passengers.all()])
        return f"{self.customer.email} - Passengers: {passenger_names}"
    

class Ticket(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets')
    pdf_file = models.FileField(upload_to='media/tickets/', help_text="Upload the PDF ticket for the customer.")
    message = models.TextField(blank=True, null=True, help_text="Optional message to be sent with the ticket.")

    def __str__(self):
        return f"Ticket for {self.customer.email} - {self.pdf_file.name}"

    class Meta:
        verbose_name = "Send Ticket"
        verbose_name_plural = "Send Tickets"

