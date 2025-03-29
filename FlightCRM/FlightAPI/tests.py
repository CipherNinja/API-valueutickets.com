from django.test import TestCase
from django.core import mail

def test_email_sent_on_status_change(self):
    """
    Test that an email is sent when the authentication status changes.
    """
    # Update the status to trigger the signal
    self.booking.customer_approval_status = "denied"
    self.booking.save()

    # Check that an email was sent
    self.assertEqual(len(mail.outbox), 1, "An email should have been sent.")
    self.assertEqual(
        mail.outbox[0].to,
        ['customerservice@valueutickets.com'],
        "Email should be sent to customerservice@valueutickets.com."
    )