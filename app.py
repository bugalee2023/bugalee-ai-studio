import streamlit as st
import tempfile
import os
import subprocess
import math
import imageio_ffmpeg
from gradio_client import Client, handle_file

st.set_page_config(
    page_title="BUGALEE AI STUDIO",
    page_icon="🎬",
    layout="wide"
)

@st.cache_resource
def get_client():
    return Client("Lightricks/LTX-2.5")

st.title("🎬 BUGALEE AI STUDIO")
st.subheader("Your Personal AI Movie Production Studio")
st.write("Create cinematic movies with your imagination.")

st.divider()

st.header("🎥 CREATE YOUR MOVIE")

story = st.text_area(
    "Enter Your Movie Story",
    height=180,
    placeholder="Write your movie story here..."
)

characters = st.file_uploader(
    "Upload Your Character Picture",
    type=["png", "jpg", "jpeg"]
)

st.divider()

st.header("🎨 MOVIE STYLE")

movie_style = st.selectbox(
    "Choose Movie Style",
    [
        "Nollywood",
        "Hollywood",
        "Cartoon / Animation",
        "Anime",
        "Realistic Cinematic"
    ]
)

genre = st.selectbox(
    "Choose Movie Genre",
    [
        "Action",
        "Comedy",
        "Romance",
        "Drama",
        "Crime / Thriller",
        "Horror",
        "Ancient Kingdom",
        "School Life",
        "Adventure",
        "Family"
    ]
)

st.divider()

st.header("⚙️ VIDEO SETTINGS")

duration = st.selectbox(
    "Choose Movie Duration",
    [10, 15, 20, 25, 30],
    format_func=lambda x: f"{x} seconds"
)

video_format = st.selectbox(
    "Choose Video Size",
    [
        "16:9 - YouTube Landscape",
        "9:16 - TikTok / Shorts",
        "1:1 - Square",
        "4:5 - Portrait",
        "21:9 - Cinematic Wide",
        "4:3 - Classic Television"
    ]
)

sizes = {
    "16:9 - YouTube Landscape": (832, 1472),
    "9:16 - TikTok / Shorts": (1472, 832),
    "1:1 - Square": (1024, 1024),
    "4:5 - Portrait": (1152, 896),
    "21:9 - Cinematic Wide": (640, 1536),
    "4:3 - Classic Television": (832, 1152)
}

st.divider()

st.caption(
    "Longer videos require multiple generations. "
    "Availability depends on the video generator's GPU limits."
)

if st.button(
    "🎬 GENERATE MY MOVIE",
    use_container_width=True
):

    if not story.strip():
        st.error("Please enter your movie story.")

    else:

        try:

            with tempfile.TemporaryDirectory() as temp_dir:

                image_path = None

                if characters:

                    image_path = os.path.join(
                        temp_dir,
                        "character.png"
                    )

                    with open(image_path, "wb") as f:
                        f.write(characters.getvalue())

                height, width = sizes[video_format]

                clip_duration = 2.0

                total_clips = math.ceil(
                    duration / clip_duration
                )

                actual_clip_duration = (
                    duration / total_clips
                )

                st.info(
                    f"Your {duration}-second project "
                    f"requires {total_clips} video clips."
                )

                progress = st.progress(0)

                clip_paths = []

                client = get_client()

                for i in range(total_clips):

                    prompt = f"""
                    Create a cinematic movie scene.

                    MOVIE STYLE: {movie_style}

                    MOVIE GENRE: {genre}

                    COMPLETE MOVIE STORY:
                    {story}

                    SCENE NUMBER: {i + 1} of {total_clips}

                    Show the next moment in the story.
                    Maintain the same main character appearance,
                    face, clothing and identity.

                    Make the scene visually engaging.
                    Use realistic movements and professional
                    cinematography.

                    For action scenes, use cinematic action
                    without graphic injuries or gore.

                    No subtitles, no captions, no watermarks.
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
                            float(actual_clip_duration),
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
                            "Unexpected video result."
                        )

                    if not os.path.exists(video_file):
                        raise Exception(
                            "Generated video file not found."
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

                        f.write(
                            f"file '{safe_path}'\n"
                        )

                output_video = os.path.join(
                    temp_dir,
                    "BUGALEE_MOVIE.mp4"
                )

                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

                with st.spinner(
                    "Joining all scenes into one movie..."
                ):

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

                with open(output_video, "rb") as f:
                    final_video = f.read()

            st.success("🎉 YOUR MOVIE IS READY!")

            st.video(final_video)

            st.download_button(
                "⬇️ DOWNLOAD MY MOVIE",
                data=final_video,
                file_name="BUGALEE_MOVIE.mp4",
                mime="video/mp4",
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Movie generation failed: {e}"
            )

st.divider()

st.caption("© BUGALEE TV | BUGALEE AI STUDIO")
