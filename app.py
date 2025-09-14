import streamlit as st
import time
import random
import io
import wave
import numpy as np
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# --- ROBUST IMAGE & ASSET LOADING ---
try:
    img_violin1 = open("public/violin1.jpg", "rb").read()
    img_violin2 = open("public/violin2.jpg", "rb").read()
    img_violin3 = open("public/violin3.jpg", "rb").read()
    img_violin4 = open("public/violin4.jpg", "rb").read()
    running_gif = open("public/running.gif", "rb").read()
    confetti_gif = open("public/confetti.gif", "rb").read()
except FileNotFoundError as e:
    st.error(f"Asset file not found: {e.filename}. Make sure all images and GIFs are in the 'public' folder.")
    st.stop() # Stop the app if essential assets are missing

# --- DATABASE (for "About the Piece" tab) ---
pieceDatabase = {
    "bach_d_minor_partita": { 
        "composer": "J.S. Bach",
        "title": "Partita No. 2 in D minor, BWV 1004", 
        "keywords": ["bach", "chaconne"], 
        "description": "...", "usualTempo": 76, "practiceTempo": 60 
    },
    "vivaldi_four_seasons": { 
        "composer": "Antonio Vivaldi",
        "title": "The Four Seasons", 
        "keywords": ["vivaldi", "winter", "spring", "summer", "autumn"], 
        "description": "...", "usualTempo": 100, "practiceTempo": 80 
    },
    # PASTE THE REST OF YOUR PIECE DATABASE HERE
}

# --- NEW: REAL AUDIO ANALYSIS ENGINE ---
def analyze_audio_features(audio_bytes):
    """Calculates key features from raw audio bytes."""
    if not audio_bytes:
        return None
    try:
        with io.BytesIO(audio_bytes) as wav_f:
            with wave.open(wav_f, 'rb') as wf:
                n_frames = wf.getnframes()
                if n_frames == 0: return None
                frames = wf.readframes(n_frames)
                framerate = wf.getframerate()
                
                # Convert byte data to a numpy array for analysis
                audio_array = np.frombuffer(frames, dtype=np.int16)
                
                # Normalize to -1 to 1 range
                normalized_audio = audio_array / 32768.0
                
                # Calculate features
                avg_amplitude = np.mean(np.abs(normalized_audio))
                peak_amplitude = np.max(np.abs(normalized_audio))
                dynamic_range = peak_amplitude - np.min(np.abs(normalized_audio))
                
                return {
                    "waveform": normalized_audio,
                    "framerate": framerate,
                    "duration": n_frames / float(framerate),
                    "avg_amplitude": avg_amplitude,
                    "peak_amplitude": peak_amplitude,
                    "dynamic_range": dynamic_range,
                }
    except Exception:
        return None # Return None if audio is invalid

# --- NEW: DYNAMIC FEEDBACK GENERATOR ---
def get_human_comparative_analysis(benchmark_features, user_features):
    """Generates a human-like paragraph by comparing real audio features."""
    if not benchmark_features or not user_features:
        return "Could not analyze one or both audio files."

    # Compare features and build feedback components
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

    # Assemble the final report
    full_report = (
        f"Here is a comparison based on the audio analysis:\n\n"
        f"**Dynamics:** {dyn_comp} The benchmark has an average loudness of {benchmark_features['avg_amplitude']:.2f}, while yours is {user_features['avg_amplitude']:.2f}.\n\n"
        f"**Tonal Quality:** {tone_comp} This suggests a difference in bow pressure or contact point.\n\n"
        f"**Playing Style:** {style_comp} This reflects the overall expressiveness of the performance."
    )
    return full_report

# --- NEW: WAVEFORM PLOTTING FUNCTION ---
def plot_waveform(features, title, color):
    """Creates a matplotlib waveform chart."""
    fig, ax = plt.subplots(figsize=(10, 2))
    time_axis = np.linspace(0, features["duration"], num=len(features["waveform"]))
    ax.plot(time_axis, features["waveform"], color=color, linewidth=0.5)
    ax.set_title(title, color='white')
    ax.set_xlabel("Time (s)", color='white')
    ax.set_ylabel("Amplitude", color='white')
    ax.set_ylim([-1, 1])
    ax.grid(True, alpha=0.2)
    ax.tick_params(colors='white', which='both')
    fig.patch.set_facecolor('none') # Transparent background
    ax.set_facecolor('none')
    return fig

