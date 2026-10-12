import os
import zipfile

PROJECT_NAME = "movie_project"
APP_NAME = "portal"

files = {
    "manage.py": """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",

    "requirements.txt": """Django>=5.0,<6.0
gunicorn>=21.2.0
whitenoise>=6.6.0
""",
    
    "render.yaml": """services:
  - type: web
    name: movie-booking-review-demo
    runtime: python
    rootDir: .
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate"
    startCommand: "python manage.py migrate && gunicorn movie_project.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: WEB_CONCURRENCY
        value: 2
      - key: RENDER
        value: "True"
""",

    f"{PROJECT_NAME}/__init__.py": "",

    f"{PROJECT_NAME}/settings.py": """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-demo-secret-key-cinema-hub-2026")
DEBUG = os.environ.get("RENDER", "False") != "True"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com", "*"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portal',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'movie_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'movie_project.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""",

    f"{PROJECT_NAME}/urls.py": """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),
]
""",

    f"{PROJECT_NAME}/wsgi.py": """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_project.settings')

application = get_wsgi_application()
""",

    f"{APP_NAME}/__init__.py": "",

    f"{APP_NAME}/apps.py": """from django.apps import AppConfig

class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'
""",

    f"{APP_NAME}/migrations/__init__.py": "",

    f"{APP_NAME}/models.py": """from django.db import models
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
""",

    f"{APP_NAME}/admin.py": """from django.contrib import admin
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
""",

    f"{APP_NAME}/forms.py": """from django import forms
from .models import SeatBooking, MovieReview

class SeatBookingForm(forms.ModelForm):
    class Meta:
        model = SeatBooking
        fields = ['customer_name', 'customer_email', 'selected_seats']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'selected_seats': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.showtime = kwargs.pop('showtime', None)
        super().__init__(*args, **kwargs)

    def clean_selected_seats(self):
        seats_raw = self.cleaned_data.get('selected_seats', '').strip()
        if not seats_raw:
            raise forms.ValidationError("Please select at least one seat.")

        requested_seats = [seat.strip() for seat in seats_raw.split(',') if seat.strip()]
        
        if not requested_seats:
            raise forms.ValidationError("Invalid seat selection.")

        if self.showtime:
            existing_bookings = SeatBooking.objects.filter(showtime=self.showtime)
            booked_seats = set()
            for booking in existing_bookings:
                for seat in booking.selected_seats.split(','):
                    booked_seats.add(seat.strip())

            already_booked = [seat for seat in requested_seats if seat in booked_seats]
            if already_booked:
                raise forms.ValidationError(
                    f"The following seat(s) are already booked: {', '.join(already_booked)}. Please select different seats."
                )

        return ",".join(requested_seats)


class MovieReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ['reviewer_name', 'rating', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your thoughts about the movie...'}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating
""",

    f"{APP_NAME}/views.py": """from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Movie, Showtime, SeatBooking
from .forms import SeatBookingForm, MovieReviewForm

def movie_list(request):
    genre_query = request.GET.get('genre', '')
    movies = Movie.objects.all()
    
    if genre_query:
        movies = movies.filter(genre__icontains=genre_query)
        
    genres = Movie.objects.values_list('genre', flat=True).distinct()
    
    context = {
        'movies': movies,
        'genres': genres,
        'selected_genre': genre_query,
    }
    return render(request, 'portal/movie_list.html', context)


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    showtimes = movie.showtimes.all()
    reviews = movie.reviews.all().order_by('-created_date')
    
    if request.method == 'POST':
        review_form = MovieReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.movie = movie
            review.save()
            messages.success(request, "Your review has been successfully submitted!")
            return redirect('movie_detail', movie_id=movie.id)
    else:
        review_form = MovieReviewForm()

    context = {
        'movie': movie,
        'showtimes': showtimes,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'portal/movie_detail.html', context)


def book_seats(request, showtime_id):
    showtime = get_object_or_404(Showtime, pk=showtime_id)
    
    existing_bookings = SeatBooking.objects.filter(showtime=showtime)
    booked_seats_set = set()
    for booking in existing_bookings:
        for seat in booking.selected_seats.split(','):
            booked_seats_set.add(seat.strip())

    if request.method == 'POST':
        form = SeatBookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.showtime = showtime
            
            selected_seats_list = [s.strip() for s in booking.selected_seats.split(',') if s.strip()]
            seat_count = len(selected_seats_list)
            booking.total_paid = seat_count * showtime.ticket_price
            booking.save()
            
            messages.success(request, f"Successfully booked {seat_count} seat(s) for {showtime.movie.title}!")
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = SeatBookingForm(showtime=showtime)

    context = {
        'showtime': showtime,
        'form': form,
        'booked_seats': list(booked_seats_set),
        'ticket_price_float': float(showtime.ticket_price),
    }
    return render(request, 'portal/book_seats.html', context)


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(SeatBooking, pk=booking_id)
    return render(request, 'portal/booking_confirmation.html', {'booking': booking})
""",

    f"{APP_NAME}/urls.py": """from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('booking/<int:showtime_id>/', views.book_seats, name='book_seats'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
""",

    f"{APP_NAME}/templates/{APP_NAME}/base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Movie Portal{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{% url 'movie_list' %}">🎬 CinemaHub</a>
        </div>
    </nav>

    <main class="container my-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
""",

    f"{APP_NAME}/templates/{APP_NAME}/movie_list.html": """{% extends 'portal/base.html' %}
{% block title %}Now Showing - CinemaHub{% endblock %}
{% block content %}
<div class="row mb-4 align-items-center">
    <div class="col-md-8">
        <h1 class="fw-bold">Now Showing</h1>
        <p class="text-muted">Explore current movies, check ratings, and book your seats.</p>
    </div>
    <div class="col-md-4">
        <form method="get" class="d-flex">
            <select name="genre" class="form-select me-2" onchange="this.form.submit()">
                <option value="">All Genres</option>
                {% for g in genres %}
                    <option value="{{ g }}" {% if selected_genre == g %}selected{% endif %}>{{ g }}</option>
                {% endfor %}
            </select>
        </form>
    </div>
</div>

<div class="row row-cols-1 row-cols-md-3 g-4">
    {% for movie in movies %}
        <div class="col">
            <div class="card h-100 shadow-sm border-0">
                <img src="{{ movie.poster_url }}" class="card-img-top" alt="{{ movie.title }}" style="height: 380px; object-fit: cover;">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title fw-bold">{{ movie.title }}</h5>
                    <p class="text-muted small mb-2"><span class="badge bg-secondary">{{ movie.genre }}</span> • {{ movie.duration }} mins</p>
                    <p class="text-warning mb-3">★ {{ movie.average_rating }} / 5.0</p>
                    <a href="{% url 'movie_detail' movie.id %}" class="btn btn-dark mt-auto">View Details & Showtimes</a>
                </div>
            </div>
        </div>
    {% empty %}
        <div class="col-12 text-center py-5">
            <p class="text-muted fs-5">No movies found matching your criteria.</p>
        </div>
    {% endfor %}
</div>
{% endblock %}
""",

    f"{APP_NAME}/templates/{APP_NAME}/movie_detail.html": """{% extends 'portal/base.html' %}
{% block title %}{{ movie.title }} - Details{% endblock %}
{% block content %}
<div class="row mb-5">
    <div class="col-md-4">
        <img src="{{ movie.poster_url }}" class="img-fluid rounded shadow" alt="{{ movie.title }}" style="width: 100%; max-height: 500px; object-fit: cover;">
    </div>
    <div class="col-md-8">
        <h1 class="fw-bold">{{ movie.title }}</h1>
        <p class="text-muted"><span class="badge bg-secondary">{{ movie.genre }}</span> | {{ movie.duration }} mins | Released: {{ movie.release_date }}</p>
        <p class="text-warning fs-5">★ {{ movie.average_rating }} / 5.0</p>
        <hr>
        <p>{{ movie.description }}</p>
        
        <h4 class="mt-4 mb-3">Available Showtimes</h4>
        <div class="d-flex flex-wrap gap-2">
            {% for show in showtimes %}
                <a href="{% url 'book_seats' show.id %}" class="btn btn-outline-dark text-start">
                    📅 {{ show.show_date }} @ {{ show.show_time|time:"H:i" }} <br>
                    <small class="text-muted">Screen {{ show.screen_number }} | ₹{{ show.ticket_price }}</small>
                </a>
            {% empty %}
                <p class="text-muted">No showtimes scheduled yet.</p>
            {% endfor %}
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <h3 class="mb-3">Community Reviews</h3>
        <div class="list-group mb-4">
            {% for review in reviews %}
                <div class="list-group-item p-3 mb-2 shadow-sm rounded border-0">
                    <div class="d-flex justify-content-between">
                        <h6 class="fw-bold mb-1">{{ review.reviewer_name }}</h6>
                        <span class="text-warning">★ {{ review.rating }}/5</span>
                    </div>
                    <p class="mb-1 text-secondary">{{ review.comment }}</p>
                    <small class="text-muted" style="font-size: 0.75rem;">{{ review.created_date|date:"M d, Y, H:i" }}</small>
                </div>
            {% empty %}
                <p class="text-muted">No reviews yet. Be the first to share your thoughts!</p>
            {% endfor %}
        </div>

        <div class="card p-4 shadow-sm border-0">
            <h4 class="mb-3">Leave a Review</h4>
            <form method="post">
                {% csrf_token %}
                {{ review_form.as_p }}
                <button type="submit" class="btn btn-dark">Submit Review</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
""",

    f"{APP_NAME}/templates/{APP_NAME}/book_seats.html": """{% extends 'portal/base.html' %}
{% block title %}Book Seats - {{ showtime.movie.title }}{% endblock %}

{% block extra_css %}
<style>
    .screen-indicator {
        background: #e9ecef;
        height: 35px;
        line-height: 35px;
        letter-spacing: 4px;
        font-weight: bold;
    }
    .seat-grid {
        display: grid;
        grid-template-columns: repeat(8, 45px);
        gap: 10px;
        justify-content: center;
    }
    .seat {
        width: 45px;
        height: 45px;
        border: 2px solid #6c757d;
        border-radius: 6px;
        background-color: #ffffff;
        cursor: pointer;
        font-weight: bold;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease-in-out;
    }
    .seat:hover:not(.booked):not(.selected) {
        background-color: #dee2e6;
    }
    .seat.selected {
        background-color: #198754;
        color: white;
        border-color: #198754;
    }
    .seat.booked {
        background-color: #dc3545;
        color: white;
        border-color: #dc3545;
        cursor: not-allowed;
    }
</style>
{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="card shadow-sm border-0 p-4">
            <h2 class="fw-bold mb-2">Book Tickets: {{ showtime.movie.title }}</h2>
            <p class="text-muted">
                Show Date: <strong>{{ showtime.show_date }}</strong> | 
                Time: <strong>{{ showtime.show_time|time:"H:i" }}</strong> | 
                Screen: <strong>{{ showtime.screen_number }}</strong> | 
                Price per seat: <strong>₹<span id="unitPrice">{{ ticket_price_float }}</span></strong>
            </p>
            <hr>

            <div class="text-center mb-4">
                <div class="screen-indicator rounded text-muted shadow-sm mb-4">SCREEN THIS WAY</div>
                <div id="seatMatrix" class="seat-grid mb-3"></div>

                <div class="d-flex justify-content-center gap-4 text-small text-muted mt-3">
                    <div><span class="d-inline-block rounded border" style="width:15px; height:15px; background:#fff;"></span> Available</div>
                    <div><span class="d-inline-block rounded" style="width:15px; height:15px; background:#198754;"></span> Selected</div>
                    <div><span class="d-inline-block rounded" style="width:15px; height:15px; background:#dc3545;"></span> Booked</div>
                </div>
            </div>

            <form method="post" id="bookingForm" class="mt-4">
                {% csrf_token %}
                
                {% if form.non_field_errors %}
                    <div class="alert alert-danger">{{ form.non_field_errors }}</div>
                {% endif %}

                <div class="mb-3">
                    <label class="form-label fw-bold">Your Name</label>
                    {{ form.customer_name }}
                    {{ form.customer_name.errors }}
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">Email Address</label>
                    {{ form.customer_email }}
                    {{ form.customer_email.errors }}
                </div>

                {{ form.selected_seats }}

                <div class="d-flex justify-content-between align-items-center bg-light p-3 rounded mb-3">
                    <div>
                        <span class="text-muted">Selected Seats: <strong id="selectedSeatsDisplay" class="text-dark">None</strong></span><br>
                        <span class="text-muted">Total Price: <strong class="text-success fs-5">₹<span id="totalPriceDisplay">0.00</span></strong></span>
                    </div>
                    <button type="submit" class="btn btn-success btn-lg px-4" id="submitBtn" disabled>Confirm Booking</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    const rows = ['A', 'B', 'C', 'D', 'E'];
    const cols = 8;
    const ticketPrice = parseFloat(document.getElementById('unitPrice').innerText);
    const bookedSeatsArray = {{ booked_seats|safe }};

    const seatMatrixContainer = document.getElementById('seatMatrix');
    const selectedSeatsInput = document.getElementById('id_selected_seats');
    const selectedSeatsDisplay = document.getElementById('selectedSeatsDisplay');
    const totalPriceDisplay = document.getElementById('totalPriceDisplay');
    const submitBtn = document.getElementById('submitBtn');

    let selectedSeats = [];

    rows.forEach(rowLetter => {
        for (let i = 1; i <= cols; i++) {
            const seatId = `${rowLetter}${i}`;
            const seatDiv = document.createElement('div');
            seatDiv.classList.add('seat');
            seatDiv.innerText = seatId;
            seatDiv.dataset.seat = seatId;

            if (bookedSeatsArray.includes(seatId)) {
                seatDiv.classList.add('booked');
            } else {
                seatDiv.addEventListener('click', () => toggleSeat(seatId, seatDiv));
            }

            seatMatrixContainer.appendChild(seatDiv);
        }
    });

    function toggleSeat(seatId, element) {
        if (element.classList.contains('booked')) return;

        if (element.classList.contains('selected')) {
            element.classList.remove('selected');
            selectedSeats = selectedSeats.filter(s => s !== seatId);
        } else {
            element.classList.add('selected');
            selectedSeats.push(seatId);
        }

        updateBookingSummary();
    }

    function updateBookingSummary() {
        selectedSeatsInput.value = selectedSeats.join(',');
        
        if (selectedSeats.length > 0) {
            selectedSeatsDisplay.innerText = selectedSeats.join(', ');
            totalPriceDisplay.innerText = (selectedSeats.length * ticketPrice).toFixed(2);
            submitBtn.removeAttribute('disabled');
        } else {
            selectedSeatsDisplay.innerText = 'None';
            totalPriceDisplay.innerText = '0.00';
            submitBtn.setAttribute('disabled', 'true');
        }
    }
</script>
{% endblock %}
""",

    f"{APP_NAME}/templates/{APP_NAME}/booking_confirmation.html": """{% extends 'portal/base.html' %}
{% block title %}Booking Confirmed{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6 mx-auto text-center py-5">
        <div class="card shadow-sm border-0 p-5">
            <div class="mb-3 text-success fs-1">✅</div>
            <h1 class="fw-bold mb-3">Booking Confirmed!</h1>
            <p class="text-muted">Thank you, <strong>{{ booking.customer_name }}</strong>. Your tickets have been successfully booked.</p>
            <hr>
            <ul class="list-unstyled text-start mb-4">
                <li class="mb-2">🎬 <strong>Movie:</strong> {{ booking.showtime.movie.title }}</li>
                <li class="mb-2">📅 <strong>Show Date & Time:</strong> {{ booking.showtime.show_date }} @ {{ booking.showtime.show_time|time:"H:i" }}</li>
                <li class="mb-2">💺 <strong>Seats:</strong> {{ booking.selected_seats }}</li>
                <li class="mb-2">💳 <strong>Total Paid:</strong> ₹{{ booking.total_paid }}</li>
            </ul>
            <a href="{% url 'movie_list' %}" class="btn btn-dark">Back to Movies</a>
        </div>
    </div>
</div>
{% endblock %}
"""
}

# 1. Write all files to directory structure
for filepath, content in files.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print(f"Generated {len(files)} project files in workspace.")

# 2. Package everything cleanly into movie_booking_portal.zip
zip_filename = "movie_booking_portal.zip"
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for filepath, content in files.items():
        zipf.writestr(filepath, content.strip() + "\n")

print(f"Successfully generated {zip_filename} with full structure including manage.py!")
