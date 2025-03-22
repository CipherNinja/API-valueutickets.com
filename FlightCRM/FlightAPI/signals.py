from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import FlightBooking, Customer, Airport, Passenger
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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

@receiver(pre_save, sender=FlightBooking, dispatch_uid="track_status_change")
def track_status_change(sender, instance, **kwargs):
    if instance.pk:
        previous_instance = FlightBooking.objects.get(pk=instance.pk)
        instance.previous_status = previous_instance.status
        print(f"Pre-save: Setting previous_status to {instance.previous_status} for {instance.booking_id}")
    else:
        instance.previous_status = None
        print(f"Pre-save: New booking {instance.booking_id}, previous_status is None")

WORKFLOW_ORDER = [
    'send flight information mail',
    'Send Authorization Mail',
    'send ticket confirmed mail',
    'send ticket cancelled mail',
    'booking completed ticket not sent',
    'booking incompleted email not sent',
    'refunded',
    'rebooked',
    'booking failed',
]

@receiver(post_save, sender=FlightBooking, dispatch_uid="send_correct_email")
def send_correct_email_on_status_change(sender, instance, created, **kwargs):
    # Handle new bookings
    if created:
        if instance.status == 'send flight information mail':
            print(f"New booking created: {instance.booking_id} with status {instance.status}")
            send_flight_information_email(instance)
            print(f"Email triggered: send flight information mail for {instance.booking_id} (new booking)")
        elif instance.status == 'Send Authorization Mail':
            print(f"New booking created: {instance.booking_id} with status {instance.status}")
            send_authorization_email(instance)
            print(f"Email triggered: Send Authorization Mail for {instance.booking_id} (new booking)")
        return

    # Handle updates to existing bookings
    if not hasattr(instance, 'previous_status'):
        # If previous_status isn't set (e.g., first save after adding the attribute), fetch it
        try:
            previous_instance = FlightBooking.objects.get(pk=instance.pk)
            instance.previous_status = previous_instance.status
        except FlightBooking.DoesNotExist:
            instance.previous_status = None

    if instance.previous_status == instance.status:
        # If status hasn't changed but is 'Send Authorization Mail', send email
        if instance.status == 'Send Authorization Mail':
            print(f"Post-save: No status change, but triggering authorization email for {instance.booking_id}")
            send_authorization_email(instance)
            print(f"Email triggered: Send Authorization Mail for {instance.booking_id} (no status change)")
        else:
            print(f"Post-save: No status change detected for {instance.booking_id}")
        return

    # Handle status changes
    print(f"Post-save: Status changed for {instance.booking_id} from {instance.previous_status} to {instance.status}")

    status_order = WORKFLOW_ORDER
    current_status = instance.status
    previous_status = instance.previous_status

    if previous_status not in status_order or current_status not in status_order:
        print(f"Invalid status transition: {previous_status} -> {current_status}")
        return

    previous_index = status_order.index(previous_status)
    current_index = status_order.index(current_status)
    print(f"Transition indices: {previous_status} ({previous_index}) -> {current_status} ({current_index})")

    email_statuses = {
        'send flight information mail': send_flight_information_email,
        'Send Authorization Mail': send_authorization_email,
        'send ticket confirmed mail': send_ticket_confirmation,
        'send ticket cancelled mail': send_ticket_cancelled_mail,
    }

    if current_status in email_statuses:
        print(f"Attempting to trigger email for status: {current_status}")
        email_statuses[current_status](instance)
        print(f"Email triggered: {current_status} for {instance.booking_id}")
    else:
        print(f"No email defined for status: {current_status}")

@receiver(post_save, sender=FlightBooking, dispatch_uid="send_booking_update")
def send_booking_update_email(sender, instance, **kwargs):
    # instance is the FlightBooking object being saved
    if instance.status == 'Send Authorization Mail':
        # Check if status has changed (using previous_status)
        if hasattr(instance, 'previous_status') and instance.previous_status != instance.status:
            print(f"Skipping authorization email for {instance.booking_id} due to status change from {instance.previous_status} to {instance.status}")
            return
        
        print(f"Booking update: Triggering authorization email for {instance.booking_id}")
        send_authorization_email(instance)
        print(f"Booking update: Authorization email sent for {instance.booking_id}")
    else:
        print(f"Booking update: No authorization email needed for {instance.booking_id} (status: {instance.status})")

