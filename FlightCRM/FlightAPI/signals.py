from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import FlightBooking
import random

@receiver(pre_save, sender=FlightBooking)
def generate_booking_id(sender, instance, **kwargs):
    if not instance.booking_id:
        last_booking = FlightBooking.objects.all().order_by('booking_id').last()
        if not last_booking:
            new_id = 2029000
        else:
            last_id = int(last_booking.booking_id[2:])
            new_id = last_id + 1
        instance.booking_id = f"VU{new_id}"
