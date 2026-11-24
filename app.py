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
MODEL = "agnes-video-2.5-flash"

st.title("🎬 BUGALEE AI STUDIO")
st.subheader("Your Personal AI Movie Studio")

st.write("Create cinematic movies from your imagination.")

style = st.selectbox(
    "Movie Style",
    [
        "Nollywood",
        "Hollywood",
        "Realistic Cinematic",
        "Cartoon / Animation",
        "Anime"
    ]
)

genre = st.selectbox(
    "Movie Genre",
    [
        "Drama",
        "Action",
        "Comedy",
        "Romance",
        "Crime / Thriller",
        "Horror",
        "Ancient Kingdom",
        "School Life",
        "Adventure",
        "Family"
    ]
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

st.caption(
    "Create cinematic short clips with optional character images."
)


def show_api_error(response):
    try:
        error_data = response.json()
        st.error(f"Agnes error: {error_data}")
    except ValueError:
        st.error(f"Agnes error: {response.text[:1000]}")


def submit_video(headers, payload):

    wait_times = [30, 60, 120, 180]

    for attempt in range(5):

        response = requests.post(
            f"{API}/v1/videos",
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code in (200, 201, 202):
            return response

        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        error_code = error_data.get("code", "")

        if error_code == "video_queue_full":

            if attempt == 4:
                st.error(
                    "Agnes video servers are still full. "
                    "Please try again later."
                )
                return None

            wait_seconds = wait_times[attempt]

            st.warning(
                f"Agnes queue is full. "
                f"Automatic retry {attempt + 1}/4 "
                f"in {wait_seconds} seconds."
            )

            time.sleep(wait_seconds)
            continue

        if response.status_code in (408, 429, 500, 502, 503, 504):

            if attempt == 4:
                show_api_error(response)
                return None

            wait_seconds = wait_times[attempt]

            st.warning(
                f"Temporary server problem. "
                f"Retrying in {wait_seconds} seconds."
            )

            time.sleep(wait_seconds)
            continue

        show_api_error(response)
        return None

    return None


if st.button(
    "🎥 GENERATE MY MOVIE",
    use_container_width=True
):

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

Scene description: {story}

Use realistic human movement, expressive facial
expressions, natural body movement, detailed environments,
professional camera movement and cinematic lighting.

Maintain consistent character appearance.

No subtitles, captions, written text or watermarks.
"""

        payload = {
            "model": MODEL,
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

            with st.spinner(
                "Connecting to Agnes AI..."
            ):

                response = submit_video(
                    headers,
                    payload
                )

            if response is None:
                st.stop()

            data = response.json()

            video_id = data.get("video_id")

            if not video_id:
                st.error(f"Video ID missing: {data}")
                st.stop()

            st.success(
                "Your video request has been accepted!"
            )

            st.info(
                "Your movie is now being generated. "
                "Please keep this page open."
            )

            progress = st.progress(0)
            message = st.empty()

            video_url = None

            for attempt in range(120):

                result = requests.get(
                    f"{API}/agnesapi",
                    params={
                        "video_id": video_id,
                        "model_name": MODEL
                    },
                    headers=headers,
                    timeout=60
                )

                if result.status_code != 200:

                    message.warning(
                        "Checking your video status..."
                    )

                    time.sleep(10)
                    continue

                status_data = result.json()

                status = str(
                    status_data.get("status", "")
                ).lower()

                current_progress = status_data.get(
                    "progress", 0
                )

                if status in (
                    "completed",
                    "succeeded",
                    "success",
                    "done"
                ):

                    video_url = status_data.get("url")
                    break

                if status in (
                    "failed",
                    "error",
                    "cancelled"
                ):

                    st.error(
                        f"Video generation failed: "
                        f"{status_data.get('error', status_data)}"
                    )

                    st.stop()

                message.info(
                    f"Generating your movie... "
                    f"Status: {status or 'Processing'}"
                )

                try:
                    progress.progress(
                        min(
                            int(current_progress) / 100,
                            0.95
                        )
                    )
                except (ValueError, TypeError):
                    pass

                time.sleep(10)

            if video_url:

                message.info(
                    "Your video is ready. Downloading..."
                )

                video_response = requests.get(
                    video_url,
                    timeout=180
                )

                video_response.raise_for_status()

                video_bytes = video_response.content

                progress.progress(1.0)

                st.success(
                    "🎉 YOUR MOVIE IS READY!"
                )

                st.video(video_bytes)

                st.download_button(
                    "⬇️ DOWNLOAD MY MOVIE",
                    video_bytes,
                    file_name="BUGALEE_movie.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

            else:

                st.warning(
                    "Your video is taking longer than expected. "
                    "Please check again later."
                )

        except requests.exceptions.Timeout:

            st.error(
                "The connection timed out. "
                "Please try again."
            )

        except requests.exceptions.RequestException as error:

            st.error(
                f"Network error: {error}"
            )

        except Exception as error:

            st.error(
                f"Unexpected error: {error}"
)
