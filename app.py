import streamlit as st
import time
import io
import wave
import numpy as np
import matplotlib.pyplot as plt

# --- THE COMPLETE DATABASE ---
pieceDatabase = {
    # Full List of 50 Pieces
    "elgar_salut_damour": { "composer": "Edward Elgar", "title": "Salut d'amour, Op. 12", "keywords": ["elgar", "love's greeting"], "duration": "03:13", "description": "Composed as an engagement present to his future wife, 'Salut d'amour' (Love's Greeting) is one of Edward Elgar's most beloved short pieces. It is a heartfelt and lyrical romance that captures a sense of gentle affection and warmth. The graceful melody requires a pure, singing tone and sincere expression from the performer. It remains a popular encore piece and a staple of the light classical repertoire, showcasing Elgar's gift for melody.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no2": { "composer": "Frédéric Chopin", "title": "Nocturne in E-flat Major, Op. 9 No. 2", "keywords": ["chopin", "nocturne", "op9", "no2"], "duration": "04:41", "description": "Arguably the most famous of all his nocturnes, this piece is a quintessential example of the Romantic piano style, here beautifully transcribed for violin. The main theme is a deeply lyrical and ornamented melody that flows with grace and elegance. It requires a beautiful, singing tone and a flexible sense of rhythm (rubato) to capture its poetic nature. The piece's structure is relatively simple, allowing the performer to focus on expressive phrasing and delicate nuance.", "usualTempo": 60, "practiceTempo": 50 },
    "debussy_clair_de_lune": { "composer": "Claude Debussy", "title": "Clair de Lune", "keywords": ["debussy", "bergamasque"], "duration": "04:38", "description": "The third and most celebrated movement of the 'Suite bergamasque,' 'Clair de Lune' is one of the most iconic pieces of Impressionist music. Its name, meaning 'moonlight,' perfectly captures the music's delicate, atmospheric, and dreamlike quality. The piece requires exceptional control over dynamics and tone color to create its shimmering textures. The fluid, almost improvisatory-sounding melody floats above rich and innovative harmonies, evoking a serene and magical nighttime scene.", "usualTempo": 50, "practiceTempo": 40 },
    # (And so on for the rest of the 50 pieces... ensure the full database is pasted here)
}

# --- HELPER FUNCTIONS ---
def fetch_piece_info(piece_name):
    if not piece_name: return None
    search_terms = piece_name.lower().split()
    for key, piece in pieceDatabase.items():
        searchable_text = f"{piece['title'].lower()} {piece['composer'].lower()} {' '.join(piece['keywords'])}"
        if all(term in searchable_text for term in search_terms):
            return piece
    return {"title": piece_name, "description": f"Information for '{piece_name}' could not be found.", "composer": "Unknown", "notFound": True}

def analyze_audio_features(audio_bytes):
    if not audio_bytes: return None
    try:
        # A simple check for MP3 files to avoid wave module errors
        if audio_bytes.startswith(b'ID3'):
             st.error("MP3 analysis is not yet supported. Please use WAV files for comparison.")
             return None
        with io.BytesIO(audio_bytes) as wav_f:
            with wave.open(wav_f, 'rb') as wf:
                n_frames, framerate = wf.getnframes(), wf.getframerate()
                if n_frames == 0: return None
                frames = wf.readframes(n_frames)
                audio_array = np.frombuffer(frames, dtype=np.int16)
                normalized_audio = audio_array / 32768.0
                return {"waveform": normalized_audio, "framerate": framerate, "duration": n_frames / float(framerate), "avg_amplitude": np.mean(np.abs(normalized_audio)), "peak_amplitude": np.max(np.abs(normalized_audio)), "dynamic_range": np.max(np.abs(normalized_audio)) - np.min(np.abs(normalized_audio))}
    except Exception as e:
        st.error(f"Could not process audio file. Please ensure it is a valid WAV file. Error: {e}")
        return None

def get_human_comparative_analysis(benchmark_features, user_features):
    if not benchmark_features or not user_features: return "Could not analyze one or both audio files."
    tone_comp, dyn_comp, style_comp = "similar", "very close to", "well"
    if user_features["peak_amplitude"] > benchmark_features["peak_amplitude"] * 1.1: tone_comp = "brighter and more piercing than"
    elif user_features["peak_amplitude"] < benchmark_features["peak_amplitude"] * 0.9: tone_comp = "warmer and less aggressive than"
    if user_features["avg_amplitude"] > benchmark_features["avg_amplitude"] * 1.15: dyn_comp = "generally louder than"
    elif user_features["avg_amplitude"] < benchmark_features["avg_amplitude"] * 0.85: dyn_comp = "quieter and more reserved than"
    if user_features["dynamic_range"] > benchmark_features["dynamic_range"] * 1.15: style_comp = "wider, with more contrast than"
    elif user_features["dynamic_range"] < benchmark_features["dynamic_range"] * 0.85: style_comp = "narrower than"
    return (f"**Dynamics:** Your performance was {dyn_comp} the benchmark. (Avg. Loudness: {user_features['avg_amplitude']:.2f} vs {benchmark_features['avg_amplitude']:.2f})\n\n"
            f"**Tonal Quality:** Your tone was {tone_comp} the goal recording, suggesting a difference in bow pressure.\n\n"
            f"**Playing Style:** You employed a {style_comp} the benchmark's dynamic range, reflecting your expressive choices.")

def plot_waveform(features, title, color):
    fig, ax = plt.subplots(figsize=(10, 2))
    time_axis = np.linspace(0, features["duration"], num=len(features["waveform"]))
    ax.plot(time_axis, features["waveform"], color=color, linewidth=0.5)
    ax.set_title(title, color='white'); ax.set_xlabel("Time (s)", color='white')
    ax.set_ylabel("Amplitude", color='white'); ax.set_ylim([-1, 1])
    ax.grid(True, alpha=0.2); ax.tick_params(colors='white', which='both')
    fig.patch.set_facecolor('none'); ax.set_facecolor('none')
    return fig

# --- STATE INITIALIZATION & CALLBACKS ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.search_query = ''; st.session_state.searched_piece_info = None
    st.session_state.user_audio_bytes = None
    st.session_state.benchmark_audio_bytes = None; st.session_state.ai_feedback = ""
    st.session_state.analysis_error = ''

def handle_benchmark_upload():
    if st.session_state.benchmark_uploader is not None:
        st.session_state.benchmark_audio_bytes = st.session_state.benchmark_uploader.getvalue()
        st.session_state.ai_feedback = ""

def handle_user_upload():
    if st.session_state.user_uploader is not None:
        st.session_state.user_audio_bytes = st.session_state.user_uploader.getvalue()
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
    st.write("Upload a recording you want to sound like, then upload your own recording to get a direct comparison.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Recording Goal")
        st.file_uploader("Upload Benchmark (WAV, MP3)", type=['wav', 'mp3', 'm4a'], key="benchmark_uploader", on_change=handle_benchmark_upload)
        if st.session_state.benchmark_audio_bytes: st.audio(st.session_state.benchmark_audio_bytes)
    with c2:
        st.subheader("My Recording")
        # --- REPLACED RECORDER WITH FILE UPLOADER ---
        st.file_uploader("Upload Your Recording (WAV)", type=['wav'], key="user_uploader", on_change=handle_user_upload, help="Use a tool like Voice Memos on your phone to record, then upload the WAV file here.")
        if st.session_state.user_audio_bytes:
            st.audio(st.session_state.user_audio_bytes, format='audio/wav')

    st.divider()
    if st.session_state.benchmark_audio_bytes and st.session_state.user_audio_bytes:
        if st.button("Compare Recordings", type="primary", use_container_width=True):
            st.session_state.ai_feedback, st.session_state.analysis_error = "", ""
            with st.spinner("AI is analyzing your performance..."):
                benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
                user_features = analyze_audio_features(st.session_state.user_audio_bytes)
                time.sleep(3)
                if benchmark_features and user_features: st.session_state.ai_feedback = get_human_comparative_analysis(benchmark_features, user_features)
                else: st.session_state.analysis_error = "Could not process one or both audio files. Please ensure they are valid WAV files."
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
