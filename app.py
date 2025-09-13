import streamlit as st
import time
import random
import io
import wave
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# --- DATABASE AND SIMULATION LOGIC ---
# (The entire large pieceDatabase from the previous step goes here)
pieceDatabase = {
  # For brevity, I'm only showing a few. The full dictionary should be pasted here.
  "bach_d_minor_partita": { "title": "Partita No. 2 in D minor, BWV 1004", "keywords": ["bach", "chaconne", "ciaccona"], "description": "A cornerstone of the solo violin repertoire by J.S. Bach...", "usualTempo": 76, "practiceTempo": 60 },
  "vivaldi_four_seasons": { "title": "The Four Seasons", "keywords": ["vivaldi", "winter", "spring", "summer", "autumn", "fall"], "description": "A set of four violin concertos by Antonio Vivaldi...", "usualTempo": 100, "practiceTempo": 80 },
  "sarasate_zigeunerweisen": { "title": "Zigeunerweisen, Op. 20", "keywords": ["sarasate", "gypsy airs"], "description": "Pablo de Sarasate's most famous work, a fantasy on Romani themes...", "usualTempo": 138, "practiceTempo": 100 },
  "massenet_meditation": { "title": "Méditation from Thaïs", "keywords": ["massenet", "thais", "meditation"], "description": "A beautiful and serene intermezzo from the opera Thaïs by Jules Massenet...", "usualTempo": 52, "practiceTempo": 44 },
  # PASTE THE REST OF THE 50+ PIECES HERE
}

feedbackPool = {
  "intonation": [
    "Your intonation was generally solid, but watch the G# in the upper register; it tended to be slightly sharp.",
    "A few of the stopped notes on the E string were a little flat. Try practicing with a drone to solidify those pitches.",
  ],
  "rhythm": [
    "The main rhythmic pulse was strong, but the dotted-eighth-sixteenth rhythm could be more precise and sharp.",
    "A tendency to rush during the faster passages was noted. Use a metronome to ensure a steady tempo.",
  ],
  "bowing": [
    "Your bow control is good. For an even smoother legato, try using a lighter bow arm and more consistent speed.",
    "The bow distribution during long notes was excellent, resulting in a very even and sustained tone.",
  ],
  "phrasing": [
    "You have a good sense of the musical phrase. To enhance it further, think about the dynamic shape of each line, building to a peak and then relaxing.",
    "The connection between phrases was seamless, telling a clear musical story.",
  ]
}

# --- NEW AUDIO HANDLING CLASS using Python's 'wave' library ---
class AudioRecorder(AudioProcessorBase):
    def __init__(self) -> None:
        self.frames_buffer = []
        self.sample_rate = 0
        self.sample_width = 0
        self.channels = 0

    def recv(self, frame):
        # Store the first frame's parameters to use when saving the WAV file
        if self.sample_rate == 0:
            self.sample_rate = frame.sample_rate
            self.sample_width = frame.format.bytes
            self.channels = len(frame.layout.channels)
        
        # Append raw audio frame data to the buffer
        self.frames_buffer.append(frame.to_ndarray().tobytes())
        return frame

    def get_wav_bytes(self):
        """Combines all recorded frames into a proper WAV byte string."""
        if not self.frames_buffer:
            return None
        
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sample_width)
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames_buffer))
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()

# --- HELPER FUNCTIONS ---
def fetch_piece_info(piece_name):
    search_terms = piece_name.lower().split()
    for key, piece in pieceDatabase.items():
        searchable_text = f"{piece['title'].lower()} {' '.join(piece['keywords'])}"
        if all(term in searchable_text for term in search_terms):
            return piece
    return {"title": piece_name, "description": "Information for this piece could not be found.", "notFound": True}

