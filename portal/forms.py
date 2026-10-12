from django import forms
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
