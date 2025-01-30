from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'airports', views.AirportViewSet)

urlpatterns = [
    path('', views.home, name='home'),  # Keep the home view
    path('api/v1/', include(router.urls)),  # Versioning included in the path
]
