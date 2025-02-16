from django.apps import AppConfig


class FlightapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FlightAPI'

    def ready(self):
        import FlightAPI.signals
