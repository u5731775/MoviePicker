import requests
from config import API_KEY


def get_movie_data(title):
    url = f"https://www.omdbapi.com/?t={title}&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "False":
        return None

    # Map the extra fields ("Poster" and "Plot") safely into your dictionary
    return {
        "title": data.get("Title"),
        "genre": data.get("Genre", "Unknown").split(",")[0].strip() if data.get("Genre") else "Unknown",
        "runtime": int(data.get("Runtime", "0").replace(" min", "")) if data.get("Runtime") and data.get("Runtime") != "N/A" else 0,
        "year": int(data.get("Year", "2026")) if data.get("Year") and data.get("Year") != "N/A" else 2026,
        "imdb_rating": float(data.get("imdbRating", "0.0")) if data.get("imdbRating") and data.get("imdbRating") != "N/A" else 0.0,
        "poster_url": data.get("Poster"), # <-- PULLS POSTER URL
        "plot": data.get("Plot"),         # <-- PULLS SHORT PLOT
        "watched": False,
        "rating": None
    }