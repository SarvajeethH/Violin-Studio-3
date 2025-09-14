import streamlit as st
import time
import io
import wave
import numpy as np
import matplotlib.pyplot as plt
from st_audiorec import st_audiorec
from datetime import datetime

# --- DATABASE WITH DURATION FIELD ---
pieceDatabase = {
    # Full List of 50 Pieces
    "elgar_salut_damour": { "composer": "Edward Elgar", "title": "Salut d'amour, Op. 12", "keywords": ["elgar", "love's greeting"], "duration": "03:13", "description": "Composed as an engagement present to his future wife, 'Salut d'amour' (Love's Greeting) is one of Edward Elgar's most beloved short pieces. It is a heartfelt and lyrical romance that captures a sense of gentle affection and warmth. The graceful melody requires a pure, singing tone and sincere expression from the performer. It remains a popular encore piece and a staple of the light classical repertoire, showcasing Elgar's gift for melody.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no2": { "composer": "Frédéric Chopin", "title": "Nocturne in E-flat Major, Op. 9 No. 2", "keywords": ["chopin", "nocturne", "op9", "no2"], "duration": "04:41", "description": "Arguably the most famous of all his nocturnes, this piece is a quintessential example of the Romantic piano style, here beautifully transcribed for violin. The main theme is a deeply lyrical and ornamented melody that flows with grace and elegance. It requires a beautiful, singing tone and a flexible sense of rhythm (rubato) to capture its poetic nature. The piece's structure is relatively simple, allowing the performer to focus on expressive phrasing and delicate nuance.", "usualTempo": 60, "practiceTempo": 50 },
    "debussy_clair_de_lune": { "composer": "Claude Debussy", "title": "Clair de Lune", "keywords": ["debussy", "bergamasque"], "duration": "04:38", "description": "The third and most celebrated movement of the 'Suite bergamasque,' 'Clair de Lune' is one of the most iconic pieces of Impressionist music. Its name, meaning 'moonlight,' perfectly captures the music's delicate, atmospheric, and dreamlike quality. The piece requires exceptional control over dynamics and tone color to create its shimmering textures. The fluid, almost improvisatory-sounding melody floats above rich and innovative harmonies, evoking a serene and magical nighttime scene.", "usualTempo": 50, "practiceTempo": 40 },
    # (And so on for the rest of the 50 pieces... ensure the full database is pasted here)
}

# --- NEW: ADVANCED AUDIO ANALYSIS ENGINE ---
def analyze_audio_features(audio_bytes):
    """Calculates key features from raw audio bytes for comparison."""
    if not audio_bytes: return None
    try:
        with io.BytesIO(audio_bytes) as wav_f:
            with wave.open(wav_f, 'rb') as wf:
                n_frames, framerate = wf.getnframes(), wf.getframerate()
                if n_frames == 0: return None
                frames = wf.readframes(n_frames)
                audio_array = np.frombuffer(frames, dtype=np.int16)
                normalized_audio = audio_array / 32768.0
                
                # New: FFT for tonal balance
                fft_data = np.fft.rfft(normalized_audio)
                fft_freq = np.fft.rfftfreq(len(normalized_audio), d=1./framerate)
                low_freq_energy = np.sum(np.abs(fft_data[fft_freq < 1000]))
                high_freq_energy = np.sum(np.abs(fft_data[fft_freq >= 1000]))
                tonal_balance = high_freq_energy / low_freq_energy if low_freq_energy > 0 else 1.0

                return {
                    "waveform": normalized_audio, "framerate": framerate,
                    "duration": n_frames / float(framerate),
                    "avg_amplitude": np.mean(np.abs(normalized_audio)),
                    "peak_amplitude": np.max(np.abs(normalized_audio)),
                    "tonal_balance": tonal_balance
                }
    except Exception: return None

# --- NEW: DATA-DRIVEN FEEDBACK GENERATOR ---
def get_human_comparative_analysis(benchmark_features, user_features):
    """Generates a human-like paragraph by comparing real audio features."""
    if not benchmark_features or not user_features: return "Could not analyze one or both audio files."
    
    dyn_comp = "very similar to"
    if user_features["avg_amplitude"] > benchmark_features["avg_amplitude"] * 1.15: dyn_comp = "generally louder and more powerful than"
    elif user_features["avg_amplitude"] < benchmark_features["avg_amplitude"] * 0.85: dyn_comp = "quieter and more reserved than"

    tone_comp = "a similar tonal balance to"
    if user_features["tonal_balance"] > benchmark_features["tonal_balance"] * 1.2: tone_comp = "a brighter, more brilliant tone than"
    elif user_features["tonal_balance"] < benchmark_features["tonal_balance"] * 0.8: tone_comp = "a warmer, richer tone than"

    duration_ratio = user_features["duration"] / benchmark_features["duration"]
    tempo_comp = "at a very similar tempo to"
    if duration_ratio < 0.95: tempo_comp = "significantly faster than"
    elif duration_ratio > 1.05: tempo_comp = "significantly slower than"

    return (f"Here is a comparison based on the audio analysis:\n\n"
            f"**Tempo & Rhythm:** You played this piece **{tempo_comp}** the benchmark, taking {user_features['duration']:.1f} seconds compared to the benchmark's {benchmark_features['duration']:.1f} seconds. This affects the overall rhythmic feel.\n\n"
            f"**Dynamics:** Your performance was **{dyn_comp}** the benchmark. This is reflected in the average loudness of your recording ({user_features['avg_amplitude']:.2f}) versus the goal ({benchmark_features['avg_amplitude']:.2f}).\n\n"
            f"**Tonal Quality:** Your recording shows **{tone_comp}** the benchmark. This is often related to bow speed, pressure, and contact point, influencing the balance of high and low frequencies in your sound.")

def plot_waveform(features, title, color):
    # This function is unchanged
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
    st.session_state.user_audio_bytes = None
    st.session_state.benchmark_audio_bytes = None; st.session_state.ai_feedback = ""
    st.session_state.analysis_error = ''
    st.session_state.recording_history = [] # New: for storing up to 5 recordings

# --- CALLBACKS ---
def handle_benchmark_upload():
    if st.session_state.benchmark_uploader is not None:
        st.session_state.benchmark_audio_bytes = st.session_state.benchmark_uploader.getvalue()
        st.session_state.ai_feedback = ""

# --- MAIN APP LAYOUT & STYLING ---
st.set_page_config(layout="centered", page_title="Violin Studio")
st.markdown("""
    <style>
        .stApp { background-color: #000000; }
        #MainMenu, footer { visibility: hidden; }
        h1 a, h2 a, h3 a { display: none !important; }
        div[role="tablist"] { justify-content: center; }
        button[role="tab"] { font-size: 1.2rem; padding: 10px 20px; border: 2px solid transparent; }
        button[role="tab"][aria-selected="true"] { border-bottom: 2px solid #FFFF00; color: #FFFF00; }
    </style>
""", unsafe_allow_html=True)

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
        info = st.session_state.searched_piece_info
        st.divider()
        st.subheader(info['title'])
        st.caption(f"By {info['composer']}")
        st.divider()
        col_duration, col_tempo1, col_tempo2 = st.columns(3)
        if info.get("duration"): col_duration.metric(label="Typical Duration", value=info['duration'])
        if not info.get("notFound"):
            col_tempo1.metric(label="Performance Tempo", value=f"~{info['usualTempo']} BPM")
            col_tempo2.metric(label="Practice Tempo", value=f"~{info['practiceTempo']} BPM")
        with st.expander("📖 Read Full Description and History"):
            st.markdown(info['description'])

with tab2:
    st.header("Compare with Benchmark")
    st.write("Upload a recording you want to sound like, then record yourself and get a direct comparison.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Recording Goal")
        st.file_uploader("Upload a benchmark recording", type=['wav', 'mp3', 'm4a'], key="benchmark_uploader", on_change=handle_benchmark_upload)
        if st.session_state.benchmark_audio_bytes: st.audio(st.session_state.benchmark_audio_bytes)
    with c2:
        st.subheader("My Recording")
        wav_audio_data = st_audiorec() # This is the recorder component

        # NEW ROBUST LOGIC: This runs only when a new recording is finished
        if wav_audio_data is not None and wav_audio_data != st.session_state.user_audio_bytes:
            st.session_state.user_audio_bytes = wav_audio_data
            
            # Add to history
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.recording_history.insert(0, {"timestamp": now, "audio": wav_audio_data})
            
            # Keep only the last 5 recordings
            if len(st.session_state.recording_history) > 5:
                st.session_state.recording_history.pop()
            
            st.rerun() # Rerun to display the new audio player immediately

        if st.session_state.user_audio_bytes:
            st.write("Latest Recording:")
            st.audio(st.session_state.user_audio_bytes, format='audio/wav')

    # --- NEW: RECORDING HISTORY SECTION ---
    if st.session_state.recording_history:
        with st.expander("View Recording History (Last 5)"):
            for i, record in enumerate(st.session_state.recording_history):
                st.write(f"**Recording {i+1}** ({record['timestamp']})")
                st.audio(record['audio'], format='audio/wav')
                st.divider()

    st.divider()
    if st.session_state.benchmark_audio_bytes and st.session_state.user_audio_bytes:
        if st.button("Compare Recordings", type="primary", use_container_width=True):
            st.session_state.ai_feedback, st.session_state.analysis_error = "", ""
            with st.spinner("AI is analyzing your performance..."):
                benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
                user_features = analyze_audio_features(st.session_state.user_audio_bytes)
                time.sleep(3)
                if benchmark_features and user_features: st.session_state.ai_feedback = get_human_comparative_analysis(benchmark_features, user_features)
                else: st.session_state.analysis_error = "Could not process one or both audio files."
            st.balloons()
            time.sleep(1)
            st.rerun()
    
    if st.session_state.ai_feedback or st.session_state.analysis_error:
        st.subheader("Comparative Analysis")
        if st.session_state.analysis_error: st.error(st.session_state.analysis_error)
        if st.session_state.ai_feedback:
            benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
            user_features = analyze_audio_features(st.session_state.user_audio_bytes)
            if benchmark_features and user_features:
                c1, c2 = st.columns(2)
                c1.pyplot(plot_waveform(benchmark_features, "Benchmark Waveform", "#FFFF00"))
                c2.pyplot(plot_waveform(user_features, "Your Waveform", "#FFFFFF"))
            st.markdown(st.session_state.ai_feedback)
