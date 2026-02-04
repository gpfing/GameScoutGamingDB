# GameScout - Personalized Video Game Discovery Platform

## Problem & Solution
With 10,000+ games released annually, players waste hours browsing Steam, PlayStation, and Xbox stores without finding games matching their interests. GameScout uses the RAWG Video Games Database to provide personalized recommendations based on user preferences, helping gamers discover upcoming and current releases tailored to their favorite genres and platforms.

**Target Users**: Gamers overwhelmed by choice who want curated recommendations and a way to track games before they launch.

## User Stories (MVP)
1. Create account and set game preferences (favorite genres, platforms)
2. Search games with filters (release timing: upcoming/current/both, genre, platform)
3. View game details (cover art, rating, platforms, release date, screenshots)
4. Add games to wishlist with status tracking (wishlist, played, interested)
5. Get personalized recommendations based on preferences and ratings
6. Manage wishlist with full CRUD operations (edit status, remove games)

## Data Models (SQLAlchemy)
**User** (authentication & preferences)
- id, username, email, hashed_password, favorite_genres (JSON), favorite_platforms (JSON)

**Game** (wishlist items, one-to-many with User)
- id, user_id (foreign key), rawg_id, title, cover_image, rating, release_date, status (enum: wishlist/played/interested), added_at

## React Components
```
App (auth state, React Context)
├── LoginPage (JWT authentication)
├── SignupPage (account creation with preferences)
└── Dashboard (protected route)
    ├── Navbar (logout, profile)
    ├── DiscoveryPage
    │   ├── PreferenceBar (display/edit favorite genres & platforms)
    │   ├── FilterBar (genre, platform, upcoming/current/both toggle)
    │   ├── GameGrid
    │   │   └── GameCard (cover, title, rating, wishlist button)
    │   └── GameModal (detailed view with screenshots)
    ├── RecommendationsPage
    │   └── RecommendationGrid (filtered by user preferences)
    └── WishlistPage
        └── WishlistItem (status dropdown, remove button)
```

**Key Hooks**: useState, useEffect, useContext (auth management)

## Tech Stack
- **Backend**: Flask, PostgreSQL, SQLAlchemy, Flask-JWT-Extended, Flask-CORS
- **Frontend**: React (Vite), React Router, Axios, CSS Modules
- **External API**: RAWG Video Games Database (500K+ games, 20K requests/month free)
- **Deployment**: Render (backend), Netlify (frontend)

## 1-Week Plan
**Day 1-2**: Flask setup, PostgreSQL models, JWT auth (signup/login), RAWG API service layer  
**Day 3**: Protected routes, wishlist CRUD endpoints, game search with filters (date ranges, genres)  
**Day 4**: React setup, authentication pages, protected routes, API fetch utilities  
**Day 5**: Game discovery interface, recommendation logic, wishlist management UI  
**Day 6**: Styling, loading states, error handling, CRUD testing, cache optimization  
**Day 7**: Deployment (Render + Netlify), documentation, demo video

## Core Logic
- **Release Filtering**: "Upcoming" = release_date > today, "Current" = released within past 6 months, "Both" = no date filter. Query RAWG API with `dates` parameter and `ordering=-released`.

- **Recommendation Algorithm** (Adaptive): 
  1. **Base Preferences**: Fetch games matching ANY of user's favorite_genres OR favorite_platforms (union, not intersection)
  2. **Wishlist Analysis**: Extract genres/platforms from user's wishlisted games, calculate frequency
  3. **Weighted Scoring**: 60% weight on stated preferences + 40% weight on wishlist behavior patterns
  4. Filter by rating ≥ 4.0, exclude games already in wishlist, sort by weighted score descending
  5. **Preference Updates**: PreferenceBar on DiscoveryPage allows instant preference changes without navigating away

- **Caching Strategy**: Store RAWG responses in memory cache (Flask-Caching) for 6 hours to avoid hitting 20K/month rate limit.

## Project Rubric Alignment
**Full CRUD**: Create, read, update, delete wishlist items  
**2+ Related Resources**: User ↔ Game (one-to-many)  
**API Integration**: RAWG Video Games Database for game data  
**Protected Routes**: JWT authentication for all wishlist/recommendation endpoints  
**Clean UI**: React components, game cards, responsive grid layout