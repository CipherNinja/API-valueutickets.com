from rest_framework.serializers import Serializer
from rest_framework import serializers
from .models import HotelBooking
class HotelBookingAPI(Serializer):
    phone_number = serializers.CharField(max_length=15)
    email = serializers.EmailField()
    checkin_datetime = serializers.DateTimeField()
    checkout_datetime = serializers.DateTimeField()
    adults = serializers.IntegerField()
    children = serializers.IntegerField()
    infants = serializers.IntegerField()
    destination = serializers.CharField(max_length=255)

    def create(self,validate_data):
        booking_details = HotelBooking.objects.create(
            phone_number=validate_data["phone_number"],
            email=validate_data["email"],
            checkin_datetime=validate_data["checkin_datetime"],
            checkout_datetime=validate_data["checkout_datetime"],
            adults = validate_data["adults"],
            children = validate_data["children"],
            infants = validate_data["infants"],
            destination = validate_data["destination"]
        )

        booking_details.save()
        return {
            "booking_id":f"{booking_details.id}",
            "message":"Booking Successful"
        }