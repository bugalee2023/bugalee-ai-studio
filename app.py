import streamlit as st
import tempfile
import os
import subprocess
import imageio_ffmpeg
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
    "Enter Your Movie Story",
    height=180,
    placeholder="Describe your movie story here..."
)

characters = st.file_uploader(
    "Upload Your Main Character Picture",
    type=["png", "jpg", "jpeg"]
)

st.subheader("⚙️ Movie Settings")

duration = st.selectbox(
    "Choose Your Movie Duration",
    [4, 6, 10, 30],
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
            with tempfile.TemporaryDirectory() as temp_dir:

                if characters:
                    image_path = os.path.join(
                        temp_dir,
                        characters.name
                    )

                    with open(image_path, "wb") as f:
                        f.write(characters.getvalue())

                if video_format == "YouTube Landscape":
                    height, width = 832, 1472
                else:
                    height, width = 1472, 832

                clip_duration = 2
                total_clips = duration // clip_duration

                st.info(
                    f"Your {duration}-second movie will be "
                    f"created using {total_clips} short clips."
                )

                progress = st.progress(0)

                clip_paths = []

                client = Client("Lightricks/LTX-2.5")

                for i in range(total_clips):

                    prompt = f"""
                    Create a realistic cinematic Nollywood movie scene.

                    Complete story:
                    {story}

                    This is scene {i + 1} of {total_clips}.
                    Continue the same story and show the next moment.
                    Maintain the same character appearance and clothing.
                    Natural lighting, realistic movements,
                    professional movie cinematography.
                    """

                    with st.spinner(
                        f"Generating scene {i + 1} of {total_clips}..."
                    ):

                        result = client.predict(
                            prompt,
                            handle_file(image_path)
                            if image_path else None,
                            height,
                            width,
                            float(clip_duration),
                            42,
                            "conv",
                            False,
                            True,
                            False,
                            api_name="/run"
                        )

                    video_file = result[0]

                    if not isinstance(video_file, str):
                        raise Exception(
                            "The video generator returned an unexpected result."
                        )

                    if not os.path.exists(video_file):
                        raise Exception(
                            "The generated video file could not be found."
                        )

                    clip_path = os.path.join(
                        temp_dir,
                        f"clip_{i:03d}.mp4"
                    )

                    with open(video_file, "rb") as source:
                        with open(clip_path, "wb") as target:
                            target.write(source.read())

                    clip_paths.append(clip_path)

                    progress.progress(
                        (i + 1) / total_clips
                    )

                concat_file = os.path.join(
                    temp_dir,
                    "clips.txt"
                )

                with open(concat_file, "w") as f:
                    for clip in clip_paths:
                        safe_path = clip.replace("\\", "/")
                        f.write(f"file '{safe_path}'\n")

                output_video = os.path.join(
                    temp_dir,
                    "BUGALEE_MOVIE.mp4"
                )

                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

                with st.spinner("Joining all scenes into one movie..."):

                    subprocess.run(
                        [
                            ffmpeg,
                            "-y",
                            "-f", "concat",
                            "-safe", "0",
                            "-i", concat_file,
                            "-c:v", "libx264",
                            "-preset", "veryfast",
                            "-crf", "23",
                            "-c:a", "aac",
                            "-movflags", "+faststart",
                            output_video
                        ],
                        check=True,
                        capture_output=True,
                        text=True
                    )

                st.success("Your movie is ready!")

                st.video(output_video)

                with open(output_video, "rb") as f:
                    st.download_button(
                        "⬇️ DOWNLOAD MY MOVIE",
                        data=f,
                        file_name="BUGALEE_MOVIE.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"Movie generation failed: {e}")

st.divider()

st.caption("© BUGALEE TV | BUGALEE AI STUDIO")
