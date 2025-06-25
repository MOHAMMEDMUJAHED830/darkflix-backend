from database import save_movie

def scrape_movies():
    # Dummy scraped movies (you'll replace this with real scraper later)
    dummy_movies = [
        {
            "title": "Inception",
            "year": "2010",
            "poster": "https://image.tmdb.org/t/p/w500/8h58d1s9Dxs9PehM9J4ItD6mY8V.jpg",
            "embed_url": "https://www.2embed.to/embed/movie?imdb=tt1375666"
        },
        {
            "title": "Interstellar",
            "year": "2014",
            "poster": "https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg",
            "embed_url": "https://www.2embed.to/embed/movie?imdb=tt0816692"
        }
    ]

    for movie in dummy_movies:
        save_movie(movie["title"], movie["year"], movie["poster"], movie["embed_url"])
    
    return dummy_movies
