from django.apps import AppConfig


class FlightapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FlightAPI'
    verbose_name = 'Flight Management' 

    def ready(self):
        import FlightAPI.signals