def get_advanced_ai_analysis(duration, piece_title, status_placeholder):
    # This simulation function remains the same
    status_placeholder.info(f"Initializing analysis for \"{piece_title}\"... (Estimated time: 10-15 seconds)")
    time.sleep(2)
    is_audio_valid = random.random() > 0.1
    if not is_audio_valid:
        raise ValueError("Analysis failed: The audio is unclear, or a non-violin instrument was detected.")
    status_placeholder.info("Step 1/3: Extracting melody and rhythm from your recording...")
    time.sleep(random.uniform(3, 5))
    status_placeholder.info("Step 2/3: Cross-referencing with professional recordings on the web...")
    time.sleep(random.uniform(3, 5))
    status_placeholder.info("Step 3/3: Comparing your performance and generating feedback...")
    time.sleep(2)
    feedback = []
    num_feedback_points = random.randint(2, 4)
    for _ in range(num_feedback_points):
        timestamp = time.strftime('%M:%S', time.gmtime(random.uniform(0, duration * 0.9)))
        category = random.choice(list(feedbackPool.keys()))
        note = random.choice(feedbackPool[category])
        feedback.append({"timestamp": timestamp, "note": note})
    status_placeholder.empty()
    return sorted(feedback, key=lambda x: x['timestamp'])

# --- STATE INITIALIZATION ---
if 'ui_stage' not in st.session_state:
    st.session_state.ui_stage = 'welcome'
    st.session_state.piece_name = ''
    st.session_state.user_tempo = ''
    st.session_state.piece_info = None
    st.session_state.tempo_feedback = ''
    st.session_state.audio_bytes = None
    st.session_state.saved_audio_bytes = None
    st.session_state.ai_feedback = []
    st.session_state.analysis_error = ''

# --- CALLBACK FUNCTIONS ---
def handle_submit_questions():
    # This function remains the same
    if not st.session_state.piece_name_input:
        st.warning("Please enter the name of the piece.")
        return
    st.session_state.ui_stage = 'describing'
    st.session_state.piece_name = st.session_state.piece_name_input
    st.session_state.user_tempo = st.session_state.user_tempo_input
    info = fetch_piece_info(st.session_state.piece_name)
    st.session_state.piece_info = info
    if st.session_state.user_tempo and not info.get("notFound"):
        user_bpm = int(st.session_state.user_tempo)
        target_bpm = info['usualTempo']
        if abs(user_bpm - target_bpm) / target_bpm <= 0.08:
            st.session_state.tempo_feedback = "This is a great performance tempo!"
        elif user_bpm > target_bpm:
            st.session_state.tempo_feedback = "This is a bit faster than a typical performance tempo."
        else:
            st.session_state.tempo_feedback = "This is a solid practice tempo, good for working out tough spots."

def handle_move_to_recording():
    st.session_state.ui_stage = 'recording'

def handle_analyze():
    if not st.session_state.audio_bytes:
        st.warning("Please record your performance first.")
        return
    st.session_state.ui_stage = 'analyzing'
    st.session_state.ai_feedback = []
    st.session_state.analysis_error = ''

def handle_start_new_analysis():
    if st.session_state.audio_bytes:
        st.session_state.saved_audio_bytes = st.session_state.audio_bytes
    st.session_state.ui_stage = 'questions'
    st.session_state.piece_name = ''
    st.session_state.user_tempo = ''
    st.session_state.piece_info = None
    st.session_state.tempo_feedback = ''
    st.session_state.audio_bytes = None
    st.session_state.ai_feedback = []
    st.session_state.analysis_error = ''

