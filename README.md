# GameScout

A personalized video game discovery platform that helps gamers find and track games matching their interests using the RAWG Video Games Database.

## Features

- **User Authentication**: Secure JWT-based signup/login with password hashing
- **Game Discovery**: Search and filter 500K+ games by genre, platform, and release timing
- **Personalized Recommendations**: Two recommendation feeds based on user preferences and collection genres
- **Wishlist Management**: Track games with statuses (wishlist, played, interested)
- **Game Details**: View ratings, release dates, screenshots, and platform availability
- **Preference Management**: Update favorite genres and platforms on-the-fly

## Tech Stack

**Backend**: Flask, PostgreSQL, SQLAlchemy, JWT, bcrypt, Flask-CORS  
**Frontend**: React, Vite, React Router, Axios  
**API**: RAWG Video Games Database  
**Deployment**: Render (backend), Netlify (frontend)

## Local Setup

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL (optional, uses SQLite by default)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your RAWG_API_KEY

# Run the server
python app.py
```

Backend runs at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Ensure VITE_API_URL=http://localhost:5000/api

# Run the dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

## Database Models

**User**: id, username, email, hashed_password, favorite_genres, favorite_platforms  
**Game**: id, user_id, rawg_id, title, cover_image, rating, release_date, status, genres, platforms

## API Endpoints

**Auth**: `/api/auth/signup`, `/api/auth/login`, `/api/auth/me`  
**Games**: `/api/games/search`, `/api/games/<id>`, `/api/games/recommendations`  
**Wishlist**: `/api/wishlist` (GET, POST, PATCH, DELETE)