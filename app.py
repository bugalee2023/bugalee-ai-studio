import streamlit as st

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
</style>
""", unsafe_allow_html=True)

st.title("🎬 BUGALEE AI STUDIO")
st.markdown("### Your Personal AI Movie Production Studio")
st.write("Turn your imagination into cinematic movies.")

st.divider()

st.header("🎥 Create Your Movie")

story = st.text_area(
    "Enter Your Movie Story",
    placeholder="Write your complete movie story here...",
    height=200
)

st.subheader("👥 Upload Your Characters")

characters = st.file_uploader(
    "Upload character pictures",
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
    "Choose Movie Duration",
    [
        "20 Seconds",
        "30 Seconds",
        "1 Minute",
        "5 Minutes",
        "10 Minutes",
        "20 Minutes",
        "30 Minutes",
        "1 Hour",
        "2 Hours"
    ]
)

video_format = st.selectbox(
    "Choose Video Format",
    [
        "YouTube Landscape (16:9)",
        "YouTube Shorts (9:16)",
        "Square (1:1)"
    ]
)

language = st.selectbox(
    "Movie Language",
    ["English", "Nigerian Pidgin", "French", "Spanish"]
)

style = st.selectbox(
    "Movie Style",
    [
        "Realistic Nollywood Movie",
        "Hollywood Cinematic",
        "African Traditional Movie",
        "School Drama",
        "Romance",
        "Comedy",
        "Action"
    ]
)

st.divider()

if st.button("🎬 GENERATE MY MOVIE", use_container_width=True):
    if not story.strip():
        st.error("Please enter your movie story first.")
    else:
        st.success("Your movie project is ready for the next stage!")

        st.write("Duration:", duration)
        st.write("Video Format:", video_format)
        st.write("Language:", language)
        st.write("Movie Style:", style)
        st.write("Characters uploaded:", len(characters or []))

        st.info(
            "The video-generation engine has not been connected yet. "
            "This is the first working interface of BUGALEE AI STUDIO."
        )

st.divider()

st.caption("© BUGALEE TV | BUGALEE AI STUDIO")
