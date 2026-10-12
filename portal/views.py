from django.shortcuts import render, get_object_or_404, redirect
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
