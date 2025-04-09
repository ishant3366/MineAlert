import streamlit as st
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Simple Map Test",
    layout="wide"
)

# Title
st.title("Simple Map Test")
st.markdown("Testing map functionality")

# Create a map
m = folium.Map(
    location=[34.0522, -118.2437],  # Los Angeles
    zoom_start=12
)

# Add a marker
folium.Marker(
    [34.0522, -118.2437],
    popup="Test Marker",
    icon=folium.Icon(icon="info", color="blue")
).add_to(m)

# Display the map
try:
    st_folium(m, width=700, height=500)
except Exception as e:
    st.error(f"Error displaying map: {e}")