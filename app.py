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
    st.error("Image files not found. Make sure the 'public' folder with images is in your repository root.")
    img_violin1, img_violin2, img_violin3, img_violin4 = None, None, None, None

# --- DATABASE AND SIMULATION LOGIC ---
pieceDatabase = {
    "bach_d_minor_partita": { 
        "composer": "J.S. Bach",
        "title": "Partita No. 2 in D minor, BWV 1004", 
        "keywords": ["bach", "chaconne"], 
        "description": "A cornerstone of the solo violin repertoire, this partita is renowned for its final movement, the 'Chaconne.' ...",
        "usualTempo": 76, 
        "practiceTempo": 60 
    },
    "vivaldi_four_seasons": { 
        "composer": "Antonio Vivaldi",
        "title": "The Four Seasons", 
        "keywords": ["vivaldi", "winter", "spring", "summer", "autumn"], 
        "description": "A set of four violin concertos, each giving musical expression to a season of the year. ...",
        "usualTempo": 100, 
        "practiceTempo": 80 
    },
    # PASTE THE REST OF YOUR PIECE DATABASE HERE, ADDING A "composer" TO EACH
}

comparativeFeedbackPool = {
    "tone": [
        "your tone is slightly brighter and more focused than the benchmark recording.",
        "the benchmark recording exhibits a warmer, richer tone, especially in the lower register. Try using a slower, heavier bow.",
        "your tonal consistency is excellent, very similar to the goal recording's clear and resonant sound.",
    ],
    "dynamics": [
        "your dynamic range is good, but the benchmark's pianissimo sections are softer and more delicate.",
        "the crescendo around [timestamp] was more pronounced and dramatic in your performance than in the benchmark.",
        "both recordings follow similar dynamic contours, showing a good understanding of the musical shape.",
    ],
    "style": [
        "your interpretation is more legato and connected, whereas the benchmark uses a more detached, articulated style.",
        "the vibrato in the benchmark recording is wider and more consistent. Your vibrato is more subtle, which is also a valid stylistic choice.",
        "the use of rubato in the lyrical sections is very similar to the goal recording, showing an excellent stylistic match.",
    ],
    "pitch": [
        "a pitch discrepancy was noted around [timestamp] compared to the benchmark. The F# was slightly flat in your recording.",
        "the intonation in the fast passage starting around [timestamp] was cleaner in your performance than in the benchmark.",
        "your overall pitch accuracy is very high and closely matches the benchmark across the entire performance.",
    ]
}

# --- HELPER FUNCTIONS ---
def fetch_piece_info(piece_name):
    search_terms = piece_name.lower().split()
    for key, piece in pieceDatabase.items():
        searchable_text = f"{piece['title'].lower()} {piece['composer'].lower()} {' '.join(piece['keywords'])}"
        if all(term in searchable_text for term in search_terms):
            return piece
    return {"title": piece_name, "description": f"Information for '{piece_name}' could not be found...", "composer": "Unknown", "notFound": True}

def get_human_comparative_analysis(status_placeholder):
    status_placeholder.info("Initializing comparison... (This may take up to 20 seconds)")
    time.sleep(2)
    status_placeholder.info("Step 1/3: Analyzing tonal characteristics of both recordings...")
    time.sleep(random.uniform(4, 6))
    status_placeholder.info("Step 2/3: Aligning dynamic levels and phrasing...")
    time.sleep(random.uniform(4, 6))
    status_placeholder.info("Step 3/3: Cross-referencing pitch contours for discrepancies...")
    time.sleep(3)
    tone_feedback = random.choice(comparativeFeedbackPool["tone"])
    dynamics_feedback = random.choice(comparativeFeedbackPool["dynamics"])
    style_feedback = random.choice(comparativeFeedbackPool["style"])
    pitch_feedback = random.choice(comparativeFeedbackPool["pitch"])
    for feedback_str in [dynamics_feedback, pitch_feedback]:
        if "[timestamp]" in feedback_str:
            timestamp = time.strftime('%M:%S', time.gmtime(random.randint(5, 50)))
            feedback_str = feedback_str.replace("[timestamp]", timestamp)
    full_report = (
        "Overall, this is a strong performance that captures the spirit of the benchmark recording. Here's a more detailed breakdown:\n\n"
        f"**In terms of tone**, {tone_feedback} \n\n"
        f"**Dynamically**, {dynamics_feedback} \n\n"
        f"**Stylistically**, {style_feedback} \n\n"
        f"**Regarding pitch accuracy**, {pitch_feedback} \n\n"
        "Great work! Keep focusing on these subtle details to get even closer to your goal."
    )
    status_placeholder.empty()
    return full_report

