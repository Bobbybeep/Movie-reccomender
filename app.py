import streamlit as st
import pickle
import pandas as pd
import requests

# -----------------------------
# Page config (modern Streamlit)
# -----------------------------
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------
# Load data (cached)
# -----------------------------
@st.cache_data
def load_data():
    movies = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

# -----------------------------
# Fetch poster from TMDB (safe + cached)
# -----------------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key=8265bd1679663a7ea12ac168da842e8&language=en-US"
        )
        response = requests.get(url, timeout=5)
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"

    except requests.exceptions.RequestException:
        pass

    # Fallback poster
    return "https://via.placeholder.com/500x750?text=No+Poster"

# -----------------------------
# Recommendation logic
# -----------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]

    movie_indices = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommendations = []
    for i in movie_indices:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommendations.append({
            "title": movies.iloc[i[0]]['title'],
            "poster": fetch_poster(movie_id)
        })

    return recommendations

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Select a movie you like",
    movies['title'].values
)

if st.button("Recommend 🎯"):
    results = recommend(selected_movie)

    cols = st.columns(5)

    for col, movie in zip(cols, results):
        with col:
            st.image(movie["poster"], use_column_width=True)
            st.markdown(
                f"<p style='text-align:center; font-weight:600;'>{movie['title']}</p>",
                unsafe_allow_html=True
            )
