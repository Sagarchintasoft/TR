from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    poster_url = models.URLField(max_length=500)
    description = models.TextField()

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    show_date = models.DateField()
    show_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2)
    screen_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.movie.title} - {self.show_date} @ {self.show_time} (Screen {self.screen_number})"


class SeatBooking(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    selected_seats = models.TextField(help_text="Comma-separated seat identifiers, e.g., A1,A2")
    total_paid = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.customer_name} for {self.showtime.movie.title} ({self.selected_seats})"


class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title} - {self.rating}★ by {self.reviewer_name}"
