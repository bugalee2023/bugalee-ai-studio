import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="BUGALEE AI STUDIO",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #101522;
    color: white;
}
h1 {
    color: #F5C542;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: #cccccc;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 BUGALEE AI STUDIO")

st.markdown(
    '<p class="subtitle">Your Personal AI Movie Production Studio</p>',
    unsafe_allow_html=True
)

st.divider()

st.header("🎥 Create Your Movie")

story = st.text_area(
    "Enter Your Movie Story",
    placeholder="Write your complete movie story here...",
    height=200
)

st.subheader("👥 Upload Your Characters")

characters = st.file_uploader(
    "Upload character reference pictures",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if characters:
    cols = st.columns(4)
    for i, file in enumerate(characters):
        with cols[i % 4]:
            st.image(file, caption=file.name, use_container_width=True)

st.divider()

st.subheader("⚙️ Movie Settings")

duration = st.selectbox(
   
