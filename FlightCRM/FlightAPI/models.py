from django.db import models

# Create your models here.

from django.db import models

class Airport(models.Model):
    city = models.CharField(max_length=255)
    airport_name = models.CharField(max_length=255)
    faa = models.CharField(max_length=3, blank=True, null=True)
    iata = models.CharField(max_length=3, blank=True, null=True)
    icao = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        db_table = 'Airports'  # Ensure Django uses the correct table

    def __str__(self):
        return self.airport_name
