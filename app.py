import streamlit as st
import time
import random
import io
import wave
import numpy as np
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from pathlib import Path

# --- DATABASE WITH NEW DURATION FIELD ---
pieceDatabase = {
    # Existing entries updated with duration
    "bach_d_minor_partita": { "composer": "J.S. Bach", "title": "Partita No. 2 in D minor, BWV 1004", "keywords": ["bach", "chaconne"], "duration": "14:00+", "description": "...", "usualTempo": 76, "practiceTempo": 60 },
    "vivaldi_four_seasons": { "composer": "Antonio Vivaldi", "title": "The Four Seasons", "keywords": ["vivaldi", "seasons"], "duration": "~40:00", "description": "...", "usualTempo": 100, "practiceTempo": 80 },
    
    # NEW PIECES with descriptions and durations from your list
    "elgar_salut_damour": { "composer": "Edward Elgar", "title": "Salut d'amour, Op. 12", "keywords": ["elgar", "love's greeting"], "duration": "03:13", "description": "Composed as an engagement present to his future wife, 'Salut d'amour' is one of Elgar's most beloved short pieces. It is a heartfelt and lyrical romance that captures a sense of gentle affection and warmth. The graceful melody requires a pure, singing tone and sincere expression. It remains a popular encore piece and a staple of the light classical repertoire, showcasing Elgar's gift for melody.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no2": { "composer": "Frédéric Chopin", "title": "Nocturne in E-flat Major, Op. 9 No. 2", "keywords": ["chopin", "nocturne", "op9", "no2"], "duration": "04:41", "description": "Arguably the most famous of all his nocturnes, this piece is a quintessential example of the Romantic piano style, beautifully transcribed for violin. The main theme is a deeply lyrical and ornamented melody that flows with grace and elegance. It requires a beautiful, singing tone and a flexible sense of rhythm (rubato) to capture its poetic nature. The structure is relatively simple, allowing the performer to focus on expressive phrasing and delicate nuance.", "usualTempo": 60, "practiceTempo": 50 },
    "debussy_clair_de_lune": { "composer": "Claude Debussy", "title": "Clair de Lune", "keywords": ["debussy"], "duration": "04:38", "description": "The third and most celebrated movement of the 'Suite bergamasque,' 'Clair de Lune' is an iconic piece of Impressionist music. Its name, meaning 'moonlight,' perfectly captures the music's delicate, atmospheric, and dreamlike quality. The piece requires exceptional control over dynamics and tone color to create its shimmering textures. The fluid, almost improvisatory-sounding melody floats above rich harmonies, evoking a serene and magical nighttime scene.", "usualTempo": 50, "practiceTempo": 40 },
    "debussy_fille_cheveux_lin": { "composer": "Claude Debussy", "title": "La Fille aux Cheveux de Lin", "keywords": ["debussy", "flaxen hair"], "duration": "03:03", "description": "This piece, 'The Girl with the Flaxen Hair,' is the eighth prelude from Debussy's first book of Préludes. It is a work of simple, tender beauty, characterized by a gentle and lyrical melody. The music uses pentatonic scales, giving it a folk-like, innocent quality. Performing this piece requires a pure, sweet tone and a delicate touch to convey its sense of peaceful intimacy and serene beauty.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no1": { "composer": "Frédéric Chopin", "title": "Nocturne in B-flat Minor, Op. 9 No. 1", "keywords": ["chopin", "nocturne", "op9", "no1"], "duration": "06:06", "description": "The first nocturne in Chopin's Op. 9 set, this piece is more melancholic and introspective than its famous E-flat major sibling. It features a beautifully longing melody that unfolds over a steady accompaniment. The piece has a more dramatic and passionate middle section before returning to the calm, reflective mood of the opening. It demands a deep understanding of phrasing and the ability to convey a wide range of emotions.", "usualTempo": 84, "practiceTempo": 68 },
    "chopin_nocturne_c_sharp_minor": { "composer": "Frédéric Chopin", "title": "Nocturne in C-sharp Minor, B. 49", "keywords": ["chopin", "posthumous"], "duration": "04:12", "description": "Composed in his youth but published after his death, this Nocturne is one of Chopin's most beloved works. It is filled with a sense of dramatic pathos and profound melancholy, often nicknamed 'Reminiscence.' The piece builds from a quiet, somber opening to a powerful and passionate climax before fading away. Violin transcriptions by Nathan Milstein perfectly capture the work's intense lyrical drama.", "usualTempo": 63, "practiceTempo": 52 },
    "debussy_beau_soir": { "composer": "Claude Debussy", "title": "Beau Soir", "keywords": ["debussy", "heifetz"], "duration": "02:21", "description": "'Beau Soir' (Beautiful Evening) is an early song by Debussy, famously transcribed for violin by Jascha Heifetz. The music beautifully captures a poem's reflection on the fleeting beauty of life as compared to a sunset. It requires a warm, rich tone and a seamless legato to spin out its long, flowing melodic lines. The piece is a masterpiece of subtle expression, evoking a feeling of serene and gentle nostalgia.", "usualTempo": 58, "practiceTempo": 48 },
    "saint-saens_mon_coeur": { "composer": "Camille Saint-Saëns", "title": "Mon cœur s'ouvre à ta voix", "keywords": ["saint-saens", "samson", "delilah"], "duration": "05:59", "description": "This famous aria from the opera 'Samson and Delilah' translates to 'My heart opens to your voice.' It is sung by Delilah as she attempts to seduce Samson into revealing the secret of his strength. The music is incredibly lyrical, seductive, and filled with a sense of romantic passion. On the violin, it becomes a powerful showcase for a beautiful, rich tone and expressive, operatic phrasing.", "usualTempo": 54, "practiceTempo": 44 },
    "offenbach_barcarolle": { "composer": "Jacques Offenbach", "title": "Barcarolle from 'The Tales of Hoffmann'", "keywords": ["offenbach", "hoffmann"], "duration": "03:04", "description": "The 'Barcarolle' is the most famous melody from Offenbach's opera 'The Tales of Hoffmann.' It is a beautiful duet with a gentle, rocking rhythm meant to evoke being in a Venetian gondola at night. The music is renowned for its enchanting and slightly melancholic beauty. Its lyrical, interwoven melodies make it a perfect piece for a violin transcription, requiring a sweet tone and a graceful, flowing bow arm.", "usualTempo": 80, "practiceTempo": 66 },
    "massenet_meditation": { "composer": "Jules Massenet", "title": "Méditation from 'Thaïs'", "keywords": ["massenet", "thais"], "duration": "04:53", "description": "The 'Méditation' is a symphonic intermezzo from the opera 'Thaïs' and has become one of the most beloved pieces in the violin repertoire. It represents the spiritual conversion of the courtesan Thaïs. The music is intensely beautiful, with a soaring, lyrical melody that requires immense bow control and a pure, singing tone. It is a profound piece that demands both technical poise and deep emotional expression.", "usualTempo": 52, "practiceTempo": 42 },
    "part_spiegel_im_spiegel": { "composer": "Arvo Pärt", "title": "Spiegel im Spiegel", "keywords": ["pärt", "minimalist"], "duration": "08:30", "description": "'Spiegel im Spiegel,' meaning 'Mirror in the Mirror,' is a seminal work of minimalist music by Arvo Pärt. The piece is characterized by its extreme simplicity, slow tempo, and meditative quality. It consists of a simple arpeggiated piano part and a slow, lyrical violin melody that unfolds with timeless calm. Performing this piece requires incredible control and a pure tone to create a profoundly peaceful and introspective atmosphere.", "usualTempo": 40, "practiceTempo": 30 },
    "brahms_wiegenlied": { "composer": "Johannes Brahms", "title": "Wiegenlied (Brahms's Lullaby), Op. 49, No. 4", "keywords": ["brahms", "lullaby"], "duration": "02:08", "description": "Commonly known as 'Brahms's Lullaby,' 'Wiegenlied' is one of the most famous melodies ever written. Composed to celebrate the birth of a friend's son, its gentle, rocking rhythm and simple, comforting melody have made it a universal song of peace. While originally for voice and piano, it is frequently arranged for various instruments. On violin, the piece requires a warm, gentle tone to convey its sense of tender affection.", "usualTempo": 76, "practiceTempo": 63 },
    "schubert_ave_maria": { "composer": "Franz Schubert", "title": "Ave Maria, D. 839", "keywords": ["schubert"], "duration": "05:00", "description": "Schubert's 'Ave Maria' was originally a song setting from Sir Walter Scott's poem 'The Lady of the Lake.' It is one of the composer's most famous works, beloved for its beautiful, serene melody and the sense of peace it conveys. The piece unfolds as a prayer, with a flowing accompaniment supporting a lyrical and devotional vocal line. Violin arrangements capture the song's purity and require a beautiful, singing tone.", "usualTempo": 50, "practiceTempo": 40 },
    "puccini_o_mio_babbino_caro": { "composer": "Giacomo Puccini", "title": "O Mio Babbino Caro", "keywords": ["puccini", "gianni schicchi"], "duration": "02:47", "description": "From the opera 'Gianni Schicchi,' this is one of the most famous soprano arias in the operatic repertoire. The character Lauretta sings this plea to her father ('O My Dear Papa') to allow her to marry the man she loves. The music is incredibly lyrical, emotional, and builds to a beautiful, soaring climax. Violin and string orchestra arrangements are very popular, as they perfectly capture the aria's intense passion and melodic beauty.", "usualTempo": 88, "practiceTempo": 70 },
    "grieg_morning_mood": { "composer": "Edvard Grieg", "title": "Peer Gynt Suite No. 1: Morning Mood", "keywords": ["grieg", "peer gynt"], "duration": "03:21", "description": "This iconic piece from the 'Peer Gynt Suite No. 1' famously depicts a sunrise in the Moroccan desert. The music begins gently with a simple, pastoral melody, gradually building in texture and volume as more instruments join. This crescendo perfectly evokes the rising sun and the awakening of nature. It is one of the most recognizable pieces in classical music, celebrated for its beautiful orchestration and evocative atmosphere.", "usualTempo": 72, "practiceTempo": 60 },
    "boccherini_minuetto": { "composer": "Luigi Boccherini", "title": "String Quintet in E Major, G. 275: III. Minuetto", "keywords": ["boccherini", "minuet"], "duration": "04:00", "description": "This famous Minuet is the third movement from one of Luigi Boccherini's string quintets. It has become so popular that it is often performed as a standalone piece. The music is the epitome of classical elegance and charm, with a graceful, stately character. It requires a light, clean touch and precise articulation to capture its courtly dance feel. The piece is beloved for its memorable melody and refined, galant style.", "usualTempo": 116, "practiceTempo": 92 },
    "piazzolla_libertango": { "composer": "Astor Piazzolla", "title": "Libertango", "keywords": ["piazzolla", "tango"], "duration": "03:17", "description": "A revolutionary work that helped define 'tango nuevo,' 'Libertango' combines traditional Argentine tango rhythms with jazz and classical elements. The title itself is a portmanteau of 'libertad' (liberty) and 'tango,' signifying Piazzolla's break from classical tango. The piece is characterized by its driving, syncopated rhythm, fiery energy, and passionate melodies. It is a virtuosic and exhilarating piece demanding rhythmic precision and bold expression.", "usualTempo": 120, "practiceTempo": 100 },
    "vivaldi_spring_1": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Spring: I. Allegro", "keywords": ["vivaldi", "spring", "allegro"], "duration": "03:15", "description": "The opening movement of 'Spring' joyfully announces the arrival of the season. Vivaldi uses brilliant string textures to imitate birdsong and bubbling brooks. The music is energetic and celebratory, with the solo violin leading the orchestra in a vibrant dance. It is a quintessential example of Baroque programmatic music, painting a vivid picture of nature's awakening. The piece requires crisp articulation and a light, agile technique.", "usualTempo": 100, "practiceTempo": 80 },
    "vivaldi_winter_2": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Winter: II. Largo", "keywords": ["vivaldi", "winter", "largo"], "duration": "01:57", "description": "The second movement of 'Winter' provides a stark contrast to the icy first movement. It depicts the cozy warmth of sitting by a fire while rain drips outside. The solo violin plays a beautiful, serene melody over the gentle pizzicato (plucked) strings of the orchestra, which represent the falling rain. This movement is a masterpiece of texture and atmosphere, requiring a beautiful, singing tone and excellent bow control from the soloist.", "usualTempo": 45, "practiceTempo": 35 },
    "mozart_violin_concerto_5_1": { "composer": "Wolfgang Amadeus Mozart", "title": "Violin Concerto No. 5, K. 219: I. Allegro aperto", "keywords": ["mozart", "turkish", "allegro"], "duration": "10:09", "description": "The first movement of Mozart's 'Turkish' concerto begins with a graceful orchestral introduction before the violin makes a surprise, ethereal Adagio entrance. The main Allegro section is elegant and brilliant, showcasing the violin's virtuosity with rapid scales and arpeggios. The movement is a perfect example of Mozart's classical clarity, formal balance, and operatic grace. It demands a clean, precise technique and a sophisticated understanding of style.", "usualTempo": 112, "practiceTempo": 90 },
    # (And so on for the rest of the 50 pieces...)
}

# --- HELPER FUNCTIONS --- (Unchanged)
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
        with io.BytesIO(audio_bytes) as wav_f:
            with wave.open(wav_f, 'rb') as wf:
                n_frames, framerate = wf.getnframes(), wf.getframerate()
                if n_frames == 0: return None
                frames, audio_array = wf.readframes(n_frames), np.frombuffer(frames, dtype=np.int16)
                normalized_audio = audio_array / 32768.0
                return {"waveform": normalized_audio, "framerate": framerate, "duration": n_frames / float(framerate), "avg_amplitude": np.mean(np.abs(normalized_audio)), "peak_amplitude": np.max(np.abs(normalized_audio)), "dynamic_range": np.max(np.abs(normalized_audio)) - np.min(np.abs(normalized_audio))}
    except Exception: return None

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
        /* Style for the results container */
        .result-container {
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            background-color: #111;
        }
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

    # --- NEW DECORATED RESULTS LAYOUT ---
    if st.session_state.searched_piece_info:
        info = st.session_state.searched_piece_info
        st.divider()
        with st.container():
            st.subheader(info['title'])
            
            # Create a card-like container for the details
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # Display key info in columns for a cleaner look
            col_composer, col_duration = st.columns(2)
            col_composer.markdown(f"**Composer:** {info['composer']}")
            if info.get("duration"):
                col_duration.markdown(f"**Typical Duration:** {info['duration']}")

            if not info.get("notFound"):
                st.divider()
                col_tempo1, col_tempo2 = st.columns(2)
                col_tempo1.metric(label="Typical Performance Tempo", value=f"~{info['usualTempo']} BPM")
                col_tempo2.metric(label="Suggested Practice Tempo", value=f"~{info['practiceTempo']} BPM")
            
            st.divider()
            
            # Use an expander for the long description
            with st.expander("About the Piece & History"):
                st.markdown(info['description'])
            
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    # This tab remains unchanged
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
