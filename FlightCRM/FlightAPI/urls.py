from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'airports', views.AirportViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/flight/search/onewaytrip/',views.FlightOnewayTrip.as_view(),name="onewaytrip"),
    path('api/v2/flight/booking/', views.FlightBookingCreateView.as_view(), name='flight-booking-create'),
    path('api/login/', views.BookingLoginView.as_view(), name='booking-login'),
]