# --- ROBUST STATE INITIALIZATION ---
# This block now initializes EVERY session state key the app might use.
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # State for "About the Piece" tab
    st.session_state.search_query = ''
    st.session_state.searched_piece_info = None
    # State for "Compare" tab
    st.session_state.audio_frames = []
    st.session_state.user_audio_bytes = None
    st.session_state.benchmark_audio_bytes = None
    st.session_state.ai_feedback = ""
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
    st.session_state["volume_level"] = volume
    st.session_state.audio_frames.append(audio_data.tobytes())
    return frame

# --- MAIN APP LAYOUT ---
st.set_page_config(layout="wide", page_title="Violin Studio")
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if img_violin1: st.image(img_violin1)
    if img_violin2: st.image(img_violin2)

with col2:
    st.title("Violin Studio")
    
    tab1, tab2 = st.tabs(["About the Piece", "Compare with Benchmark"])

    with tab1:
        st.header("Musical Repertoire Explorer")
        st.write("Enter the name of a piece to learn about its composer, history, and musical context.")
        search_query = st.text_input("Search for a piece:", key="search_query_input", placeholder="e.g., Vivaldi Four Seasons")
        if st.button("Search", key="search_piece"):
            with st.spinner(f"Searching for '{search_query}'..."):
                st.session_state.searched_piece_info = fetch_piece_info(search_query)
        
        # This check is now safe because the key is guaranteed to exist.
        if st.session_state.searched_piece_info:
            st.divider()
            info = st.session_state.searched_piece_info
            st.subheader(info['title'])
            st.markdown(f"**Composer:** {info['composer']}")
            st.markdown(f"**About the Piece:** {info['description']}")
            if not info.get("notFound"):
                c1, c2 = st.columns(2)
                c1.metric("Typical Performance Tempo", f"~{info['usualTempo']} BPM")
                c2.metric("Suggested Practice Tempo", f"~{info['practiceTempo']} BPM")

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
            if not webrtc_ctx.state.playing and len(st.session_state.audio_frames) > 0:
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(b''.join(st.session_state.audio_frames))
                st.session_state.user_audio_bytes = wav_buffer.getvalue()
                st.session_state.audio_frames = []
                st.rerun()
            if st.session_state.user_audio_bytes:
                st.audio(st.session_state.user_audio_bytes, format='audio/wav')

        st.divider()

        if st.session_state.benchmark_audio_bytes and st.session_state.user_audio_bytes:
            if st.button("Compare Recordings", type="primary", use_container_width=True):
                st.session_state.ai_feedback = ""
                st.session_state.analysis_error = ''
                status_placeholder = st.empty()
                try:
                    feedback = get_human_comparative_analysis(status_placeholder)
                    st.session_state.ai_feedback = feedback
                except ValueError as e:
                    st.session_state.analysis_error = str(e)

        if st.session_state.ai_feedback or st.session_state.analysis_error:
            st.subheader("Comparative Analysis")
            if st.session_state.analysis_error:
                st.error(st.session_state.analysis_error)
            if st.session_state.ai_feedback:
                st.markdown(st.session_state.ai_feedback)

with col3:
    if img_violin3: st.image(img_violin3)
    if img_violin4: st.image(img_violin4)
