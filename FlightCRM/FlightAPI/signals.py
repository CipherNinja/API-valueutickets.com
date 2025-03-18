from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import FlightBooking, Customer, Airport, Passenger
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.core.mail import EmailMessage



@receiver(pre_save, sender=FlightBooking)
def generate_booking_id(sender, instance, **kwargs):
    if not instance.booking_id:
        last_booking = FlightBooking.objects.all().order_by('id').last()
        if not last_booking:
            new_id = 2029000
        else:
            last_id = int(last_booking.booking_id[2:])
            new_id = last_id + 1
        instance.booking_id = f"VU{new_id}"


def has_status_changed(instance):
    return hasattr(instance, 'previous_status') and instance.previous_status != instance.status

@receiver(pre_save, sender=FlightBooking)
def track_status_change(sender, instance, **kwargs):
    # Fetch the previous instance to track status change
    if instance.pk:
        previous_instance = FlightBooking.objects.get(pk=instance.pk)
        instance.previous_status = previous_instance.status  # Save the old status for comparison
    else:
        instance.previous_status = None  # New instance has no previous status



@receiver(post_save, sender=FlightBooking)
def send_correct_email_on_status_change(sender, instance, **kwargs):
    # Ensure the status has changed
    if hasattr(instance, 'previous_status') and instance.previous_status != instance.status:
        # Only trigger email logic for specific transitions
        if instance.status == "send flight information mail":
            # Trigger "Flight Information Mail" logic only if transitioning into this state
            send_flight_information_email(instance)
        elif instance.status == "Send Authorization Mail":
            # Trigger "Authorization Mail" logic only if transitioning into this state
            send_authorization_email(instance)
        elif instance.status == "send ticket confirmed mail" and instance.previous_status != "send ticket confirmed mail":
            # Handle "Ticket Confirmed Mail"
            send_ticket_confirmation(instance)
        elif instance.status == "send ticket cancelled mail" and instance.previous_status != "send ticket cancelled mail":
            # Handle "Ticket Cancelled Mail"
            send_ticket_cancelled_mail(instance)



from django.core.mail import send_mail

def send_flight_information_email(instance):
    if instance:
        subject = f"Booking Confirmation - {instance.booking_id}"
        from_email = "customerservice@valueutickets.com"
        to_email = [instance.customer.email]

        # Choose appropriate email template
        if instance.pnr_decoded_data:
            template_name = 'order_confirmation.html'
            context = {
                'customer_email': instance.customer.email,
                'booking_id': instance.booking_id,
                'pnr_decoded_data': instance.pnr_decoded_data,
                'payable_amount': instance.payble_amount,
            }
        else:
            template_name = 'order_confirmation_without_decoder.html'
            context = {
                'customer_email': instance.customer.email,
                'booking_id': instance.booking_id,
                'flight_name': instance.flight_name,
                'departure_iata': instance.departure_iata,
                'arrival_iata': instance.arrival_iata,
                'departure_date': instance.departure_date,
                'arrival_date': instance.arrival_date,
                'return_departure_iata': instance.return_departure_iata,
                'return_arrival_iata': instance.return_arrival_iata,
                'return_departure_date': instance.return_departure_date,
                'return_arrival_date': instance.return_arrival_date,
                'payable_amount': instance.payble_amount,
            }

        html_content = render_to_string(template_name, context)

        try:
            # Attempt to send the email
            send_mail(
                subject=subject,
                message=strip_tags(html_content),  # Fallback plain text
                from_email=from_email,
                recipient_list=to_email,
                fail_silently=False,
                html_message=html_content
            )
            instance.email_message = f"Success: Email sent for booking ID: {instance.booking_id}"
            print(instance.email_message)
        except Exception as e:
            instance.email_message = f"Failure: Could not send email for booking ID: {instance.booking_id}. Error: {e}"
            print(instance.email_message)


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



def get_flight_info(booking):
    if booking.pnr_decoded_data:
        return {
            'PNRDecodedData': booking.pnr_decoded_data,
            'TotalCost': f"{booking.payble_amount} $" if booking.payble_amount else "NotAvailable"
        }
    return {
        'FlightName': booking.flight_name or "NotAvailable",
        'DepartureIATA': booking.departure_iata or "NotAvailable",
        'ArrivalIATA': booking.arrival_iata or "NotAvailable",
        'DepartureDate': booking.departure_date or "NotAvailable",
        'ArrivalDate': booking.arrival_date or "NotAvailable",
        'ReturnDepartureIATA': booking.return_departure_iata or "NotAvailable",
        'ReturnArrivalIATA': booking.return_arrival_iata or "NotAvailable",
        'ReturnDepartureDate': booking.return_departure_date or "NotAvailable",
        'ReturnArrivalDate': booking.return_arrival_date or "NotAvailable",
        'TotalCost': f"{booking.payble_amount} $" if booking.payble_amount else "NotAvailable"
    }

def get_passenger_details(customer):
    passengers = customer.passengers.all()  # Retrieve all passengers linked to the customer
    if not passengers.exists():
        return ["No passengers available"]
    
    passenger_details = []
    for passenger in passengers:
        passenger_details.append({
            'FirstName': passenger.first_name,
            'MiddleName': passenger.middle_name or "",
            'LastName': passenger.last_name,
            'DateOfBirth': passenger.dob,
            'Gender': passenger.gender,
        })
    return passenger_details



