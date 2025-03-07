from rest_framework.views import APIView
from .models import ContactUs
from rest_framework.response import Response
from rest_framework import status
from .serializers import contactUsSerializer
# Create your views here.

class ContactUsCarrier(APIView):
    "This API handels the logic to save and carry the contactus page data to CRM "

    def post(self,request,*arg,**kwarg):
        
        serializer = contactUsSerializer(data=request.data)
        if serializer.is_valid():    
            serializer.save()
            success_message = {
                "message":"Data is added to inventory ✅"
            }
            return Response(success_message,status=status.HTTP_201_CREATED)
        else:
            failure_message = {
                "message":"Something went wrong"
            }
            return Response(failure_message,status=status.HTTP_400_BAD_REQUEST)
            
    
