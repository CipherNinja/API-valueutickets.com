from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'airports', views.AirportViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/flight/search/onewaytrip/',views.FlightOnewayTrip.as_view(),name="onewaytrip"),
    path('api/v1/flight/search/roundtrip/',views.FlightRoundTrip.as_view(),name="roundtrip"),
    path('api/v2/flight/booking/', views.FlightBookingCreateView.as_view(), name='flight-booking-create'),
    path('api/email/auth/resp/<str:booking_id>/<str:email_id>/<str:customer_response>', views.CustomerResponseView.as_view(), name='customer_response'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    


]