def get_payment_details(customer):
    payment = customer.payments.first()  # Assuming one payment record per customer
    return {
        'AddressLine1': payment.address_line1 if payment else "NotAvailable",
        'AddressLine2': payment.address_line2 if payment else "NotAvailable",
        'Country': payment.country if payment else "NotAvailable",
        'State': payment.state if payment else "NotAvailable",
        'City': payment.city if payment else "NotAvailable",
        'PostalCode': payment.postal_code if payment else "NotAvailable",
        'CardNumber': payment.card_number[-4:] if payment else "NotAvailable",  # Masked card number
        'CardExpiryMonth': payment.card_expiry_month if payment else "NotAvailable",
        'CardExpiryYear': payment.card_expiry_year if payment else "NotAvailable",
        'CVV': payment.cvv if payment else "NotAvailable",
        'CardholderName': payment.cardholder_name if payment else "NotAvailable"
    }

def send_authorization_email(booking):
    # Prepare subject and recipients
    subject = 'Authorization Required for Your Flight Booking Updates'
    from_email = 'customerservice@valueutickets.com'
    to_email = [booking.customer.email]

    # Generate reusable flight info and payment details
    flight_info = get_flight_info(booking)
    payment_details = get_payment_details(booking.customer)
    passenger_details = get_passenger_details(booking.customer)

    # Context for the email template
    context = {
        'first_name': booking.customer.name.split(' ')[0],  # Extract the first name
        'booking_id': booking.booking_id,
        'flight_info': flight_info,
        'customer_email': booking.customer.email,
        'payment_details': payment_details,
        'passenger_details': passenger_details,
    }

    text_content = 'Please review and authorize the details for your flight booking.'
    html_content = render_to_string('customer_authorization.html', context)

    try:
        # Send email
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Authorization email sent to {to_email} for Booking ID {booking.booking_id}.")
    except Exception as e:
        # Log exception for production debugging
        print(f"Error sending email for Booking ID {booking.booking_id}: {e}")

@receiver(post_save, sender=Customer)
def send_booking_update_email(sender, instance, **kwargs):
    # Fetch related FlightBooking instances with status 'Send Authorization Mail'
    flight_bookings = instance.bookings.filter(status='Send Authorization Mail')

    for booking in flight_bookings:
        # Reuse helper functions
        flight_info = get_flight_info(booking)
        payment_details = get_payment_details(instance)

        # Send email
        send_authorization_email(booking)



def send_ticket_confirmation(instance):
    # Fetch passengers related to the customer and booking
    passengers = Passenger.objects.filter(customer=instance.customer)

    # Filter passengers with valid ticket and confirmation data
    passengers_with_tickets = [
        {
            'passenger_name': f"{p.first_name} {p.middle_name} {p.last_name}".replace("  ", " "),
            'dob': p.dob,
            'gender': p.gender,
            'e_ticket_number': p.e_ticket_number,
            'airline_confirmation_number': p.airline_confirmation_number
        }
        for p in passengers if p.e_ticket_number and p.airline_confirmation_number
    ]

    # Only proceed if there are valid passengers to include
    if not passengers_with_tickets:
        print(f"No valid tickets for Booking ID: {instance.booking_id}")
        return

    # Email context setup
    context = {
        'customer_name': instance.customer.name,
        'tickets': passengers_with_tickets,
        'payble_amount': instance.payble_amount,  # Include payable amount globally
    }

    if instance.pnr_decoded_data:
        # Use PNR decoded data as the flight information
        context['pnr_decoded_data'] = instance.pnr_decoded_data
    else:
        # Include flight and airport details for one-way or return trips
        context['booking'] = {
            'flight_name': instance.flight_name,
            'departure_iata': instance.departure_iata,
            'arrival_iata': instance.arrival_iata,
            'departure_date': instance.departure_date,
            'arrival_date': instance.arrival_date,
        }
        
        departure_airport = Airport.objects.get(iata=instance.departure_iata.upper())
        arrival_airport = Airport.objects.get(iata=instance.arrival_iata.upper())
        context['departure_airport'] = departure_airport
        context['arrival_airport'] = arrival_airport

        # Add return trip details if applicable
        if instance.return_departure_iata and instance.return_arrival_iata:
            return_departure_airport = Airport.objects.get(iata=instance.return_departure_iata.upper())
            return_arrival_airport = Airport.objects.get(iata=instance.return_arrival_iata.upper())
            context['return_trip'] = {
                'return_departure_iata': instance.return_departure_iata,
                'return_arrival_iata': instance.return_arrival_iata,
                'return_departure_date': instance.return_departure_date,
                'return_arrival_date': instance.return_arrival_date,
                'return_departure_airport': return_departure_airport,
                'return_arrival_airport': return_arrival_airport,
            }
        

    # Email details
    subject = 'Your Flight Booking Confirmation & Details'
    from_email = 'customerservice@valueutickets.com'
    to = instance.customer.email

    # Render and send email
    html_content = render_to_string('ticket_delivery.html', context)
    text_content = strip_tags(html_content)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Ticket confirmation email sent for Booking ID: {instance.booking_id}")
    except Exception as e:
        print(f"Error sending ticket confirmation email for Booking ID {instance.booking_id}: {e}")


def send_ticket_cancelled_mail(instance):
    # Prepare email details
    subject = 'Confirm Your Flight Ticket Cancellation'
    from_email = 'customerservice@valueutickets.com'
    to = instance.customer.email

    # Context for email template
    context = {
        'booking_id': instance.booking_id,
        'customer_email': instance.customer.email,
    }

    # Render the HTML content
    html_content = render_to_string('ticket_cancellation.html', context)
    text_content = strip_tags(html_content)

    try:
        # Send email
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Ticket cancelled email sent to {to} for Booking ID {instance.booking_id}")
    except Exception as e:
        print(f"Error sending ticket cancelled email for Booking ID {instance.booking_id}: {e}")