# --- MAIN APP LAYOUT ---
st.set_page_config(layout="wide", page_title="Violin Studio")
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        .stButton>button {
            background-color: #ffffff; color: #000000; border-radius: 50px;
            padding: 10px 25px; font-weight: bold; border: none;
        }
        .stButton>button:hover {
            background-color: #dddddd; transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.image("public/violin1.jpg")
    st.image("public/violin2.jpg")

with col2:
    if st.session_state.ui_stage == 'welcome':
        # Welcome UI is the same
        st.title("Violin Studio")
        st.markdown("### Welcome to the AI-Optimized Acoustic Enhancer Dashboard!")
        st.markdown("This application is designed to help you grow as a musician...")
        if st.button("Start Your Analysis", key="start_welcome"):
            st.session_state.ui_stage = 'questions'
            st.experimental_rerun()

    if st.session_state.ui_stage != 'welcome':
        with st.container():
            # Questions UI is the same
            st.header("Practice Analysis")
            st.text_input("What piece of music are you playing?", key="piece_name_input", placeholder="e.g., Vivaldi Winter")
            st.number_input("What tempo (in BPM) are you taking it?", min_value=30, max_value=250, step=1, key="user_tempo_input")
            st.button("Submit for Description", on_click=handle_submit_questions)

        if st.session_state.ui_stage in ['describing', 'recording', 'analyzing', 'feedback']:
            # Piece Info UI is the same
            if st.session_state.piece_info:
                with st.container():
                    st.subheader(f"About: {st.session_state.piece_info['title']}")
                    if st.session_state.tempo_feedback:
                        st.info(f"**Tempo Note:** {st.session_state.tempo_feedback}")
                    st.write(st.session_state.piece_info['description'])
                    if not st.session_state.piece_info.get("notFound"):
                        c1, c2 = st.columns(2)
                        c1.metric("Suggested Practice", f"{st.session_state.piece_info['practiceTempo']} BPM")
                        c2.metric("Typical Performance", f"{st.session_state.piece_info['usualTempo']} BPM")
                    st.button("Move to Recording", on_click=handle_move_to_recording)

        if st.session_state.ui_stage in ['recording', 'analyzing', 'feedback']:
            with st.container():
                st.subheader("Record Your Performance")
                webrtc_ctx = webrtc_streamer(key="audio-recorder", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioRecorder, media_stream_constraints={"audio": True, "video": False})
                
                # NEW LOGIC: When recording stops, use the processor's method to get WAV bytes
                if not webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
                    audio_bytes = webrtc_ctx.audio_processor.get_wav_bytes()
                    if audio_bytes:
                        st.session_state.audio_bytes = audio_bytes

                if st.session_state.saved_audio_bytes:
                    st.markdown("##### Previous Recording")
                    st.audio(st.session_state.saved_audio_bytes, format='audio/wav')
                if st.session_state.audio_bytes:
                    st.markdown("##### Current Recording")
                    st.audio(st.session_state.audio_bytes, format='audio/wav')
                    st.button("Analyze My Recording", on_click=handle_analyze)

        if st.session_state.ui_stage == 'analyzing':
            status_placeholder = st.empty()
            try:
                # NEW LOGIC: Get duration directly from WAV bytes
                with io.BytesIO(st.session_state.audio_bytes) as wav_f:
                    with wave.open(wav_f, 'rb') as wf:
                        duration = wf.getnframes() / float(wf.getframerate())
                
                feedback = get_advanced_ai_analysis(duration, st.session_state.piece_info['title'], status_placeholder)
                st.session_state.ai_feedback = feedback
                st.session_state.ui_stage = 'feedback'
                st.experimental_rerun()
            except ValueError as e:
                st.session_state.analysis_error = str(e)
                st.session_state.ui_stage = 'feedback'
                st.experimental_rerun()

        if st.session_state.ui_stage == 'feedback':
            # Feedback UI is the same
            with st.container():
                st.subheader("Performance Analysis")
                if st.session_state.analysis_error:
                    st.error(st.session_state.analysis_error)
                if st.session_state.ai_feedback:
                    for item in st.session_state.ai_feedback:
                        st.markdown(f"**Timestamp [{item['timestamp']}]**: {item['note']}")
                st.button("Start New Analysis", on_click=handle_start_new_analysis)

with col3:
    st.image("public/violin3.jpg")
    st.image("public/violin4.jpg")
