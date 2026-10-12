from django.contrib import admin
from .models import Movie, Showtime, SeatBooking, MovieReview

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration', 'release_date', 'average_rating')
    search_fields = ('title', 'genre')

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'show_date', 'show_time', 'ticket_price', 'screen_number')
    list_filter = ('show_date', 'screen_number')

@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'showtime', 'selected_seats', 'total_paid', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'selected_seats')

@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'reviewer_name', 'rating', 'created_date')
    list_filter = ('rating',)
