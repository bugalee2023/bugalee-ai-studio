import streamlit as st
import tempfile
import os
from gradio_client import Client, handle_file

st.set_page_config(
    page_title="BUGALEE AI STUDIO",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 BUGALEE AI STUDIO")
st.subheader("Your Personal AI Movie Production Studio")

st.write("Turn your imagination into cinematic movies.")

st.divider()

st.header("🎥 Create Your Movie")

story = st.text_area(
    "Enter Your Movie Story or Scene Description",
    height=180,
    placeholder="Describe what happens in your scene..."
)

characters = st.file_uploader(
    "Upload Your Character Picture",
    type=["png", "jpg", "jpeg"]
)

st.subheader("⚙️ Movie Settings")

duration = st.selectbox(
    "Video Duration",
    [2, 3, 4, 5],
    index=0,
    format_func=lambda x: f"{x} seconds"
)

video_format = st.selectbox(
    "Video Format",
    ["YouTube Landscape", "Portrait"]
)

if st.button("🎬 GENERATE MY MOVIE", use_container_width=True):

    if not story.strip():
        st.error("Please enter your movie story.")
    else:
        image_path = None

        try:
            if characters:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".png"
                ) as temp:
                    temp.write(characters.getvalue())
                    image_path = temp.name

            if video_format == "YouTube Landscape":
                height, width = 832, 1472
            else:
                height, width = 1472, 832

            with st.spinner(
                "Connecting to LTX-2.5... Your video is being generated."
            ):

                client = Client("Lightricks/LTX-2.5")

                result = client.predict(
                    story,
                    handle_file(image_path) if image_path else None,
                    height,
                    width,
                    float(duration),
                    42,
                    "conv",
                    False,
                    True,
                    False,
                    api_name="/run"
                )

            st.success("Your video is ready!")

            st.video(result[0])

            st.write("**Generated prompt:**", result[1])
            st.write("**Video length:**", result[3])

        except Exception as e:
            st.error(f"Video generation failed: {e}")

        finally:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

st.divider()

st.caption("© BUGALEE TV | BUGALEE AI STUDIO")
