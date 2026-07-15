import time
import streamlit as st
from menu import display_menu
from picker import pick_random_movie
from storage import load_movies, save_movies
from movie import create_movie
from stats import show_stats
from movie_api import get_movie_data

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Movie Night",
    page_icon="🍿",
    layout="wide"  # Wide layout gives us room for a cool movie grid
)

# 2. Load Data
# Using session state so updates reflect immediately across tabs without reloading files constantly
if "movies" not in st.session_state:
    st.session_state.movies = load_movies()

movies = st.session_state.movies

# 3. Header & Stats Banner
st.title("🎬 Cozy Movie Night")
st.markdown("---")

# Quick metric banner at the top so you always see your progress
total_movies = len(movies)
watched_count = sum(1 for m in movies if m.get("watched", False))
unwatched_count = total_movies - watched_count

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total in Library", total_movies)
with col2:
    st.metric("Watched Together ✅", watched_count)
with col3:
    st.metric("Left to Watch 🍿", unwatched_count)

st.markdown("---")

# 4. Navigation (Using Tabs instead of Sidebar feels much more modern!)
tab_picker, tab_library, tab_add, tab_stats = st.tabs([
    "🎲 Spin the Wheel",
    "📚 Movie Library",
    "➕ Add a Movie",
    "📈 Fun Stats"
])

# --- TAB 1: RANDOM PICKER (Now with suspense & filter options) ---
with tab_picker:
    st.header("🎲 Tonight's Selection")
    st.write("Can't decide? Let the app choose your fate.")

    # Filter options before picking
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        only_unwatched = st.checkbox("Only pick from Unwatched movies", value=True)

    # Filter the pool
    pool = [m for m in movies if not m.get("watched", False)] if only_unwatched else movies

    if st.button("🔥 Pick Tonight's Movie", use_container_width=True):
        if not pool:
            st.warning("No movies match your criteria! Try adding some more first.")
        else:
            # Create a fun "roulette" suspense effect
            with st.spinner("Consulting the movie gods..."):
                time.sleep(1.5)  # The suspense builds!

            chosen_movie = pick_random_movie(pool)

            if chosen_movie:
                st.balloons()
                st.success(f"### 🎉 We are watching: **{chosen_movie['title']}** ({chosen_movie.get('year', 'N/A')})!")

                # Show movie details if we have them
                col_img, col_det = st.columns([1, 2])
                with col_img:
                    # Fallback to a placeholder if no poster URL exists
                    poster = chosen_movie.get("poster_url") or "https://via.placeholder.com/300x450?text=No+Poster"
                    st.image(poster, use_container_width=True)
                with col_det:
                    st.subheader(chosen_movie['title'])
                    st.markdown(f"**Genre:** {chosen_movie.get('genre', 'Unknown')}")
                    st.markdown(f"**Runtime:** {chosen_movie.get('runtime', 'N/A')} mins")
                    if chosen_movie.get("plot"):
                        st.write(f"*\"{chosen_movie['plot']}\"*")

                    # Quick action to mark as watched right there!
                    if st.button("Mark as Watched! ✅"):
                        for m in movies:
                            if m['title'] == chosen_movie['title']:
                                m['watched'] = True
                        save_movies(movies)
                        st.session_state.movies = movies
                        st.rerun()

