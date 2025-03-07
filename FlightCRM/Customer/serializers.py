from rest_framework import serializers
from .models import ContactUs
class contactUsSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=False,max_length=255,required=True)
    email = serializers.EmailField(allow_blank=False,required=True)
    phone = serializers.CharField(allow_blank=False,max_length=20,required=True)
    country = serializers.CharField(allow_blank=False,max_length=100,required=True)
    message = serializers.CharField(allow_blank=False,required=True)

    def create(self,validate_data):
        name = validate_data["name"]
        email = validate_data["email"]
        phone = validate_data["phone"]
        country = validate_data["country"]
        message = validate_data["message"]

        contact = ContactUs.objects.create(
            name=name,
            email=email,
            phone=phone,
            country=country,
            message=message
        )
        contact.save()
        return contact