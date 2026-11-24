import streamlit as st
import requests
import time
import base64

st.set_page_config(
    page_title="BUGALEE AI STUDIO",
    page_icon="🎬",
    layout="wide"
)

API = "https://apihub.agnes-ai.com"

st.title("🎬 BUGALEE AI STUDIO")
st.subheader("Your Personal AI Movie Studio")

st.write("Create cinematic movies from your imagination.")

style = st.selectbox(
    "Movie Style",
    ["Nollywood", "Hollywood", "Realistic Cinematic",
     "Cartoon / Animation", "Anime"]
)

genre = st.selectbox(
    "Movie Genre",
    ["Drama", "Action", "Comedy", "Romance",
     "Crime / Thriller", "Horror", "Ancient Kingdom",
     "School Life", "Adventure", "Family"]
)

duration = st.selectbox(
    "Video Duration",
    [4, 5, 6, 8, 10, 12]
)

ratio = st.selectbox(
    "Video Format",
    ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]
)

story = st.text_area(
    "Describe Your Movie Scene",
    height=150
)

image_file = st.file_uploader(
    "Upload Character Reference Image (Optional)",
    type=["png", "jpg", "jpeg"]
)

st.caption("Video generation produces individual short clips.")

if st.button("🎥 GENERATE MY MOVIE", use_container_width=True):

    if not story.strip():
        st.warning("Please enter your movie scene.")

    elif "AGNES_API_KEY" not in st.secrets:
        st.error("Agnes API key has not been connected yet.")

    else:
        headers = {
            "Authorization": f"Bearer {st.secrets['AGNES_API_KEY']}",
            "Content-Type": "application/json"
        }

        prompt = f"""
        Create a professional cinematic {style} movie scene.
        Genre: {genre}.
        Scene: {story}

        Realistic human movement, expressive faces,
        detailed environment, professional camera movement,
        cinematic lighting and consistent appearance.
        No subtitles, captions or watermarks.
        """

        payload = {
            "model": "agnes-video-2.5-flash",
            "prompt": prompt,
            "mode": "text",
            "seconds": str(duration),
            "size": "720P",
            "aspect_ratio": ratio,
            "n": 1
        }

        if image_file:
            encoded = base64.b64encode(
                image_file.getvalue()
            ).decode("utf-8")

            payload["mode"] = "img2video"
            payload["first_frame"] = (
                f"data:{image_file.type};base64,{encoded}"
            )

        try:
            with st.spinner("Submitting your video request..."):
                response = requests.post(
                    f"{API}/v1/videos",
                    headers=headers,
                    json=payload,
                    timeout=120
                )

            if response.status_code not in (200, 201, 202):
                st.error(f"Agnes error: {response.text[:1000]}")
                st.stop()

            data = response.json()
            video_id = data.get("video_id")

            if not video_id:
                st.error(f"Video ID missing: {data}")
                st.stop()

            st.success("Video request submitted!")

            progress = st.progress(0)
            message = st.empty()

            video_url = None

            for attempt in range(120):

                result = requests.get(
                    f"{API}/agnesapi",
                    params={
                        "video_id": video_id,
                        "model_name": "agnes-video-2.5-flash"
                    },
                    headers=headers,
                    timeout=60
                )

                if result.status_code != 200:
                    message.warning("Checking video status...")
                    time.sleep(10)
                    continue

                status_data = result.json()
                status = status_data.get("status", "").lower()

                if status == "completed":
                    video_url = status_data.get("url")
                    break

                if status == "failed":
                    st.error(
                        f"Generation failed: "
                        f"{status_data.get('error', status_data)}"
                    )
                    st.stop()

                message.info(
                    f"Generating your movie... {status}"
                )

                progress.progress(
                    min((attempt + 1) / 120, 0.95)
                )

                time.sleep(10)

            if video_url:
                video_response = requests.get(
                    video_url,
                    timeout=180
                )
                video_response.raise_for_status()

                video_bytes = video_response.content

                progress.progress(1.0)
                st.success("Your movie is ready!")

                st.video(video_bytes)

                st.download_button(
                    "⬇️ DOWNLOAD MY MOVIE",
                    video_bytes,
                    file_name="BUGALEE_movie.mp4",
                    mime="video/mp4"
                )

            else:
                st.warning(
                    "Video is still processing. Please try again later."
                )

        except Exception as error:
            st.error(f"Error: {error}")
