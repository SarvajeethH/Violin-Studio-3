import streamlit as st
import time
import random
import io
import wave
import numpy as np
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from pathlib import Path # Import the pathlib library

# --- ROBUST IMAGE & ASSET LOADING using pathlib ---
# This creates a reliable path to your files, no matter where the script is run from.
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"

try:
    img_violin1 = open(PUBLIC_DIR / "violin1.jpg", "rb").read()
    img_violin2 = open(PUBLIC_DIR / "violin2.jpg", "rb").read()
    img_violin3 = open(PUBLIC_DIR / "violin3.jpg", "rb").read()
    img_violin4 = open(PUBLIC_DIR / "violin4.jpg", "rb").read()
except FileNotFoundError as e:
    st.error(f"Asset file not found: {e.filename}. Please ensure the 'public' folder with your images is in the same directory as app.py.")
    st.stop() # Stop the app if essential assets are missing

# --- DATABASE (for "About the Piece" tab) ---
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
    # PASTE THE REST OF YOUR PIECE DATABASE HERE
}

comparativeFeedbackPool = {
    # This dictionary remains unchanged
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
def analyze_audio_features(audio_bytes):
    if not audio_bytes: return None
    try:
        with io.BytesIO(audio_bytes) as wav_f:
            with wave.open(wav_f, 'rb') as wf:
                n_frames = wf.getnframes()
                if n_frames == 0: return None
                frames = wf.readframes(n_frames)
                framerate = wf.getframerate()
                audio_array = np.frombuffer(frames, dtype=np.int16)
                normalized_audio = audio_array / 32768.0
                return {
                    "waveform": normalized_audio, "framerate": framerate,
                    "duration": n_frames / float(framerate),
                    "avg_amplitude": np.mean(np.abs(normalized_audio)),
                    "peak_amplitude": np.max(np.abs(normalized_audio)),
                    "dynamic_range": np.max(np.abs(normalized_audio)) - np.min(np.abs(normalized_audio)),
                }
    except Exception: return None

def get_human_comparative_analysis(benchmark_features, user_features):
    if not benchmark_features or not user_features: return "Could not analyze one or both audio files."
    tone_comp = "Your tonal character appears similar to the benchmark."
    if user_features["peak_amplitude"] > benchmark_features["peak_amplitude"] * 1.1:
        tone_comp = "Your sound is brighter and more piercing than the benchmark, with higher peak amplitudes."
    elif user_features["peak_amplitude"] < benchmark_features["peak_amplitude"] * 0.9:
        tone_comp = "Your tone is warmer and less aggressive than the benchmark, with softer peaks."
    dyn_comp = "Your overall dynamic level is very close to the goal recording."
    if user_features["avg_amplitude"] > benchmark_features["avg_amplitude"] * 1.15:
        dyn_comp = "Your performance was generally louder and more powerful than the benchmark."
    elif user_features["avg_amplitude"] < benchmark_features["avg_amplitude"] * 0.85:
        dyn_comp = "Your performance was played at a quieter, more reserved dynamic level than the benchmark."
    style_comp = "You matched the benchmark's dynamic range well."
    if user_features["dynamic_range"] > benchmark_features["dynamic_range"] * 1.15:
        style_comp = "You employed a wider dynamic range, with greater contrast between your quiet and loud passages."
    elif user_features["dynamic_range"] < benchmark_features["dynamic_range"] * 0.85:
        style_comp = "The benchmark recording features a broader dynamic range; aim to make your softs softer and your louds louder."
    full_report = (
        f"Here is a comparison based on the audio analysis:\n\n"
        f"**Dynamics:** {dyn_comp} The benchmark has an average loudness of {benchmark_features['avg_amplitude']:.2f}, while yours is {user_features['avg_amplitude']:.2f}.\n\n"
        f"**Tonal Quality:** {tone_comp} This suggests a difference in bow pressure or contact point.\n\n"
        f"**Playing Style:** {style_comp} This reflects the overall expressiveness of the performance."
    )
    return full_report

def plot_waveform(features, title, color):
    fig, ax = plt.subplots(figsize=(10, 2))
    time_axis = np.linspace(0, features["duration"], num=len(features["waveform"]))
    ax.plot(time_axis, features["waveform"], color=color, linewidth=0.5)
    ax.set_title(title, color='white'); ax.set_xlabel("Time (s)", color='white')
    ax.set_ylabel("Amplitude", color='white'); ax.set_ylim([-1, 1])
    ax.grid(True, alpha=0.2); ax.tick_params(colors='white', which='both')
    fig.patch.set_facecolor('none'); ax.set_facecolor('none')
    return fig

# --- STATE INITIALIZATION ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.search_query = ''; st.session_state.searched_piece_info = None
    st.session_state.audio_frames = []; st.session_state.user_audio_bytes = None
    st.session_state.benchmark_audio_bytes = None; st.session_state.ai_feedback = ""
    st.session_state.analysis_error = ''; st.session_state.volume_level = 0.0

# --- CALLBACKS ---
def handle_benchmark_upload():
    if st.session_state.benchmark_uploader is not None:
        st.session_state.benchmark_audio_bytes = st.session_state.benchmark_uploader.getvalue()
        st.session_state.ai_feedback = ""

def audio_frame_callback(frame):
    audio_data = frame.to_ndarray()
    rms = np.sqrt(np.mean(np.square(audio_data)))
    volume = min(100, int(rms * 500))
    st.session_state["volume_level"] = volume
    st.session_state.audio_frames.append(audio_data.tobytes())
    return frame

# --- MAIN APP LAYOUT & STYLING ---
st.set_page_config(layout="wide", page_title="Violin Studio")
st.markdown("""
    <style>
        .stApp { background-color: #000000; }
        #MainMenu, footer { visibility: hidden; }
        h1 a, h2 a, h3 a { display: none !important; }
        div[role="tablist"] { justify-content: center; }
        button[role="tab"] { font-size: 1.2rem; padding: 10px 20px; border: 2px solid transparent; }
        button[role="tab"][aria-selected="true"] { border-bottom: 2px solid #FFFF00; color: #FFFF00; }
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(1) h2,
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(1) h3 { color: #FFFF00 !important; }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if img_violin1: st.image(img_violin1)
    if img_violin2: st.image(img_violin2)

with col2:
    st.markdown("<h1 style='text-align: center; color: yellow;'>Violin Studio</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["About the Piece", "Compare with Benchmark"])

    with tab1:
        # This tab is unchanged
        st.header("Musical Repertoire Explorer")
        st.write("Enter the name of a piece to learn about its composer, history, and musical context.")
        search_query = st.text_input("Search for a piece:", key="search_query_input", placeholder="e.g., Vivaldi Four Seasons")
        if st.button("Search", key="search_piece"):
            st.session_state.searched_piece_info = fetch_piece_info(search_query)
        if st.session_state.searched_piece_info:
            st.divider()
            info = st.session_state.searched_piece_info
            st.subheader(info['title'])
            st.markdown(f"**Composer:** {info['composer']}")
            st.markdown(f"**About the Piece:** {info['description']}")

    with tab2:
        st.header("Compare with Benchmark")
        st.write("Upload a recording you want to sound like, then record yourself and get a direct comparison.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Recording Goal")
            st.file_uploader("Upload a benchmark recording", type=['wav', 'mp3', 'm4a'], key="benchmark_uploader", on_change=handle_benchmark_upload)
            if st.session_state.benchmark_audio_bytes:
                st.audio(st.session_state.benchmark_audio_bytes)

        with c2:
            st.subheader("My Recording")
            webrtc_ctx = webrtc_streamer(key="audio-recorder", mode=WebRtcMode.SENDONLY, audio_frame_callback=audio_frame_callback, media_stream_constraints={"audio": True, "video": False})
            if webrtc_ctx.state.playing:
                st.progress(st.session_state.get("volume_level", 0), text=f"Loudness: {st.session_state.get('volume_level', 0)}%")
            if not webrtc_ctx.state.playing and len(st.session_state.audio_frames) > 0:
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000)
                    wf.writeframes(b''.join(st.session_state.audio_frames))
                st.session_state.user_audio_bytes = wav_buffer.getvalue()
                st.session_state.audio_frames = []
                st.rerun()
            if st.session_state.user_audio_bytes:
                st.audio(st.session_state.user_audio_bytes, format='audio/wav')

        st.divider()

        # --- COMPARISON ANALYSIS & SPINNER SECTION (NO GIFS) ---
        if st.session_state.benchmark_audio_bytes and st.session_state.user_audio_bytes:
            if st.button("Compare Recordings", type="primary", use_container_width=True):
                st.session_state.ai_feedback = ""
                st.session_state.analysis_error = ""
                
                # Use a spinner for the analysis process
                with st.spinner("AI is analyzing your performance..."):
                    benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
                    user_features = analyze_audio_features(st.session_state.user_audio_bytes)
                    
                    # Simulate a longer processing time
                    time.sleep(5)
                    
                    if benchmark_features and user_features:
                        feedback = get_human_comparative_analysis(benchmark_features, user_features)
                        st.session_state.ai_feedback = feedback
                    else:
                        st.session_state.analysis_error = "Could not process one or both audio files. Please try a different file or re-record."
                
                st.balloons() # Confetti effect after analysis is done
                time.sleep(1) # Give a moment for the balloons to show
                st.rerun() # Rerun to display the results cleanly

        if st.session_state.ai_feedback or st.session_state.analysis_error:
            st.subheader("Comparative Analysis")
            if st.session_state.analysis_error:
                st.error(st.session_state.analysis_error)
            if st.session_state.ai_feedback:
                benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
                user_features = analyze_audio_features(st.session_state.user_audio_bytes)
                if benchmark_features and user_features:
                    chart1, chart2 = st.columns(2)
                    with chart1:
                        st.pyplot(plot_waveform(benchmark_features, "Benchmark Waveform", "#FFFF00"))
                    with chart2:
                        st.pyplot(plot_waveform(user_features, "Your Waveform", "#FFFFFF"))
                st.markdown(st.session_state.ai_feedback)

with col3:
    if img_violin3: st.image(img_violin3)
    if img_violin4: st.image(img_violin4)
