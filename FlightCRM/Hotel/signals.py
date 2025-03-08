from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HotelBooking

@receiver(post_save, sender=HotelBooking)
def send_hotel_booking_confirmation_email(sender, instance, created, **kwargs):
    if created:  # Only send email for new bookings
        subject = "Hotel Booking Confirmation - Valueu Tickets"
        from_email = "customerservice@valueutickets.com"
        recipient_list = [instance.email]
        
        # Context for the email template
        context = {
            "customer_email": instance.email,
            "booking_id": instance.hotel_booking_id,
            "destination": instance.destination,
            "checkin_date": instance.checkin_datetime.strftime('%d-%m-%Y %H:%M'),
            "checkout_date": instance.checkout_datetime.strftime('%d-%m-%Y %H:%M'),
            "adults": instance.adults,
            "children": instance.children,
            "infants": instance.infants,
        }
        html_content = render_to_string('new_hotel_booking.html', context)
        email = EmailMultiAlternatives(
            subject=subject,
            from_email=from_email,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")

        # Send the email
        email.send()
