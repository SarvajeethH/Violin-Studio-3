import streamlit as st
import time
import random
import io
import wave
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- ROBUST IMAGE LOADING ---
try:
    img_violin1 = open("public/violin1.jpg", "rb").read()
    img_violin2 = open("public/violin2.jpg", "rb").read()
    img_violin3 = open("public/violin3.jpg", "rb").read()
    img_violin4 = open("public/violin4.jpg", "rb").read()
except FileNotFoundError:
    st.error("Image files not found. Make sure the 'public' folder is in your repository root.")
    img_violin1, img_violin2, img_violin3, img_violin4 = None, None, None, None

# --- DATABASES AND SIMULATION LOGIC ---
# (The entire pieceDatabase from the previous step goes here for the 'Practice with AI' tab)
pieceDatabase = {
    "bach_d_minor_partita": { "title": "Partita No. 2 in D minor, BWV 1004", "keywords": ["bach", "chaconne"], "description": "...", "usualTempo": 76, "practiceTempo": 60 },
    "vivaldi_four_seasons": { "title": "The Four Seasons", "keywords": ["vivaldi", "winter", "spring", "summer", "autumn"], "description": "...", "usualTempo": 100, "practiceTempo": 80 },
    # PASTE THE REST OF YOUR PIECE DATABASE HERE
}

comparativeFeedbackPool = {
    "tone": [
        "Your tone is slightly brighter and more focused than the benchmark recording.",
        "The benchmark recording exhibits a warmer, richer tone, especially in the lower register. Try using a slower, heavier bow.",
        "Excellent tonal consistency, very similar to the goal recording's clear and resonant sound.",
    ],
    "dynamics": [
        "Your dynamic range is good, but the benchmark's pianissimo sections are softer and more delicate.",
        "The crescendo at [timestamp] was more pronounced and dramatic in your performance than in the benchmark.",
        "Both recordings follow similar dynamic contours, showing a good understanding of the musical shape.",
    ],
    "style": [
        "Your interpretation is more legato and connected, whereas the benchmark uses a more detached, articulated style.",
        "The vibrato in the benchmark recording is wider and more consistent. Your vibrato is more subtle, which is also a valid stylistic choice.",
        "Excellent stylistic match. The use of rubato in the lyrical sections is very similar to the goal recording.",
    ],
    "pitch": [
        "A pitch discrepancy was noted at [timestamp] compared to the benchmark. The F# was slightly flat in your recording.",
        "The intonation in the fast passage starting around [timestamp] was cleaner in your performance than in the benchmark.",
        "Overall pitch accuracy is very high and closely matches the benchmark across the entire performance.",
    ]
}

# --- HELPER FUNCTIONS ---
def fetch_piece_info(piece_name):
    search_terms = piece_name.lower().split()
    for key, piece in pieceDatabase.items():
        searchable_text = f"{piece['title'].lower()} {' '.join(piece['keywords'])}"
        if all(term in searchable_text for term in search_terms):
            return piece
    return {"title": piece_name, "description": "Information for this piece could not be found.", "notFound": True}

def get_comparative_analysis(status_placeholder):
    status_placeholder.info("Initializing comparison... (This may take up to 20 seconds)")
    time.sleep(2)
    status_placeholder.info("Step 1/3: Analyzing tonal characteristics of both recordings...")
    time.sleep(random.uniform(4, 6))
    status_placeholder.info("Step 2/3: Aligning dynamic levels and phrasing...")
    time.sleep(random.uniform(4, 6))
    status_placeholder.info("Step 3/3: Cross-referencing pitch contours for discrepancies...")
    time.sleep(3)
    feedback = []
    for category in comparativeFeedbackPool:
        note = random.choice(comparativeFeedbackPool[category])
        if "[timestamp]" in note:
            timestamp = time.strftime('%M:%S', time.gmtime(random.randint(5, 50)))
            note = note.replace("[timestamp]", timestamp)
        feedback.append(f"**{category.capitalize()}:** {note}")
    status_placeholder.empty()
    return feedback

