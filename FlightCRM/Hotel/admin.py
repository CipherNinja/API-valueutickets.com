from django.contrib import admin
from .models import HotelBooking

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = (
        'hotel_booking_id', 
        'email', 
        'phone_number', 
        'destination', 
        'checkin_datetime', 
        'checkout_datetime', 
        'adults', 
        'children', 
        'infants'
    )  # Fields to display in the list view

    list_filter = ('destination', 'checkin_datetime', 'checkout_datetime')  # Filters for quick data segmentation

    search_fields = ('hotel_booking_id', 'email', 'phone_number', 'destination')  # Search functionality

    ordering = ('-checkin_datetime',)  # Order bookings by newest check-in date first

    readonly_fields = ('hotel_booking_id',)  # Make booking ID read-only to prevent accidental edits

    # date_hierarchy = 'checkin_datetime'  # Add a date hierarchy navigation bar

    fieldsets = (
        ('Customer Information', {
            'fields': ('email', 'phone_number'),
        }),
        ('Booking Details', {
            'fields': ('hotel_booking_id', 'destination', 'checkin_datetime', 'checkout_datetime'),
        }),
        ('Group Information', {
            'fields': ('adults', 'children', 'infants'),
        }),
    )

    def get_queryset(self, request):
        # Customize the queryset for better performance or filtering
        qs = super().get_queryset(request)
        return qs.prefetch_related()

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False
