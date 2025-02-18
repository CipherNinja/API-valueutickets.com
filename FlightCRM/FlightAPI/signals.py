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


@receiver(pre_save, sender=FlightBooking)
def get_old_flight_booking_data(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_instance = FlightBooking.objects.get(pk=instance.pk)
    instance._old_instance = old_instance
    print(f'Old instance data fetched for booking {instance.booking_id}')

@receiver(post_save, sender=FlightBooking)
def send_booking_update_email(sender, instance, created, **kwargs):
    print(f'Post save signal triggered for booking {instance.booking_id} with status {instance.status}')
    if instance.status == 'c.auth request':
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            changes = {}
            fields_to_check = [
                'flight_cancellation_protection', 'sms_support', 'baggage_protection', 
                'premium_support', 'total_refund_protection', 'payble_amount', 
                'flight_name', 'departure_iata', 'arrival_iata', 'departure_date', 
                'arrival_date'
            ]

            for field in fields_to_check:
                old_value = getattr(old_instance, field)
                new_value = getattr(instance, field)
                print(f'Checking field: {field}, Old value: {old_value}, New value: {new_value}')  # Debug print statement
                if old_value != new_value:
                    if isinstance(new_value, bool):
                        changes[field] = 'Included' if new_value else 'Excluded'
                    else:
                        changes[field] = new_value
            print(f'Changes detected: {changes}')
            
            if changes:
                print('Preparing to send email')
                subject = 'Authorization Required for Your Flight Booking Updates'
                from_email = 'customerservice@valueutickets.com'
                to_email = [instance.customer.email]
                
                context = {
                    'first_name': instance.customer.email.split('@')[0],
                    'booking_id': instance.booking_id,
                    'changes': changes,
                    'customer_email': instance.customer.email
                }
                
                text_content = 'Please update the details for your flight booking.'
                html_content = render_to_string('customer_authorization.html', context)
                print(f'HTML content: {html_content}')
                
                msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                print('Email sent successfully')