# --- TAB 2: VISUAL LIBRARY (With Standardized Poster Heights) ---
with tab_library:
    st.header("📚 Your Collection")

    # Simple search bar
    search_query = st.text_input("🔍 Search movies...", "").lower()

    filtered_movies = [m for m in movies if search_query in m['title'].lower()]

    if not filtered_movies:
        st.info("No movies found in your library.")
    else:
        # Display as a clean grid of cards (4 columns)
        cols = st.columns(4)
        for idx, movie in enumerate(filtered_movies):
            col = cols[idx % 4]
            with col:
                # --- POSTER FIX & STANDARDIZATION ---
                poster = movie.get("poster_url")
                if not poster or poster == "N/A":
                    # Cozy default background image
                    poster = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&q=80"

                # Instead of st.image, we render with custom HTML to lock a 2:3 aspect ratio (e.g., 300px width x 450px height)
                # This ensures absolute grid alignment and crops odd-sized posters flawlessly!
                st.markdown(
                    f"""
                    <div style="
                        width: 100%;
                        height: 600px; 
                        overflow: hidden;
                        border-radius: 10px;
                        margin-bottom: 10px;
                    ">
                        <img src="{poster}" style="
                            width: 100%;
                            height: 100%;
                            object-fit: cover;
                            object-position: center;
                        "/>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Title & Year
                watched_status = "✅" if movie.get("watched") else "⏳"
                st.markdown(f"**{movie['title']}** ({movie.get('year', 'N/A')})")

                # --- INTERACTIVE STAR RATING ---
                current_rating = movie.get("rating", 0)

                try:
                    initial_stars = int(current_rating // 2) if current_rating else 0
                except (TypeError, ValueError):
                    initial_stars = 0

                new_stars = st.feedback(
                    "stars",
                    key=f"stars_{idx}",
                )

                if new_stars is not None:
                    calculated_rating = (new_stars + 1) * 2
                    if movie.get("rating") != calculated_rating:
                        movie["rating"] = calculated_rating
                        save_movies(movies)
                        st.session_state.movies = movies
                        st.success(f"Rated {movie['title']} a {calculated_rating}/10!")
                        st.rerun()

                # Show text rating below the stars
                rating_text = f"⭐ {movie.get('rating', 'Not Rated')}/10" if movie.get('rating') else "⏳ Not Rated yet"
                st.write(f"{watched_status} | {rating_text}")

                # Quick toggle status button
                btn_label = "Mark Unwatched" if movie.get("watched") else "Mark Watched"
                if st.button(btn_label, key=f"toggle_{idx}", use_container_width=True):
                    movie['watched'] = not movie.get('watched', False)
                    save_movies(movies)
                    st.session_state.movies = movies
                    st.rerun()

                st.markdown("---")

# --- TAB 3: ADD MOVIE (Beautiful clean layouts) ---
with tab_add:
    st.header("➕ Expand the Library")

    method = st.radio("How would you like to add it?", ["Automatic Lookup 🌐", "Manual Entry ✍️"], horizontal=True)

    if method == "Automatic Lookup 🌐":
        title = st.text_input("Enter Movie Title to Search")
        if st.button("Search & Add", use_container_width=True):
            if title:
                with st.spinner("Searching OMDB..."):
                    movie = get_movie_data(title)

                if movie:
                    # Avoid duplicates
                    if any(m['title'].lower() == movie['title'].lower() for m in movies):
                        st.warning(f"\"{movie['title']}\" is already in your list!")
                    else:
                        movies.append(movie)
                        save_movies(movies)
                        st.session_state.movies = movies
                        st.success(f"Added **{movie['title']}** to your list!")
                        st.rerun()
                else:
                    st.error("Couldn't find that movie. Check the spelling or try manual entry.")
            else:
                st.warning("Please enter a title first.")

    else:
        # Side-by-side columns look much better for manual entry forms
        with st.form("manual_entry_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                manual_title = st.text_input("Title")
                manual_genre = st.text_input("Genre (e.g. Comedy, Sci-Fi)")
            with col_b:
                manual_year = st.number_input("Year", min_value=1900, max_value=2030, value=2026)
                manual_runtime = st.number_input("Runtime (Minutes)", min_value=1, value=120)

            submitted = st.form_submit_button("Add Movie manually", use_container_width=True)
            # Inside your Manual Entry form submission block in app.py:
            if submitted:
                if manual_title:
                    # One clean function call does it all now!
                    movie = create_movie(
                        title=manual_title,
                        genre=manual_genre,
                        runtime=manual_runtime,
                        year=manual_year
                    )

                    movies.append(movie)
                    save_movies(movies)
                    st.session_state.movies = movies
                    st.success(f"Successfully added **{manual_title}**!")
                    st.rerun()
                else:
                    st.error("Movie Title is required.")

# --- TAB 4: STATISTICS (A bit more visual flair) ---
with tab_stats:
    st.header("📈 Our Watching Habits")
    show_stats(movies)  # Utilizing your custom stats module