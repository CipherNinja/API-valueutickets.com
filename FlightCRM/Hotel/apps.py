from django.apps import AppConfig


class HotelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Hotel'
    verbose_name = "Hotel Management"
    def ready(self):
        import Hotel.signals