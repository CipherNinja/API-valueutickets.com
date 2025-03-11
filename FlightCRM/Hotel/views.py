from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import HotelBookingAPI
# Create your views here.

class HotelBookingView(APIView):
    
    def post(self,request):
        fetched_data = request.data
        serializer = HotelBookingAPI(data=fetched_data)
        if serializer.is_valid():
            booking_details = serializer.save()
            return Response({
                "Booking_ID":booking_details,
                "Message":"Successfully Created"
            },status=status.HTTP_201_CREATED)
        else:
            error = serializer.errors
            return Response({
                    "Error":error
                    },status=status.HTTP_406_NOT_ACCEPTABLE)

