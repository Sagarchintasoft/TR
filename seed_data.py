import os
import django
from datetime import date, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_project.settings')
django.setup()

from portal.models import Movie, Showtime, MovieReview

def seed():
    print("Seeding database with sample movies, showtimes, and reviews...")
    
    if Movie.objects.exists():
        print("Movies already exist in database. Skipping seeding.")
        return

    m1 = Movie.objects.create(
        title="Inception",
        genre="Sci-Fi / Action",
        duration=148,
        release_date=date(2010, 7, 16),
        poster_url="https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=800&auto=format&fit=crop&q=80",
        description="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
    )

    m2 = Movie.objects.create(
        title="Interstellar",
        genre="Sci-Fi / Drama",
        duration=169,
        release_date=date(2014, 11, 7),
        poster_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=80",
        description="When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft, along with a team of researchers, to find a new planet for humans."
    )

    m3 = Movie.objects.create(
        title="The Dark Knight",
        genre="Action / Crime",
        duration=152,
        release_date=date(2008, 7, 18),
        poster_url="https://images.unsplash.com/photo-1509281373149-e957c6296406?w=800&auto=format&fit=crop&q=80",
        description="When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice."
    )

    today = date.today()

    # Showtimes
    Showtime.objects.create(movie=m1, show_date=today, show_time=time(14, 0), ticket_price=250.00, screen_number=1)
    Showtime.objects.create(movie=m1, show_date=today, show_time=time(18, 30), ticket_price=300.00, screen_number=2)
    Showtime.objects.create(movie=m2, show_date=today, show_time=time(15, 30), ticket_price=280.00, screen_number=3)
    Showtime.objects.create(movie=m2, show_date=today, show_time=time(20, 0), ticket_price=350.00, screen_number=1)
    Showtime.objects.create(movie=m3, show_date=today, show_time=time(16, 45), ticket_price=260.00, screen_number=2)
    Showtime.objects.create(movie=m3, show_date=today, show_time=time(21, 15), ticket_price=320.00, screen_number=3)

    # Reviews
    MovieReview.objects.create(movie=m1, reviewer_name="Alice M.", rating=5, comment="Mind-bending masterpiece! The visual effects and Hans Zimmer score are unmatched.")
    MovieReview.objects.create(movie=m1, reviewer_name="David K.", rating=4, comment="Brilliant concept and tight pacing. Kept me on the edge of my seat.")
    MovieReview.objects.create(movie=m2, reviewer_name="Sarah T.", rating=5, comment="Emotionally powerful and visually breathtaking. Truly an unforgettable experience.")
    MovieReview.objects.create(movie=m3, reviewer_name="Bruce W.", rating=5, comment="Heath Ledger gave one of the greatest performances in cinematic history.")

    print("Seeding complete! Sample movies, showtimes, and reviews created.")

if __name__ == '__main__':
    seed()
