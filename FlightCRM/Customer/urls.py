from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    path("api/v3/contact-us/",views.ContactUsCarrier.as_view(),name="contact-us"),
    
]
