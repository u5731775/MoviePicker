import streamlit as st
import pandas as pd


def show_stats(movies):
    if not movies:
        st.info("Add some movies to your library to unlock statistics!")
        return

    # 1. Calculations
    total = len(movies)
    watched_movies = [m for m in movies if m.get("watched", False)]
    watched = len(watched_movies)
    remaining = total - watched

    # Calculate total watch time in hours
    total_minutes = sum(movie.get("runtime", 0) for movie in watched_movies)
    total_hours = round(total_minutes / 60, 1)

    # Average personal rating
    ratings = [movie["rating"] for movie in movies if movie.get("rating") is not None]
    average = sum(ratings) / len(ratings) if ratings else 0.0

    # 2. Progress Bar
    st.subheader("🏆 Watchlist Progress")
    if total > 0:
        completion_rate = watched / total
        st.progress(completion_rate)
        st.write(f"You have finished **{int(completion_rate * 100)}%** of your movie list!")

    st.markdown("---")

    # 3. Quick Stats Cards
    st.subheader("📊 Fun Facts")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Average Rating",
            value=f"⭐ {average:.1f}/10" if ratings else "N/A",
            help="Your average rating across rated movies"
        )
    with col2:
        st.metric(
            label="Time Spent Watching",
            value=f"⏳ {total_hours} hrs",
            help="Total runtime of all watched movies combined"
        )
    with col3:
        # Find the most common genre in the library
        genres = [m.get("genre", "Unknown") for m in movies if m.get("genre")]
        favorite_genre = max(set(genres), key=genres.count) if genres else "N/A"
        st.metric(
            label="Dominant Genre",
            value=favorite_genre,
            help="The genre you add to your library the most"
        )

    st.markdown("---")

    # 4. Genre Breakdown Chart
    if genres:
        st.subheader("🎭 Genre Breakdown")
        # Count occurrences of each genre and put into a clean dataframe
        genre_counts = pd.Series(genres).value_counts().reset_index()
        genre_counts.columns = ["Genre", "Count"]

        # Display as a clean bar chart
        st.bar_chart(data=genre_counts, x="Genre", y="Count", color="#ff4b4b", use_container_width=True)

    st.markdown("---")

    # 5. Hall of Fame (Top Rated)
    # Sort by rating and get top 3 rated movies
    top_rated = sorted(
        [m for m in movies if m.get("rating") is not None],
        key=lambda x: x["rating"],
        reverse=True
    )[:3]

    if top_rated:
        st.subheader("⭐ Our All-Time Favorites")
        st.write("These are your absolute highest-rated movies:")

        cols = st.columns(len(top_rated))
        for idx, movie in enumerate(top_rated):
            with cols[idx]:
                poster = movie.get("poster_url")
                if not poster or poster == "N/A":
                    poster = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&q=80"

                st.markdown(
                    f"""
                    <div style="width: 100%; height: 220px; overflow: hidden; border-radius: 8px;">
                        <img src="{poster}" style="width:100%; height:100%; object-fit: cover;"/>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(f"**{movie['title']}**")
                st.caption(f"Rated: {movie['rating']}/10")