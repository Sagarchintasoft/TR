# 🎬 Movie Booking & Review Portal (CinemaHub)

A full-featured Django web application for movie browsing, seat selection & booking, and user reviews. Ready to run locally or deploy to Render.

---

## 🚀 Features

- **Movie Catalog**: Browse movies, filter by genre, view release dates, runtime, and average ratings.
- **Movie Details & Showtimes**: Detailed synopsis, poster, showtimes list, and community reviews.
- **Interactive Seat Booking**: Visual grid with live seat selection (Available / Selected / Booked), dynamic price calculation, and duplicate seat collision validation.
- **Booking Confirmation**: Summary ticket display with seats and total price.
- **Reviews & Ratings**: User submission form with 1–5 star ratings and reviews list.
- **Admin Panel**: Manage Movies, Showtimes, Bookings, and Reviews via Django Admin.
- **Render Deployment Ready**: Preconfigured `render.yaml` with Gunicorn and WhiteNoise.

---

## 🛠️ Quickstart

### 1. Create and Activate a Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py makemigrations portal
python manage.py migrate
```

### 4. (Optional) Seed Sample Data
```bash
python seed_data.py
```

### 5. Create Admin Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## ☁️ Deployment on Render

This project includes a `render.yaml` blueprint:
1. Push this repository to GitHub or GitLab.
2. Link your repository in [Render](https://render.com/).
3. Choose **Blueprint** deployment or create a Web Service using the build & start commands in `render.yaml`.