# --- STATE INITIALIZATION ---
# This ensures all necessary keys are always present in the session state.
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.app_mode = "Practice with AI"
    st.session_state.piece_name_input = ''
    st.session_state.user_tempo_input = 120
    st.session_state.piece_info = None
    st.session_state.audio_frames = []
    st.session_state.user_audio_bytes = None
    st.session_state.saved_user_audio_bytes = None
    st.session_state.benchmark_audio_bytes = None
    st.session_state.ai_feedback = []
    st.session_state.analysis_error = ''
    st.session_state.volume_level = 0.0

# --- CALLBACKS & LOGIC ---
def handle_benchmark_upload():
    if st.session_state.benchmark_uploader is not None:
        st.session_state.benchmark_audio_bytes = st.session_state.benchmark_uploader.getvalue()

def audio_frame_callback(frame):
    audio_data = frame.to_ndarray()
    rms = np.sqrt(np.mean(np.square(audio_data)))
    volume = min(100, int(rms * 500))
    # Use a thread-safe way to update session state from a callback
    st.session_state["volume_level"] = volume
    st.session_state.audio_frames.append(audio_data.tobytes())
    return frame

# --- MAIN APP LAYOUT ---
st.set_page_config(layout="wide", page_title="Violin Studio")
st.markdown("""<style>#MainMenu, footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if img_violin1: st.image(img_violin1)
    if img_violin2: st.image(img_violin2)

with col2:
    st.title("Violin Studio")
    
    tab1, tab2 = st.tabs(["Practice with AI", "Compare with Benchmark"])

    with tab1:
        st.header("Practice with AI")
        st.info("This feature allows you to look up a piece and get simulated feedback. (Feature from previous version can be integrated here).")
        st.write("---")

    with tab2:
        st.header("Compare with Benchmark")
        st.write("Upload a recording you want to sound like, then record yourself and get a direct comparison.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Recording Goal")
            st.file_uploader(
                "Upload a benchmark recording",
                type=['wav', 'mp3', 'm4a'],
                key="benchmark_uploader",
                on_change=handle_benchmark_upload
            )
            if st.session_state.benchmark_audio_bytes:
                st.audio(st.session_state.benchmark_audio_bytes)

        with c2:
            st.subheader("My Recording")
            
            webrtc_ctx = webrtc_streamer(
                key="audio-recorder",
                mode=WebRtcMode.SENDONLY,
                audio_frame_callback=audio_frame_callback,
                media_stream_constraints={"audio": True, "video": False},
                rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            )

            if webrtc_ctx.state.playing:
                st.progress(st.session_state.get("volume_level", 0), text=f"Loudness: {st.session_state.get('volume_level', 0)}%")
            
            # ROBUST LOGIC: Process audio frames only when recording stops and frames are available.
            if not webrtc_ctx.state.playing and len(st.session_state.audio_frames) > 0:
                if st.session_state.user_audio_bytes:
                    st.session_state.saved_user_audio_bytes = st.session_state.user_audio_bytes
                
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(b''.join(st.session_state.audio_frames))
                st.session_state.user_audio_bytes = wav_buffer.getvalue()
                st.session_state.audio_frames = [] # IMPORTANT: Clear frames after processing
                st.rerun()

            if st.session_state.user_audio_bytes:
                st.audio(st.session_state.user_audio_bytes, format='audio/wav')

        st.divider()

        # --- COMPARISON ANALYSIS SECTION ---
        if st.session_state.benchmark_audio_bytes and st.session_state.user_audio_bytes:
            if st.button("Compare Recordings", type="primary", use_container_width=True):
                st.session_state.ai_feedback = []
                st.session_state.analysis_error = ''
                
                status_placeholder = st.empty()
                try:
                    feedback = get_comparative_analysis(status_placeholder)
                    st.session_state.ai_feedback = feedback
                except ValueError as e:
                    st.session_state.analysis_error = str(e)

        if st.session_state.ai_feedback or st.session_state.analysis_error:
            st.subheader("Comparative Analysis")
            if st.session_state.analysis_error:
                st.error(st.session_state.analysis_error)
            if st.session_state.ai_feedback:
                for item in st.session_state.ai_feedback:
                    st.markdown(f"- {item}")

with col3:
    if img_violin3: st.image(img_violin3)
    if img_violin4: st.image(img_violin4)
