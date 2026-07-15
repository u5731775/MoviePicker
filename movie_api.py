import requests
from config import API_KEY


def get_movie_data(title):
    url = f"https://www.omdbapi.com/?t={title}&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "False":
        return None

    return {
        "title": data["Title"],
        "genre": data["Genre"].split(",")[0].strip(),
        "runtime": int(data["Runtime"].replace(" min", "")),
        "year": int(data["Year"]),
        "imdb_rating": float(data["imdbRating"]),
        "watched": False,
        "rating": None
    }