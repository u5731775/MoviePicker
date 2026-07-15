from menu import display_menu
from picker import pick_random_movie
from storage import load_movies, save_movies
from movie import create_movie
from stats import show_stats
from movie_api import get_movie_data

def add_movie(movies):
    print("\nAdd Movie")
    print("1. Automatic lookup")
    print("2. Manual entry")

    choice = input("\nSelect option: ")

    if choice == "1":
        add_movie_api(movies)
    elif choice == "2":
        add_movie_manual(movies)
    else:
        print("Invalid option")

def add_movie_api(movies):
    title = input("Movie title: ").strip()

    movie = get_movie_data(title)

    if movie is None:
        print("Movie not found.")
        return

    movies.append(movie)

    save_movies(movies)

    print("\n✅ Movie added!")
    print(f"Title: {movie['title']}")
    print(f"Year: {movie['year']}")
    print(f"Genre: {movie['genre']}")
    print(f"Runtime: {movie['runtime']} mins")

def add_movie_manual(movies):
    title = input("Movie title: ").strip()

    genre = input("Genre: ").strip()

    try:
        runtime = int(input("Runtime (minutes): "))
        year = int(input("Year: "))
    except ValueError:
        print("Invalid number entered.")
        return

    movie = create_movie(
        title,
        genre,
        runtime,
        year
    )

    movies.append(movie)

    save_movies(movies)

    print(f"\n✅ Added {title}")

def list_movies(movies):
    print("\n--- MOVIES ---")

    for i, movie in enumerate(movies, 1):

        status = "✅" if movie["watched"] else "🎬"

        rating = movie["rating"]

        rating_text = (
            f"⭐ {rating}/10"
            if rating is not None
            else "Not Rated"
        )

        print(
            f"{i}. "
            f"{status} "
            f"{movie['title']} "
            f"({movie['year']}) - "
            f"{rating_text}"
        )

def remove_movie(movies):
    list_movies(movies)

    try:
        index = int(input()) - 1

        if index < 0 or index >= len(movies):
            raise IndexError

        removed = movies.pop(index)

        save_movies(movies)

        print(f"Removed {removed['title']}")

    except (ValueError, IndexError):
        print("Invalid selection")

def mark_watched(movies):
    list_movies(movies)

    try:
        index = int(
            input("\nMovie number: ")
        ) - 1

        movies[index]["watched"] = True

        save_movies(movies)

        print("Movie marked as watched.")

    except (ValueError, IndexError):
        print("Invalid selection")

def rate_movie(movies):
    list_movies(movies)

    try:
        index = int(
            input("\nMovie number: ")
        ) - 1

        rating = int(
            input("Rating (1-10): ")
        )

        if 1 <= rating <= 10:

            movies[index]["rating"] = rating

            save_movies(movies)

            print("Rating saved.")

        else:
            print("Rating must be 1-10")

    except (ValueError, IndexError):
        print("Invalid input")
