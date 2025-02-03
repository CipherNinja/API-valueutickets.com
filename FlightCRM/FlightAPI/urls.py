from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'airports', views.AirportViewSet)


urlpatterns = [
    path('', views.home, name='home'),
    path('api/v1/', include(router.urls)),
    path('api/v1/flight/search/onewaytrip/',views.FlightOnewayTrip.as_view(),name="onewaytrip")
]
