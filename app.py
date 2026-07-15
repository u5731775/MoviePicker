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

# --- TAB 1: THE ULTIMATE MOVIE PICKER (Now with Filters & Rerolls!) ---
with tab_picker:
    st.header("🎲 Tonight's Movie Roulette")
    st.write("Set your filters and let the app decide your fate.")

    # 1. Roulette Filters
    with st.expander("🛠️ Spin Filters (Optional)", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            # Filter by Watched Status
            pool_choice = st.radio("Which movies should we pick from?", ["Unwatched Only 🍿", "Everything 🔄"])
            only_unwatched = (pool_choice == "Unwatched Only 🍿")

        with col_f2:
            # Filter by Genre
            all_genres = sorted(list(set(m.get("genre", "Unknown") for m in movies if m.get("genre"))))
            selected_genres = st.multiselect("Limit to specific Genres:", all_genres, placeholder="All Genres")

        with col_f3:
            # Filter by Runtime & Min Rating
            max_runtime = st.slider("Max Runtime (minutes)", min_value=60, max_value=240, value=240, step=10)
            min_imdb = st.slider("Minimum IMDb Rating ⭐", min_value=1.0, max_value=10.0, value=1.0, step=0.5)

    # Apply filters to build our roulette pool
    pool = movies
    if only_unwatched:
        pool = [m for m in pool if not m.get("watched", False)]
    if selected_genres:
        pool = [m for m in pool if m.get("genre") in selected_genres]

    # Filter out by runtime and imdb rating safely
    pool = [
        m for m in pool
        if int(m.get("runtime", 0) or 0) <= max_runtime
           and float(m.get("imdb_rating", 0.0) or 0.0) >= min_imdb
    ]

    st.write(f"🎯 Movies matching your filters: **{len(pool)}**")

    # Keep track of the currently picked movie in Session State so rerolling works seamlessly
    if "current_pick" not in st.session_state:
        st.session_state.current_pick = None

    col_spin_btn, col_clear_btn = st.columns([3, 1])
    with col_spin_btn:
        if st.button("🔥 Spin the Wheel!", use_container_width=True, type="primary"):
            if not pool:
                st.error("No movies match your filters! Try widening your search.")
                st.session_state.current_pick = None
            else:
                with st.spinner("Shuffling the deck..."):
                    time.sleep(1.2)
                st.session_state.current_pick = pick_random_movie(pool)
                st.balloons()

    with col_clear_btn:
        if st.button("Reset 🔄", use_container_width=True):
            st.session_state.current_pick = None
            st.rerun()

    # 2. Display Selected Movie
    if st.session_state.current_pick:
        chosen_movie = st.session_state.current_pick
        st.markdown("---")

        col_img, col_det = st.columns([1, 2])
        with col_img:
            poster = chosen_movie.get("poster_url")
            if not poster or poster == "N/A":
                poster = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&q=80"
            st.image(poster, use_container_width=True)

        with col_det:
            st.subheader(f"🎉 Tonight's Selection: **{chosen_movie['title']}**")
            st.write(
                f"📅 **Year:** {chosen_movie.get('year', 'N/A')} | ⏳ **Runtime:** {chosen_movie.get('runtime', 'N/A')} mins | 🎭 **Genre:** {chosen_movie.get('genre', 'Unknown')}")
            st.write(f"⭐ **IMDb:** {chosen_movie.get('imdb_rating', 'N/A')}/10")

            if chosen_movie.get("plot"):
                st.info(f"**Plot Summary:**\n\n*\"{chosen_movie['plot']}\"*")

            # Interactive Picker Actions (Accept vs. Veto!)
            st.markdown("### Decision Time!")
            col_act1, col_act2 = st.columns(2)

            with col_act1:
                # Mark as watched right here!
                if st.button("✅ Accept & Mark Watched!", use_container_width=True):
                    for m in movies:
                        if m['title'] == chosen_movie['title']:
                            m['watched'] = True
                    save_movies(movies)
                    st.session_state.movies = movies
                    st.session_state.current_pick = None
                    st.toast(f"Excellent choice! Marked '{chosen_movie['title']}' as watched.")
                    time.sleep(1)
                    st.rerun()

            with col_act2:
                # VETO! Instantly pull a new movie from the pool
                if st.button("🚫 VETO! Spin Again", use_container_width=True):
                    # Filter out the vetoed movie so we don't pick it again immediately
                    vetoed_pool = [m for m in pool if m['title'] != chosen_movie['title']]
                    if vetoed_pool:
                        with st.spinner("Finding something better..."):
                            time.sleep(1)
                        st.session_state.current_pick = pick_random_movie(vetoed_pool)
                        st.rerun()
                    else:
                        st.warning("No other movies left in your filtered pool to spin!")

# --- TAB 2: VISUAL LIBRARY (With 3D Flip Cards & Delete Actions!) ---
with tab_library:
    st.header("📚 Your Collection")

    # 1. Search and Mode Toggle
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        search_query = st.text_input("🔍 Search movies...", "").lower()
    with col_header2:
        phone_mode = st.toggle("📱 Phone Mode", value=False)

    filtered_movies = [m for m in movies if search_query in m['title'].lower()]

    if not filtered_movies:
        st.info("No movies found in your library.")
    else:
        # Inject our responsive CSS
        st.markdown(
            """
            <style>
            .flip-card {
                background-color: transparent;
                perspective: 1000px;
            }
            .flip-card-inner {
                position: relative;
                width: 100%;
                height: 100%;
                text-align: center;
                transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                transform-style: preserve-3d;
            }
            .flip-card:hover .flip-card-inner, 
            .flip-card:active .flip-card-inner,
            .flip-card:focus .flip-card-inner {
                transform: rotateY(180deg);
            }
            .flip-card-front, .flip-card-back {
                position: absolute;
                width: 100%;
                height: 100%;
                -webkit-backface-visibility: hidden;
                backface-visibility: hidden;
                border-radius: 12px;
                overflow: hidden;
            }
            .flip-card-front img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                object-position: center;
            }
            .flip-card-back {
                background-color: #1a1a1a;
                color: #f0f0f0;
                transform: rotateY(180deg);
                padding: 14px;
                display: flex;
                flex-direction: column;
                justify-content: flex-start;
                align-items: center;
                border: 1px solid #333;
                box-sizing: border-box;
            }
            .movie-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                gap: 12px;
                width: 100%;
            }
            @media (max-width: 600px) {
                .movie-grid {
                    grid-template-columns: repeat(2, 1fr) !important;
                    gap: 10px;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # --- PHONE MODE LAYOUT ---
        if phone_mode:
            cards = []
            for idx, movie in enumerate(filtered_movies):
                poster = movie.get("poster_url")
                if not poster or poster == "N/A":
                    poster = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&q=80"

                watched_status = "✅" if movie.get("watched") else "⏳"
                plot_snippet = movie.get("plot", "No plot summary available.") or "No plot summary available."
                imdb = f"⭐ {movie.get('imdb_rating', 'N/A')}" if movie.get('imdb_rating') else "⭐ N/A"

                card_html = (
                    f'<div class="flip-card" style="width:100%; height:240px;" tabindex="0">'
                    f'<div class="flip-card-inner">'
                    f'<div class="flip-card-front"><img src="{poster}"/></div>'
                    f'<div class="flip-card-back">'
                    f'<div style="font-size:0.8rem; font-weight:bold; margin-bottom:4px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">{movie["title"]}</div>'
                    f'<div style="font-size:0.65rem; color:#888; margin-bottom:6px;">{imdb} | {movie.get("year", "N/A")}</div>'
                    f'<p style="font-size:0.65rem; line-height:1.2; text-align:left; display:-webkit-box; -webkit-line-clamp:7; -webkit-box-orient:vertical; overflow:hidden; margin:0; color:#ccc;">{plot_snippet}</p>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )
                cards.append(card_html)

            grid_html = f'<div class="movie-grid">{"".join(cards)}</div>'
            st.write(grid_html, unsafe_allow_html=True)

            # Mobile Action Drawer
            st.markdown("---")
            st.subheader("⚙️ Quick Manager")
            selected_title = st.selectbox("Choose a movie to update:", [m['title'] for m in filtered_movies])

            if selected_title:
                selected_movie = next(m for m in movies if m['title'] == selected_title)

                col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
                with col_m1:
                    m_status = "Mark Unwatched ⏳" if selected_movie.get("watched") else "Mark Watched ✅"
                    if st.button(m_status, key=f"mob_btn_{selected_title}", use_container_width=True):
                        selected_movie['watched'] = not selected_movie.get('watched', False)
                        save_movies(movies)
                        st.session_state.movies = movies
                        st.rerun()
                with col_m2:
                    m_stars = st.feedback("stars", key=f"mob_star_{selected_title}")
                    if m_stars is not None:
                        calc_rate = (m_stars + 1) * 2
                        selected_movie["rating"] = calc_rate
                        save_movies(movies)
                        st.session_state.movies = movies
                        st.rerun()
                with col_m3:
                    # Mobile Delete Button
                    if st.button("🗑️", key=f"mob_del_{selected_title}", use_container_width=True, help="Delete movie"):
                        movies.remove(selected_movie)
                        save_movies(movies)
                        st.session_state.movies = movies
                        st.toast(f"Removed {selected_movie['title']}!")
                        time.sleep(0.5)
                        st.rerun()

        # --- ORIGINAL DESKTOP LAYOUT (With sleek Side-by-side Trash Can!) ---
        else:
            cols = st.columns(4)
            for idx, movie in enumerate(filtered_movies):
                col = cols[idx % 4]
                with col:
                    poster = movie.get("poster_url")
                    if not poster or poster == "N/A":
                        poster = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&q=80"

                    plot_snippet = movie.get("plot", "No plot summary available.") or "No plot summary available."
                    imdb = f"⭐ {movie.get('imdb_rating', 'N/A')}" if movie.get('imdb_rating') else "⭐ N/A"

                    # 3D Flip Card Container
                    st.markdown(
                        f"""
                        <div class="flip-card" style="width: 100%; height: 380px;" tabindex="0">
                            <div class="flip-card-inner">
                                <div class="flip-card-front">
                                    <img src="{poster}"/>
                                </div>
                                <div class="flip-card-back">
                                    <div style="font-size: 1.05rem; font-weight: bold; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                                        {movie['title']}
                                    </div>
                                    <div style="font-size: 0.8rem; color: #ffaa00; margin-bottom: 12px; font-weight: 600;">
                                        {imdb} | {movie.get('year', 'N/A')}
                                    </div>
                                    <p style="font-size: 0.8rem; line-height: 1.4; text-align: left; display: -webkit-box; -webkit-line-clamp: 10; -webkit-box-orient: vertical; overflow: hidden; color: #ddd; margin: 0;">
                                        {plot_snippet}
                                    </p>
                                    <div style="margin-top: auto; font-size: 0.75rem; color: #888; font-style: italic;">
                                        Genre: {movie.get('genre', 'N/A')}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    watched_status = "✅" if movie.get("watched") else "⏳"
                    st.markdown(f"**{movie['title']}** ({movie.get('year', 'N/A')})")

                    # Desktop Rating
                    current_rating = movie.get("rating", 0)
                    new_stars = st.feedback("stars", key=f"desktop_stars_{idx}")

                    if new_stars is not None:
                        calculated_rating = (new_stars + 1) * 2
                        if movie.get("rating") != calculated_rating:
                            movie["rating"] = calculated_rating
                            save_movies(movies)
                            st.session_state.movies = movies
                            st.success(f"Rated {movie['title']} a {calculated_rating}/10!")
                            st.rerun()

                    rating_text = f"⭐ {movie.get('rating', 'Not Rated')}/10" if movie.get(
                        'rating') else "⏳ Not Rated yet"
                    st.write(f"{watched_status} | {rating_text}")

                    # Split controls row to put the Trash Can cleanly on the right
                    col_btn_status, col_btn_delete = st.columns([3, 1])

                    with col_btn_status:
                        btn_label = "Mark Unwatched" if movie.get("watched") else "Mark Watched"
                        if st.button(btn_label, key=f"desktop_toggle_{idx}", use_container_width=True):
                            movie['watched'] = not movie.get('watched', False)
                            save_movies(movies)
                            st.session_state.movies = movies
                            st.rerun()

                    with col_btn_delete:
                        # Desktop delete action!
                        if st.button("🗑️", key=f"desktop_delete_{idx}", use_container_width=True,
                                     help="Delete from library"):
                            movies.remove(movie)
                            save_movies(movies)
                            st.session_state.movies = movies
                            st.toast(f"Removed '{movie['title']}' from library.")
                            time.sleep(0.5)
                            st.rerun()

                    st.markdown("---")

# --- TAB 3: ADD MOVIE (With Live Preview & Confirmation!) ---
with tab_add:
    st.header("➕ Expand the Library")

    # Initialize a temporary session state variable to store the searched movie
    if "temp_movie" not in st.session_state:
        st.session_state.temp_movie = None

    method = st.radio("How would you like to add it?", ["Automatic Lookup 🌐", "Manual Entry ✍️"], horizontal=True)

    if method == "Automatic Lookup 🌐":
        # Text input and Search button
        title = st.text_input("Enter Movie Title to Search")

        if st.button("Search Movie 🔍", use_container_width=True):
            if title:
                with st.spinner("Searching OMDB..."):
                    found_movie = get_movie_data(title)

                if found_movie:
                    # Quick duplicate check
                    if any(m['title'].lower() == found_movie['title'].lower() for m in movies):
                        st.warning(f"⚠️ \"{found_movie['title']}\" is already in your library!")
                        st.session_state.temp_movie = None
                    else:
                        # Store in session state for confirmation step
                        st.session_state.temp_movie = found_movie
                else:
                    st.error("❌ Couldn't find that movie. Check the spelling or try manual entry.")
                    st.session_state.temp_movie = None
            else:
                st.warning("Please enter a title first.")

        # --- PREVIEW & CONFIRMATION STEP ---
        # If we have a movie waiting in temp storage, show the preview!
        if st.session_state.temp_movie:
            temp = st.session_state.temp_movie

            st.markdown("---")
            st.subheader("🤔 Is this the right movie?")

            col_img, col_info = st.columns([1, 2])
            with col_img:
                # Poster preview
                poster = temp.get("poster_url")
                if not poster or poster == "N/A":
                    poster = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&q=80"
                st.image(poster, use_container_width=True)

            with col_info:
                st.markdown(f"### **{temp['title']}** ({temp.get('year', 'N/A')})")
                st.markdown(f"**Genre:** {temp.get('genre', 'Unknown')}")
                st.markdown(f"**Runtime:** {temp.get('runtime', 'N/A')} mins")
                st.markdown(f"**IMDb Rating:** ⭐ {temp.get('imdb_rating', 'N/A')}/10")
                if temp.get("plot"):
                    st.write(f"*\"{temp['plot']}\"*")

                # Yes/No Confirmation Buttons
                st.write("")  # Spacing
                col_yes, col_no = st.columns(2)
                with col_yes:
                    # Using type="primary" colors this button specifically so it stands out!
                    if st.button("✅ Yes, Add to Library!", type="primary", use_container_width=True):
                        movies.append(temp)
                        save_movies(movies)
                        st.session_state.movies = movies  # Sync main state
                        st.session_state.temp_movie = None  # Clear preview
                        st.success(f"Successfully added **{temp['title']}**!")
                        st.rerun()
                with col_no:
                    if st.button("❌ No, Cancel Search", use_container_width=True):
                        st.session_state.temp_movie = None  # Clear preview
                        st.rerun()

    else:
        # Manual Entry Form
        with st.form("manual_entry_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                manual_title = st.text_input("Title")
                manual_genre = st.text_input("Genre (e.g. Comedy, Sci-Fi)")
            with col_b:
                manual_year = st.number_input("Year", min_value=1900, max_value=2030, value=2026)
                manual_runtime = st.number_input("Runtime (Minutes)", min_value=1, value=120)

            submitted = st.form_submit_button("Add Movie Manually", use_container_width=True)
            if submitted:
                if manual_title:
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