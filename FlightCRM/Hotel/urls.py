from django.urls import include, path
from . import views


urlpatterns = [
    path("api/v4/hotel-booking/",views.HotelBookingView.as_view(),name="book-stay")
]