# --- STATE INITIALIZATION ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.search_query = ''
    st.session_state.searched_piece_info = None
    st.session_state.audio_frames = []
    st.session_state.user_audio_bytes = None
    st.session_state.benchmark_audio_bytes = None
    st.session_state.ai_feedback = ""
    st.session_state.analysis_error = ''
    st.session_state.volume_level = 0.0
    st.session_state.is_analyzing = False

# --- CALLBACKS & HELPER FUNCTIONS ---
def handle_benchmark_upload():
    if st.session_state.benchmark_uploader is not None:
        st.session_state.benchmark_audio_bytes = st.session_state.benchmark_uploader.getvalue()
        st.session_state.ai_feedback = "" # Clear old feedback

def audio_frame_callback(frame):
    audio_data = frame.to_ndarray()
    rms = np.sqrt(np.mean(np.square(audio_data)))
    volume = min(100, int(rms * 500))
    st.session_state["volume_level"] = volume
    st.session_state.audio_frames.append(audio_data.tobytes())
    return frame

def handle_start_comparison():
    st.session_state.is_analyzing = True
    st.session_state.ai_feedback = ""
    st.session_state.analysis_error = ""

# --- MAIN APP LAYOUT & STYLING ---
st.set_page_config(layout="wide", page_title="Violin Studio")

st.markdown("""
    <style>
        /* Main background */
        .stApp { background-color: #000000; }
        /* Hide default Streamlit elements */
        #MainMenu, footer { visibility: hidden; }
        h1 a, h2 a, h3 a { display: none !important; }

        /* Center and style tabs */
        div[role="tablist"] { justify-content: center; }
        button[role="tab"] {
            font-size: 1.2rem;
            padding: 10px 20px;
            border: 2px solid transparent;
        }
        /* Style for the active tab button */
        button[role="tab"][aria-selected="true"] {
            border-bottom: 2px solid #FFFF00; /* Yellow underline */
            color: #FFFF00;
        }

        /* Custom header colors */
        .yellow-header h2, .yellow-header h3 { color: #FFFF00; }
        .black-header h2, .black-header h3 { color: #000000; }
        
        /* Theming for tabs (backgrounds are harder, so we style headers) */
        /* Tab 1: About the Piece (Yellow on Black) */
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(1) h2,
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(1) h3,
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(1) h1 {
             color: #FFFF00 !important;
        }
        
        /* Tab 2: Compare (This is a bit of a hack, but colors the direct headers) */
        /* Since we can't set a yellow background easily, we just keep the text readable */
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(2) h2,
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(2) h3,
        div[data-testid="stTabs"] .st-emotion-cache-19rxjzo:nth-child(2) h1 {
             color: #FFFFFF !important;
        }
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
        st.header("Musical Repertoire Explorer")
        st.write("Enter the name of a piece to learn about its composer, history, and musical context.")
        search_query = st.text_input("Search for a piece:", key="search_query_input", placeholder="e.g., Vivaldi Four Seasons")
        if st.button("Search", key="search_piece"):
            with st.spinner(f"Searching for '{search_query}'..."):
                st.session_state.searched_piece_info = fetch_piece_info(search_query)
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

        # --- COMPARISON ANALYSIS & ANIMATION SECTION ---
        if st.session_state.benchmark_audio_bytes and st.session_state.user_audio_bytes:
            st.button("Compare Recordings", type="primary", use_container_width=True, on_click=handle_start_comparison)

        if st.session_state.is_analyzing:
            animation_placeholder = st.empty()
            with animation_placeholder.container():
                st.image(running_gif)
                st.info("AI is analyzing your performance...")
            
            # Run the actual analysis
            benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
            user_features = analyze_audio_features(st.session_state.user_audio_bytes)
            time.sleep(4) # Simulate long analysis time
            
            if benchmark_features and user_features:
                feedback = get_human_comparative_analysis(benchmark_features, user_features)
                st.session_state.ai_feedback = feedback
            else:
                st.session_state.analysis_error = "Could not process one or both audio files. Please try a different file or re-record."
            
            # Show confetti and then clear
            with animation_placeholder.container():
                st.image(confetti_gif)
                st.balloons()
            time.sleep(2)
            animation_placeholder.empty()
            st.session_state.is_analyzing = False
            st.rerun()

        if st.session_state.ai_feedback or st.session_state.analysis_error:
            st.subheader("Comparative Analysis")
            if st.session_state.analysis_error:
                st.error(st.session_state.analysis_error)
            if st.session_state.ai_feedback:
                # Display charts first
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
