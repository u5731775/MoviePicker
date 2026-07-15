def create_movie(
    title,
    genre,
    runtime,
    year
):
    return {
        "title": title,
        "genre": genre,
        "runtime": runtime,
        "year": year,
        "watched": False,
        "rating": None
    }