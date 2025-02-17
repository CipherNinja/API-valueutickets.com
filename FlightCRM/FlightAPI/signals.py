from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import FlightBooking
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

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

# signals.py



@receiver(pre_save, sender=FlightBooking)
def check_agent_change(sender, instance, **kwargs):
    if instance.pk:
        previous_instance = FlightBooking.objects.get(pk=instance.pk)
        if previous_instance.agent != instance.agent:
            instance.agent_changed = True
        else:
            instance.agent_changed = False
    else:
        instance.agent_changed = False

@receiver(post_save, sender=FlightBooking)
def send_agent_assignment_email(sender, instance, created, **kwargs):
    if instance.agent_changed:
        agent = instance.agent
        agent_email = agent.email
        agent_first_name = agent.first_name
        agent_user_name = agent.username
        email_subject = 'New Customer Flight Booking'
        email_template_name = 'new_booking_assign.html'
        context = {
            'first_name': agent_first_name,
            'booking_id': instance.booking_id,
            'username': agent_user_name
        }
        
        # Render email content
        email_html_content = render_to_string(email_template_name, context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=email_subject,
            body='',
            from_email='',  # Replace with your sender email
            to=[agent_email],
        )

        # Attach the HTML version
        email.attach_alternative(email_html_content, "text/html")

        # Send the email
        email.send(fail_silently=False)