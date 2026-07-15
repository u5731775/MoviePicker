# movie.py

def create_movie(
    title,
    genre,
    runtime,
    year,
    poster_url=None,
    plot=None
):
    """
    Creates a movie dictionary with defaults for missing fields
    to match the schema used by get_movie_data.
    """
    return {
        "title": title,
        "genre": genre,
        "runtime": runtime,
        "year": year,
        "poster_url": poster_url,  # Defaults to None if not provided
        "plot": plot,              # Defaults to None if not provided
        "watched": False,
        "rating": None
    }