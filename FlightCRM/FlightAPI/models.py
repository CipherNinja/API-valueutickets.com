from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date

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

    def get_age(self):
        today = date.today()
        age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        if age < 1:
            months = (today.year - self.dob.year) * 12 + today.month - self.dob.month
            if today.day < self.dob.day:
                months -= 1
            return f"{months} months"
        return f"{age} years"

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

    def clean(self):
        # Validate card number length
        if len(self.card_number) != 16:
            raise ValidationError(_('Card number must be exactly 16 digits long.'))
        
        # Validate card expiry year format
        if len(str(self.card_expiry_year)) != 4:
            raise ValidationErr̥r̥ror(_('Card expiry year must be a 4-digit number Example: 2024, 2030, etc.'))
        
        # Validate card expiry month
        if self.card_expiry_month < 1 or self.card_expiry_month > 12:
            raise ValidationError(_('Card expiry month must be between 1 and 12.'))
        
        # Validate card expiry date
        current_year = datetime.now().year
        current_month = datetime.now().month
        if self.card_expiry_year < current_year or (self.card_expiry_year == current_year and self.card_expiry_month < current_month):
            raise ValidationError(_('Card expiry date must be in the future.'))
        
        # Validate CVV length
        if len(str(self.cvv)) not in [3, 4]:
            raise ValidationError(_('CVV must be either 3 or 4 digits long.'))
        
        # Validate postal code length (you can adjust this based on specific country's format)
        if len(self.postal_code) < 5 or len(self.postal_code) > 10:
            raise ValidationError(_('Postal code must be between 5 and 10 characters long.'))

    def save(self, *args, **kwargs):
        self.clean()
        super(Payment, self).save(*args, **kwargs)


class FlightBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('c.auth request', 'C.Auth Request'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('refunded', 'Refunded'),
        ('rebooked', 'Rebooked'),
        ('failed', 'Failed'),
    ]
    booking_id = models.CharField(max_length=12, unique=True, blank=True)
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # update_customer_about_changes = models.BooleanField(default=False)
    customer_approval_status = models.CharField(max_length=20,choices=[('approved','Approved'),('denied','Denied'),("na","NA")],default='na')

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

