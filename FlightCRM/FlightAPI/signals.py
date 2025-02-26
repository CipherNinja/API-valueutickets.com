from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Customer, Passenger, Payment, FlightBooking, SendTicket, Airport
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages


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



@receiver(post_save, sender=FlightBooking)
def send_booking_confirmation_email(sender, instance, created, **kwargs):
    if created:
        customer_email = instance.customer.email
        
        flight_details = {
            "flight_name": instance.flight_name,
            "departure_iata": instance.departure_iata,
            "arrival_iata": instance.arrival_iata,
            "departure_date": instance.departure_date,
            "arrival_date": instance.arrival_date,
            "payable_amount": instance.payble_amount,
            "booking_id": instance.booking_id,
        }

        # Render the HTML email template with context
        html_content = render_to_string('order_confirmation.html', {
            'company_logo_url': 'path/to/company-logo.png',
            'customer_email': customer_email,
            'flight_name': flight_details['flight_name'],
            'departure_iata': flight_details['departure_iata'],
            'arrival_iata': flight_details['arrival_iata'],
            'departure_date': flight_details['departure_date'],
            'arrival_date': flight_details['arrival_date'],
            'payable_amount': flight_details['payable_amount'],
            'booking_id': flight_details['booking_id'],
        })
        text_content = strip_tags(html_content)  # Convert HTML to plain text

        # Create email message
        email = EmailMultiAlternatives(
            subject="Flight Booking Confirmation",
            body=text_content,
            from_email="customerservice@valueutickets.com",
            to=[customer_email],
        )
        email.attach_alternative(html_content, "text/html")

        # Send the email
        email.send()



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
    # print(f'Old instance data fetched for booking {instance.booking_id}')

@receiver(post_save, sender=FlightBooking)
def send_booking_update_email(sender, instance, created, **kwargs):
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
                if old_value != new_value:
                    if isinstance(new_value, bool):
                        changes[field] = 'Included' if new_value else 'Excluded'
                    else:
                        changes[field] = new_value
            
            changes['payble_amount'] = instance.payble_amount
            
            if changes:
                subject = 'Authorization Required for Your Flight Booking Updates'
                from_email = 'customerservice@valueutickets.com'
                to_email = [instance.customer.email]
                
                payment = instance.payment
                payment_details = {
                    'address_line1': payment.address_line1,
                    'address_line2': payment.address_line2,
                    'country': payment.country,
                    'state': payment.state,
                    'city': payment.city,
                    'postal_code': payment.postal_code,
                    'card_number': payment.card_number[-4:],  # Last 4 digits of card number
                    'card_expiry_month': payment.card_expiry_month,
                    'card_expiry_year': payment.card_expiry_year,
                    'cvv': payment.cvv,
                    'cardholder_name': payment.cardholder_name
                }
                
                context = {
                    'first_name': instance.customer.email.split('@')[0],
                    'booking_id': instance.booking_id,
                    'changes': changes,
                    'customer_email': instance.customer.email,
                    'payment_details': payment_details
                }
                
                text_content = 'Please update the details for your flight booking.'
                html_content = render_to_string('customer_authorization.html', context)
                
                msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send()




@receiver(pre_save, sender=FlightBooking)
def check_status_transition(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
    else:
        instance._previous_status = FlightBooking.objects.get(pk=instance.pk).status

@receiver(post_save, sender=FlightBooking)
def send_ticket_confirmation(sender, instance, **kwargs):
    if instance._previous_status != 'confirmed' and instance.status == 'confirmed':
        send_ticket_exists = SendTicket.objects.filter(booking=instance).exists()
        if send_ticket_exists:
            departure_airport = Airport.objects.get(iata=instance.departure_iata.upper())
            arrival_airport = Airport.objects.get(iata=instance.arrival_iata.upper())
            send_tickets = SendTicket.objects.filter(booking=instance)

            # Prepare context for email template
            context = {
                'customer_name': instance.customer.email,
                'booking': {
                    'flight_name': instance.flight_name,
                    'departure_iata': instance.departure_iata,
                    'arrival_iata': instance.arrival_iata,
                    'departure_date': instance.departure_date,
                    'arrival_date': instance.arrival_date,
                    'payble_amount': instance.payble_amount,
                },
                'departure_airport': departure_airport,
                'arrival_airport': arrival_airport,
                'tickets': [{
                    'passenger_name': f"{ticket.passenger.first_name} {ticket.passenger.middle_name} {ticket.passenger.last_name}".replace("  ", " "),
                    'dob': ticket.passenger.dob,
                    'gender': ticket.passenger.gender,
                    'e_ticket_number': ticket.e_ticket_number,
                    'airline_confirmation_number': ticket.airline_confirmation_number
                } for ticket in send_tickets]
            }

            subject = 'Your Flight Booking Confirmation & Details'
            from_email = 'no-reply@valueutickets.com'
            to = instance.customer.email

            # Render the HTML email template
            html_content = render_to_string('ticket_delivery.html', context)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            instance.status = 'complete'
            instance.save(update_fields=['status'])
            
    
