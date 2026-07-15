import json
import os
import time
import requests


def get_api_key():
    # 1. Check system environment variables first
    if os.getenv("OMDB_API_KEY"):
        print("🔑 Found API key in system environment variables!")
        return os.getenv("OMDB_API_KEY")

    # 2. Check local .env file (Your setup)
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    if "OMDB_API_KEY" in line:
                        # Split at the first '=' to get the value
                        key_val = line.split("=", 1)[-1].strip()
                        # Strip off any accidental surrounding quotes
                        api_key = key_val.strip('"').strip("'")
                        print("🔑 Found API key in your local .env file!")
                        return api_key
        except Exception as e:
            print(f"⚠️ Tried reading .env but ran into an issue: {e}")

    # 3. Check local Streamlit secrets as a backup
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, "r") as f:
                for line in f:
                    if "OMDB_API_KEY" in line or "api_key" in line:
                        api_key = line.split("=")[-1].strip().strip('"').strip("'")
                        print("🔑 Found API key in local Streamlit secrets!")
                        return api_key
        except Exception:
            pass

    # 4. Total manual fallback
    print("🤖 Could not find the key in .env or Streamlit secrets.")
    return input("🔑 Please paste your OMDb API Key: ").strip()


# Get the key using our fallback system
api_key = get_api_key()

if not api_key:
    print("❌ Error: API key is required to fetch movie data.")
    exit()


# Helper function to query OMDb
def fetch_movie_metadata(title, key):
    url = f"https://www.omdbapi.com/?t={title}&apikey={key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("Response") == "False":
            return None
        return {
            "poster_url": data.get("Poster"),
            "plot": data.get("Plot"),
            "imdb_rating": float(data.get("imdbRating", "0.0")) if data.get("imdbRating") and data.get(
                "imdbRating") != "N/A" else 0.0
        }
    except Exception as e:
        print(f"⚠️ Error fetching {title}: {e}")
        return None


# Load your existing JSON file
try:
    with open("movies.json", "r") as f:
        movies = json.load(f)
except FileNotFoundError:
    print("❌ Error: Could not find movies.json in this directory!")
    exit()

print(f"🍿 Found {len(movies)} movies. Starting upgrade...")

updated_movies = []

for idx, movie in enumerate(movies):
    title = movie["title"]

    # Only fetch if we are missing the keys
    if "poster_url" not in movie or "plot" not in movie:
        print(f"[{idx + 1}/{len(movies)}] Fetching metadata for: {title}...")

        metadata = fetch_movie_metadata(title, api_key)

        if metadata:
            movie["poster_url"] = metadata["poster_url"]
            movie["plot"] = metadata["plot"]
            movie["imdb_rating"] = metadata["imdb_rating"]
        else:
            # Fallbacks so the schema stays strictly aligned
            movie["poster_url"] = None
            movie["plot"] = None
            movie["imdb_rating"] = 0.0

        # Standard safety delay
        time.sleep(0.2)
    else:
        print(f"[{idx + 1}/{len(movies)}] {title} already has metadata. Skipping.")

    updated_movies.append(movie)

# Save the updated structured data back to movies.json
with open("movies.json", "w") as f:
    json.dump(updated_movies, f, indent=4)

print("\n🎉 Upgrade complete! All existing movies now have posters, ratings, and plots mapped directly.")