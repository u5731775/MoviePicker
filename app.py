import streamlit as st
from menu import display_menu
from picker import pick_random_movie
from storage import load_movies, save_movies
from movie import create_movie
from stats import show_stats
from movie_api import get_movie_data
from storage import load_movies

movies = load_movies()

st.set_page_config(
    page_title="Movie Night",
    page_icon="🎬"
)

page = st.sidebar.selectbox(
    "Choose a page",
    [
        "Movies",
        "Add Movie",
        "Random Picker",
        "Statistics"
    ]
)

st.title("🎬 Movie Night")

st.write(f"Movies in library: {len(movies)}")

if page == "Movies":

    st.header("Movie Library")

    for movie in movies:

        watched = "✅" if movie["watched"] else "🎬"

        rating = (
            f"⭐ {movie['rating']}/10"
            if movie["rating"]
            else "Not Rated"
        )

        st.write(
            f"{watched} "
            f"{movie['title']} "
            f"({movie['year']}) "
            f"- {rating}"
        )

if page == "Add Movie":

    st.header("Add Movie")

    method = st.radio(
        "Method",
        [
            "Automatic Lookup",
            "Manual Entry"
        ]
    )

    if method == "Automatic Lookup":

        title = st.text_input(
            "Movie Title"
        )

        if st.button("Add Movie"):

            movie = get_movie_data(title)

            if movie:

                movies.append(movie)

                save_movies(movies)

                st.success(
                    f"Added {movie['title']}"
                )

            else:

                st.error("Movie not found")

    else:

        title = st.text_input("Title")

        genre = st.text_input("Genre")

        runtime = st.number_input(
            "Runtime",
            min_value=1
        )

        year = st.number_input(
            "Year",
            min_value=1900
        )

        if st.button("Save"):

            movie = create_movie(
                title,
                genre,
                runtime,
                year
            )

            movies.append(movie)

            save_movies(movies)

            st.success(
                f"Added {title}"
            )

if page == "Random Picker":

    st.header("🎲 Movie Picker")

    if st.button(
        "Pick Tonight's Movie"
    ):

        movie = pick_random_movie(
            movies
        )

        if movie:

            st.balloons()

            st.success(
                movie["title"]
            )

if page == "Statistics":

    total = len(movies)

    watched = sum(
        1 for movie in movies
        if movie["watched"]
    )

    st.metric(
        "Movies",
        total
    )

    st.metric(
        "Watched",
        watched
    )

    st.metric(
        "Remaining",
        total - watched
    )