import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Create the Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)


def load_movies():
    # Read the data from Google Sheets (cached for 2 seconds to make transitions snappy)
    df = conn.read(ttl="2s")
    # Convert empty/NaN values to None so Python handles them cleanly
    df = df.fillna(value="")

    # Convert the DataFrame back into our familiar list of dictionaries
    movies = df.to_dict(orient="records")

    # Clean up types (convert 'watched' column to actual booleans)
    for m in movies:
        m["watched"] = bool(m["watched"]) if m.get("watched") != "" else False
        m["rating"] = int(m["rating"]) if m.get("rating") != "" else None
        m["imdb_rating"] = float(m["imdb_rating"]) if m.get("imdb_rating") != "" else 0.0
        m["runtime"] = int(m["runtime"]) if m.get("runtime") != "" else 0
        m["year"] = int(m["year"]) if m.get("year") != "" else 0

    return movies


def save_movies(movies_list):
    # Convert list of dicts back to a DataFrame
    df = pd.DataFrame(movies_list)

    # Write the entire DataFrame back to the Google Sheet instantly!
    conn.update(data=df)

    # Clear the local Streamlit cache so the changes show up immediately on reload
    st.cache_data.clear()