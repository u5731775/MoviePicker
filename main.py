from menu import display_menu
from picker import pick_random_movie
from storage import load_movies, save_movies
from movie import create_movie
from stats import show_stats
from movie_api import get_movie_data
from movie_manager import list_movies, rate_movie, add_movie, remove_movie, mark_watched


def main():
    movies = load_movies()

    while True:
        choice = display_menu()

        if choice == "1":
            list_movies(movies)

        elif choice == "2":
            movie = pick_random_movie(movies)

            if movie:
                print("\nTonight's movie is...")
                print("🥁")
                print("🥁🥁")
                print("🥁🥁🥁")
                print()
                print(movie["title"].upper())

        elif choice == "3":
            add_movie(movies)

        elif choice == "4":
            remove_movie(movies)

        elif choice == "5":
            mark_watched(movies)

        elif choice == "6":
            rate_movie(movies)

        elif choice == "7":
            show_stats(movies)

        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice")



if __name__ == "__main__":
    main()