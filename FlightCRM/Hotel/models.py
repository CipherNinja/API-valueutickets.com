from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.timezone import now
class HotelBooking(models.Model):
    hotel_booking_id = models.CharField(max_length=15, unique=True, editable=False)  # Unique booking ID
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?[1-9]\d{1,14}$',
                message="Enter a valid international phone number with country code."
            )
        ]
    )
    email = models.EmailField()
    checkin_datetime = models.DateTimeField()
    checkout_datetime = models.DateTimeField()
    adults = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    children = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    infants = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    destination = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.hotel_booking_id:
            last_booking = HotelBooking.objects.all().order_by('-id').first()
            if last_booking and last_booking.hotel_booking_id.startswith("HTL"):
                last_number = int(last_booking.hotel_booking_id[3:])
                self.hotel_booking_id = f"HTL{last_number + 1}"
            else:
                self.hotel_booking_id = "HTL2029000"  # Starting ID
        super().save(*args, **kwargs)

    def clean(self):
        if self.checkin_datetime and self.checkout_datetime:
            if self.checkout_datetime <= self.checkin_datetime:
                raise ValidationError("Checkout must be after check-in.")
        if self.checkin_datetime and self.checkin_datetime < now():
            raise ValidationError("Check-in date cannot be in the past.")

    def __str__(self):
        return f"Booking at {self.destination} by {self.email}"

    class Meta:
        ordering = ['checkin_datetime']