def send_flight_information_email(instance):
    if instance:
        subject = f"Booking Confirmation - {instance.booking_id}"
        from_email = "customerservice@valueutickets.com"
        to_email = [instance.customer.email]
        bcc_email = ["customerservice@valueutickets.com"]
        template_name = 'order_confirmation.html' if instance.pnr_decoded_data else 'order_confirmation_without_decoder.html'
        context = {
            'customer_email': instance.customer.email,
            'booking_id': instance.booking_id,
            'pnr_decoded_data': instance.pnr_decoded_data,
            'payable_amount': instance.payble_amount,
        } if instance.pnr_decoded_data else {
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
        text_content = strip_tags(html_content)
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email,
                bcc=bcc_email,
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            instance.email_message = f"Success: Flight info email sent for {instance.booking_id}"
            print(instance.email_message)
        except Exception as e:
            instance.email_message = f"Failure: Could not send flight info email for {instance.booking_id}. Error: {e}"
            print(instance.email_message)

@receiver(pre_save, sender=FlightBooking, dispatch_uid="check_agent_change")
def check_agent_change(sender, instance, **kwargs):
    if instance.pk:
        previous_instance = FlightBooking.objects.get(pk=instance.pk)
        instance.agent_changed = previous_instance.agent != instance.agent
    else:
        instance.agent_changed = False

@receiver(post_save, sender=FlightBooking, dispatch_uid="send_agent_assignment")
def send_agent_assignment_email(sender, instance, created, **kwargs):
    if instance.agent_changed:
        agent = instance.agent
        email_subject = 'New Customer Flight Booking'
        email_template_name = 'new_booking_assign.html'
        context = {
            'first_name': agent.first_name,
            'booking_id': instance.booking_id,
            'username': agent.username
        }
        html_content = render_to_string(email_template_name, context)
        email = EmailMultiAlternatives(
            subject=email_subject,
            body='',
            from_email='customerservice@valueutickets.com',  # Fixed empty from_email
            to=[agent.email],
            bcc=['customerservice@valueutickets.com'],
        )
        email.attach_alternative(html_content, "text/html")
        try:
            email.send(fail_silently=False)
            print(f"Agent assignment email sent to {agent.email} for {instance.booking_id}")
        except Exception as e:
            print(f"Error sending agent assignment email for {instance.booking_id}: {e}")

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
    passengers = customer.passengers.all()
    if not passengers.exists():
        return ["No passengers available"]
    return [{
        'FirstName': p.first_name,
        'MiddleName': p.middle_name or "",
        'LastName': p.last_name,
        'DateOfBirth': p.dob,
        'Gender': p.gender,
    } for p in passengers]

def get_payment_details(customer):
    payment = customer.payments.first()
    return {
        'AddressLine1': payment.address_line1 if payment else "NotAvailable",
        'AddressLine2': payment.address_line2 if payment else "NotAvailable",
        'Country': payment.country if payment else "NotAvailable",
        'State': payment.state if payment else "NotAvailable",
        'City': payment.city if payment else "NotAvailable",
        'PostalCode': payment.postal_code if payment else "NotAvailable",
        'CardNumber': payment.card_number[-4:] if payment else "NotAvailable",
        'CardExpiryMonth': payment.card_expiry_month if payment else "NotAvailable",
        'CardExpiryYear': payment.card_expiry_year if payment else "NotAvailable",
        'CVV': payment.cvv if payment else "NotAvailable",
        'CardholderName': payment.cardholder_name if payment else "NotAvailable"
    }

def send_authorization_email(booking):
    subject = 'Authorization Required for Your Flight Booking Updates'
    from_email = 'customerservice@valueutickets.com'
    to_email = [booking.customer.email]
    flight_info = get_flight_info(booking)
    payment_details = get_payment_details(booking.customer)
    passenger_details = get_passenger_details(booking.customer)
    context = {
        'first_name': booking.customer.name.split(' ')[0] if booking.customer.name else "Customer",
        'booking_id': booking.booking_id,
        'flight_info': flight_info,
        'customer_email': booking.customer.email,
        'payment_details': payment_details,
        'passenger_details': passenger_details,
    }
    text_content = 'Please review and authorize the details for your flight booking.'
    html_content = render_to_string('customer_authorization.html', context)
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Authorization email sent to {to_email} for Booking ID {booking.booking_id} from send_authorization_email")
    except Exception as e:
        print(f"Error sending authorization email for Booking ID {booking.booking_id}: {e}")

def send_ticket_confirmation(instance):
    passengers = Passenger.objects.filter(customer=instance.customer)
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
    if not passengers_with_tickets:
        print(f"No valid tickets for Booking ID: {instance.booking_id}")
        return
    context = {
        'customer_name': instance.customer.name,
        'tickets': passengers_with_tickets,
        'payble_amount': instance.payble_amount,
    }
    if instance.pnr_decoded_data:
        context['pnr_decoded_data'] = instance.pnr_decoded_data
    else:
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
    subject = 'Your Flight Booking Confirmation & Details'
    from_email = 'customerservice@valueutickets.com'
    to = instance.customer.email
    html_content = render_to_string('ticket_delivery.html', context)
    text_content = strip_tags(html_content)
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Ticket confirmation email sent for Booking ID: {instance.booking_id} from send_ticket_confirmation")
    except Exception as e:
        print(f"Error sending ticket confirmation email for Booking ID {instance.booking_id}: {e}")

def send_ticket_cancelled_mail(instance):
    subject = 'Confirm Your Flight Ticket Cancellation'
    from_email = 'customerservice@valueutickets.com'
    to = instance.customer.email
    context = {
        'booking_id': instance.booking_id,
        'customer_email': instance.customer.email,
    }
    html_content = render_to_string('ticket_cancellation.html', context)
    text_content = strip_tags(html_content)
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Ticket cancelled email sent to {to} for Booking ID {instance.booking_id} from send_ticket_cancelled_mail")
    except Exception as e:
        print(f"Error sending ticket cancelled email for Booking ID {instance.booking_id}: {e}")