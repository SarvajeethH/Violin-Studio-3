import streamlit as st
import time
import random
import io
import wave
import numpy as np
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from pathlib import Path

# --- ROBUST IMAGE LOADING ---
# If you decide to add images back later, this is the correct way to load them.
# For now, this part of the code is not used in the layout.
# try:
#     BASE_DIR = Path(__file__).resolve().parent
#     PUBLIC_DIR = BASE_DIR / "public"
#     img_violin1 = open(PUBLIC_DIR / "violin1.jpg", "rb").read()
#     img_violin2 = open(PUBLIC_DIR / "violin2.jpg", "rb").read()
#     img_violin3 = open(PUBLIC_DIR / "violin3.jpg", "rb").read()
#     img_violin4 = open(PUBLIC_DIR / "violin4.jpg", "rb").read()
# except FileNotFoundError:
#     # This part is commented out so the app runs without images.
#     # st.error("Image files not found.")
#     pass

# --- NEW EXPANDED DATABASE ---
pieceDatabase = {
    # Existing entries for reference
    "bach_d_minor_partita": { "composer": "J.S. Bach", "title": "Partita No. 2 in D minor, BWV 1004", "keywords": ["bach", "chaconne"], "description": "A cornerstone of the solo violin repertoire, this partita is renowned for its final movement, the 'Chaconne.' This single movement is a monumental work, demanding profound emotional depth and technical mastery through a continuous set of variations on a bass line.", "usualTempo": 76, "practiceTempo": 60 },
    "vivaldi_four_seasons": { "composer": "Antonio Vivaldi", "title": "The Four Seasons", "keywords": ["vivaldi", "seasons"], "description": "A set of four violin concertos, each giving musical expression to a season of the year. They are among the most famous works of the Baroque period, known for their programmatic and innovative instrumental writing, which was revolutionary for its time.", "usualTempo": 100, "practiceTempo": 80 },
    
    # NEW PIECES START HERE
    "elgar_salut_damour": { "composer": "Edward Elgar", "title": "Salut d'amour, Op. 12", "keywords": ["elgar", "love's greeting"], "description": "Composed as an engagement present to his future wife, 'Salut d'amour' (Love's Greeting) is one of Edward Elgar's most beloved short pieces. It is a heartfelt and lyrical romance that captures a sense of gentle affection and warmth. The graceful melody requires a pure, singing tone and sincere expression from the performer. It remains a popular encore piece and a staple of the light classical repertoire, showcasing Elgar's gift for melody.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no2": { "composer": "Frédéric Chopin", "title": "Nocturne in E-flat Major, Op. 9 No. 2", "keywords": ["chopin", "nocturne"], "description": "Arguably the most famous of all his nocturnes, this piece is a quintessential example of the Romantic piano style, here beautifully transcribed for violin. The main theme is a deeply lyrical and ornamented melody that flows with grace and elegance. It requires a beautiful, singing tone and a flexible sense of rhythm (rubato) to capture its poetic nature. The piece's structure is relatively simple, allowing the performer to focus on expressive phrasing and delicate nuance.", "usualTempo": 60, "practiceTempo": 50 },
    "debussy_clair_de_lune": { "composer": "Claude Debussy", "title": "Clair de Lune", "keywords": ["debussy"], "description": "The third and most celebrated movement of the 'Suite bergamasque,' 'Clair de Lune' is one of the most iconic pieces of Impressionist music. Its name, meaning 'moonlight,' perfectly captures the music's delicate, atmospheric, and dreamlike quality. The piece requires exceptional control over dynamics and tone color to create its shimmering textures. The fluid, almost improvisatory-sounding melody floats above rich and innovative harmonies, evoking a serene and magical nighttime scene.", "usualTempo": 50, "practiceTempo": 40 },
    "debussy_fille_cheveux_lin": { "composer": "Claude Debussy", "title": "La Fille aux Cheveux de Lin", "keywords": ["debussy", "flaxen hair"], "description": "This piece, whose title means 'The Girl with the Flaxen Hair,' is the eighth prelude from Debussy's first book of Préludes. It is a work of simple, tender beauty, characterized by a gentle and lyrical melody. The music is known for its use of pentatonic scales, which gives it a folk-like, innocent quality. Performing this piece requires a pure, sweet tone and a delicate touch to convey its sense of peaceful intimacy and serene beauty.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no1": { "composer": "Frédéric Chopin", "title": "Nocturne in B-flat Minor, Op. 9 No. 1", "keywords": ["chopin", "nocturne"], "description": "The first nocturne in Chopin's Op. 9 set, this piece is more melancholic and introspective than its famous E-flat major sibling. It features a beautifully longing melody that unfolds over a steady left-hand accompaniment. The piece has a more dramatic and passionate middle section before returning to the calm, reflective mood of the opening. It demands a deep understanding of musical phrasing and the ability to convey a wide range of emotions with a controlled, beautiful tone.", "usualTempo": 84, "practiceTempo": 68 },
    "chopin_nocturne_c_sharp_minor": { "composer": "Frédéric Chopin", "title": "Nocturne in C-sharp Minor, B. 49", "keywords": ["chopin", "posthumous"], "description": "Composed in his youth but published after his death, this Nocturne in C-sharp Minor is one of Chopin's most beloved works. It is filled with a sense of dramatic pathos and profound melancholy, often nicknamed 'Reminiscence.' The piece builds from a quiet, somber opening to a powerful and passionate climax before fading away. Famous violin transcriptions, like the one by Nathan Milstein, capture the work's intense lyrical drama and virtuosic flair.", "usualTempo": 63, "practiceTempo": 52 },
    "debussy_beau_soir": { "composer": "Claude Debussy", "title": "Beau Soir", "keywords": ["debussy", "heifetz"], "description": "'Beau Soir' (Beautiful Evening) is an early song by Claude Debussy, set to a poem by Paul Bourget, famously transcribed for violin by Jascha Heifetz. The music beautifully captures the poem's reflection on the fleeting beauty of life, comparing a sunset to the end of a day. It requires a warm, rich tone and a seamless legato to spin out its long, flowing melodic lines. The piece is a masterpiece of subtle expression, evoking a feeling of serene and gentle nostalgia.", "usualTempo": 58, "practiceTempo": 48 },
    "saint-saens_mon_coeur": { "composer": "Camille Saint-Saëns", "title": "Mon cœur s'ouvre à ta voix", "keywords": ["saint-saens", "samson", "delilah"], "description": "This piece is a famous aria from the opera 'Samson and Delilah,' with a title that translates to 'My heart opens to your voice.' It is sung by Delilah in Act II as she attempts to seduce Samson into revealing the secret of his strength. The music is incredibly lyrical, seductive, and filled with a sense of romantic passion. On the violin, it becomes a powerful showcase for a beautiful, rich tone and expressive, operatic phrasing.", "usualTempo": 54, "practiceTempo": 44 },
    "offenbach_barcarolle": { "composer": "Jacques Offenbach", "title": "Barcarolle from 'The Tales of Hoffmann'", "keywords": ["offenbach", "hoffmann"], "description": "The 'Barcarolle' is the most famous melody from Jacques Offenbach's opera 'The Tales of Hoffmann.' It is a beautiful duet with a gentle, rocking rhythm meant to evoke the feeling of being in a Venetian gondola at night. The music is renowned for its enchanting and slightly melancholic beauty. The lyrical, interwoven melodies make it a perfect piece for a violin transcription, requiring a sweet tone and a graceful, flowing bow arm.", "usualTempo": 80, "practiceTempo": 66 },
    "massenet_meditation": { "composer": "Jules Massenet", "title": "Méditation from 'Thaïs'", "keywords": ["massenet", "thais"], "description": "The 'Méditation' is a symphonic intermezzo from the opera 'Thaïs' and has become one of the most beloved pieces in the violin repertoire. It occurs between the acts as the courtesan Thaïs reflects and decides to change her life, representing her spiritual conversion. The music is intensely beautiful, with a soaring, lyrical melody that requires immense bow control and a pure, singing tone. It is a profound piece that demands both technical poise and deep emotional expression.", "usualTempo": 52, "practiceTempo": 42 },
    "part_spiegel_im_spiegel": { "composer": "Arvo Pärt", "title": "Spiegel im Spiegel", "keywords": ["pärt", "minimalist"], "description": "'Spiegel im Spiegel,' meaning 'Mirror in the Mirror,' is a seminal work of minimalist music by the Estonian composer Arvo Pärt. The piece is characterized by its extreme simplicity, slow tempo, and meditative quality. It consists of a simple, arpeggiated piano part and a slow, lyrical violin melody that unfolds with a sense of timeless calm. Performing this piece requires incredible control, a pure tone, and the ability to sustain a long, unbroken musical line, creating a profoundly peaceful and introspective atmosphere.", "usualTempo": 40, "practiceTempo": 30 },
    "brahms_wiegenlied": { "composer": "Johannes Brahms", "title": "Wiegenlied (Brahms's Lullaby), Op. 49, No. 4", "keywords": ["brahms", "lullaby"], "description": "Commonly known as 'Brahms's Lullaby,' 'Wiegenlied' is one of the most famous melodies ever written. Composed to celebrate the birth of a friend's son, its gentle, rocking rhythm and simple, comforting melody have made it a universal song of peace. While originally a song for voice and piano, it is frequently arranged for various instruments. On the violin or string orchestra, the piece requires a warm, gentle tone and a smooth bowing technique to convey its sense of tender affection.", "usualTempo": 76, "practiceTempo": 63 },
    "schubert_ave_maria": { "composer": "Franz Schubert", "title": "Ave Maria, D. 839", "keywords": ["schubert"], "description": "While often used in religious services, Schubert's 'Ave Maria' was originally a song setting from Sir Walter Scott's poem 'The Lady of the Lake.' It is one of the composer's most famous works, beloved for its beautiful, serene melody and the sense of peace it conveys. The piece unfolds as a prayer, with a flowing accompaniment supporting a lyrical and devotional vocal line. Violin arrangements capture the song's purity and require a beautiful, singing tone and expressive phrasing.", "usualTempo": 50, "practiceTempo": 40 },
    "puccini_o_mio_babbino_caro": { "composer": "Giacomo Puccini", "title": "O Mio Babbino Caro", "keywords": ["puccini", "gianni schicchi"], "description": "From the opera 'Gianni Schicchi,' this is one of the most famous and beloved soprano arias in the entire operatic repertoire. In the story, the character Lauretta sings this plea to her father ('O My Dear Papa') to allow her to be with the man she loves. The music is incredibly lyrical, emotional, and builds to a beautiful, soaring climax. Violin and string orchestra arrangements are very popular, as they perfectly capture the aria's intense passion and melodic beauty.", "usualTempo": 88, "practiceTempo": 70 },
    "grieg_morning_mood": { "composer": "Edvard Grieg", "title": "Peer Gynt Suite No. 1: Morning Mood", "keywords": ["grieg", "peer gynt"], "description": "This iconic piece is the opening movement of the 'Peer Gynt Suite No. 1' and famously depicts a sunrise in the Moroccan desert. The music begins gently with a simple, pastoral melody played by the flute, gradually building in texture and volume as more instruments join. This crescendo perfectly evokes the rising sun and the awakening of nature. It is one of the most recognizable pieces in classical music, celebrated for its beautiful orchestration and evocative atmosphere.", "usualTempo": 72, "practiceTempo": 60 },
    "boccherini_minuetto": { "composer": "Luigi Boccherini", "title": "String Quintet in E Major, G. 275: III. Minuetto", "keywords": ["boccherini", "minuet"], "description": "This famous Minuet is the third movement from one of Luigi Boccherini's string quintets. It has become so popular that it is often performed as a standalone piece and is a staple of the classical repertoire. The music is the epitome of classical elegance and charm, with a graceful, stately character. It requires a light, clean touch and precise articulation to capture its courtly dance feel. The piece is beloved for its memorable melody and refined, galant style.", "usualTempo": 116, "practiceTempo": 92 },
    "piazzolla_libertango": { "composer": "Astor Piazzolla", "title": "Libertango", "keywords": ["piazzolla", "tango"], "description": "A revolutionary work that helped define the genre of 'tango nuevo,' 'Libertango' combines the traditional rhythms of Argentine tango with elements of jazz and classical music. The title itself is a portmanteau of 'libertad' (liberty) and 'tango,' signifying Piazzolla's break from classical tango. The piece is characterized by its driving, syncopated rhythm, fiery energy, and passionate melodies. It is a virtuosic and exhilarating piece for any combination of instruments, demanding rhythmic precision and bold expression.", "usualTempo": 120, "practiceTempo": 100 },
    "mozart_violin_concerto_5": { "composer": "Wolfgang Amadeus Mozart", "title": "Violin Concerto No. 5 in A Major, K. 219", "keywords": ["mozart", "turkish"], "description": "Nicknamed the 'Turkish' concerto, this is the last and most famous of Mozart's five violin concertos. It is a masterpiece of the classical style, known for its elegance, brilliant writing for the solo violin, and formal perfection. The concerto is particularly famous for its final movement, which includes a boisterous and exotic-sounding 'Turkish' section that was fashionable at the time. The entire work demands technical brilliance, a pure, clean tone, and a deep understanding of Mozart's graceful and operatic phrasing.", "usualTempo": 112, "practiceTempo": 90 },
    "brahms_violin_concerto": { "composer": "Johannes Brahms", "title": "Violin Concerto in D Major, Op. 77", "keywords": ["brahms"], "description": "Johannes Brahms's only violin concerto is considered one of the three great German violin concertos of the 19th century. It is a monumental work, symphonic in scope, that demands immense technical skill and profound musical maturity from the soloist. The concerto is known for its rich harmonies, complex structure, and the beautiful integration of the solo violin with the orchestra. It is a cornerstone of the violin repertoire, celebrated for its heroic first movement, a deeply expressive adagio, and a fiery, Hungarian-influenced finale.", "usualTempo": 96, "practiceTempo": 76 },
    "tchaikovsky_violin_concerto": { "composer": "Pyotr Ilyich Tchaikovsky", "title": "Violin Concerto in D Major, Op. 35", "keywords": ["tchaikovsky"], "description": "Initially deemed 'unplayable' by its intended dedicatee, Tchaikovsky's Violin Concerto has become one of the most beloved and frequently performed concertos in the world. It is a work of immense passion, filled with beautiful Russian melodies and dazzling virtuosic passages. The first movement is expansive and dramatic, the second is a lyrical and melancholic 'Canzonetta,' and the finale is a thrilling, folk-dance-inspired Allegro Vivacissimo. It is a true test of a violinist's technical and expressive abilities.", "usualTempo": 120, "practiceTempo": 92 },
    "mendelssohn_violin_concerto": { "composer": "Felix Mendelssohn", "title": "Violin Concerto in E minor, Op. 64", "keywords": ["mendelssohn"], "description": "Mendelssohn's Violin Concerto is a masterpiece of the Romantic era, celebrated for its structural innovations and soaring, lyrical melodies. Unlike earlier concertos, it begins with the solo violin immediately stating the main theme, and its movements are connected without pause. The concerto is known for its passionate first movement, a graceful and song-like Andante, and a light, sparkling finale that requires brilliant virtuosity. It demands both technical brilliance and deep musical sensitivity from the soloist.", "usualTempo": 126, "practiceTempo": 100 },
    # Add other entries as needed, following this format
}

# --- AUDIO ANALYSIS ENGINE --- (Unchanged)
def analyze_audio_features(audio_bytes):
    if not audio_bytes: return None
    try:
        with io.BytesIO(audio_bytes) as wav_f:
            with wave.open(wav_f, 'rb') as wf:
                n_frames, framerate = wf.getnframes(), wf.getframerate()
                if n_frames == 0: return None
                frames = wf.readframes(n_frames)
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

# --- DYNAMIC FEEDBACK GENERATOR --- (Unchanged)
def get_human_comparative_analysis(benchmark_features, user_features):
    if not benchmark_features or not user_features: return "Could not analyze one or both audio files."
    tone_comp = "Your tonal character appears similar to the benchmark."
    if user_features["peak_amplitude"] > benchmark_features["peak_amplitude"] * 1.1: tone_comp = "Your sound is brighter and more piercing than the benchmark."
    elif user_features["peak_amplitude"] < benchmark_features["peak_amplitude"] * 0.9: tone_comp = "Your tone is warmer and less aggressive than the benchmark."
    dyn_comp = "Your overall dynamic level is very close to the goal recording."
    if user_features["avg_amplitude"] > benchmark_features["avg_amplitude"] * 1.15: dyn_comp = "Your performance was generally louder and more powerful than the benchmark."
    elif user_features["avg_amplitude"] < benchmark_features["avg_amplitude"] * 0.85: dyn_comp = "Your performance was played at a quieter dynamic level."
    style_comp = "You matched the benchmark's dynamic range well."
    if user_features["dynamic_range"] > benchmark_features["dynamic_range"] * 1.15: style_comp = "You employed a wider dynamic range, with greater contrast."
    elif user_features["dynamic_range"] < benchmark_features["dynamic_range"] * 0.85: style_comp = "The benchmark recording features a broader dynamic range; aim to make your softs softer and your louds louder."
    return (
        f"Here is a comparison based on the audio analysis:\n\n"
        f"**Dynamics:** {dyn_comp} The benchmark has an average loudness of {benchmark_features['avg_amplitude']:.2f}, while yours is {user_features['avg_amplitude']:.2f}.\n\n"
        f"**Tonal Quality:** {tone_comp} This suggests a difference in bow pressure or contact point.\n\n"
        f"**Playing Style:** {style_comp} This reflects the overall expressiveness of the performance."
    )

# --- WAVEFORM PLOTTING FUNCTION --- (Unchanged)
def plot_waveform(features, title, color):
    fig, ax = plt.subplots(figsize=(10, 2))
    time_axis = np.linspace(0, features["duration"], num=len(features["waveform"]))
    ax.plot(time_axis, features["waveform"], color=color, linewidth=0.5)
    ax.set_title(title, color='white'); ax.set_xlabel("Time (s)", color='white')
    ax.set_ylabel("Amplitude", color='white'); ax.set_ylim([-1, 1])
    ax.grid(True, alpha=0.2); ax.tick_params(colors='white', which='both')
    fig.patch.set_facecolor('none'); ax.set_facecolor('none')
    return fig

# --- STATE INITIALIZATION & CALLBACKS --- (Unchanged)
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.search_query = ''; st.session_state.searched_piece_info = None
    st.session_state.audio_frames = []; st.session_state.user_audio_bytes = None
    st.session_state.benchmark_audio_bytes = None; st.session_state.ai_feedback = ""
    st.session_state.analysis_error = ''; st.session_state.volume_level = 0.0

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
st.set_page_config(layout="centered", page_title="Violin Studio")
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

st.markdown("<h1 style='text-align: center; color: yellow;'>Violin Studio</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["About the Piece", "Compare with Benchmark"])

with tab1:
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
        if st.session_state.benchmark_audio_bytes: st.audio(st.session_state.benchmark_audio_bytes)
    with c2:
        st.subheader("My Recording")
        webrtc_ctx = webrtc_streamer(key="audio-recorder", mode=WebRtcMode.SENDONLY, audio_frame_callback=audio_frame_callback, media_stream_constraints={"audio": True, "video": False})
        if webrtc_ctx.state.playing: st.progress(st.session_state.get("volume_level", 0), text=f"Loudness: {st.session_state.get('volume_level', 0)}%")
        if not webrtc_ctx.state.playing and len(st.session_state.audio_frames) > 0:
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000)
                wf.writeframes(b''.join(st.session_state.audio_frames))
            st.session_state.user_audio_bytes = wav_buffer.getvalue()
            st.session_state.audio_frames = []
            st.rerun()
        if st.session_state.user_audio_bytes: st.audio(st.session_state.user_audio_bytes, format='audio/wav')
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
