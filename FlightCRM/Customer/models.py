from django.db import models

class ContactUs(models.Model):
    name = models.CharField(max_length=255, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    country = models.CharField(max_length=100, verbose_name="Country")
    message = models.TextField(verbose_name="Message")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Submitted At")

    class Meta:
        verbose_name = "Contact Form"
        verbose_name_plural = "Contact Form"
    
    def __str__(self):
        return f"Contact Request from {self.name} ({self.email})"
