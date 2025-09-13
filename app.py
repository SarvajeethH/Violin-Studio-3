import streamlit as st
import time
import random
import io
import wave
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

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

# --- AUDIO HANDLING: This part is now handled within the callback ---

# --- HELPER FUNCTIONS ---
def fetch_piece_info(piece_name):
    # This function is unchanged
    search_terms = piece_name.lower().split()
    for key, piece in pieceDatabase.items():
        searchable_text = f"{piece['title'].lower()} {' '.join(piece['keywords'])}"
        if all(term in searchable_text for term in search_terms):
            return piece
    return {"title": piece_name, "description": "Information for this piece could not be found.", "notFound": True}

def get_advanced_ai_analysis(duration, piece_title, status_placeholder):
    # This function is unchanged
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
    st.session_state.piece_name_input = ''
    st.session_state.user_tempo_input = 120 # Default value
    st.session_state.piece_info = None
    st.session_state.tempo_feedback = ''
    st.session_state.audio_frames = []
    st.session_state.audio_bytes = None
    st.session_state.saved_audio_bytes = None
    st.session_state.ai_feedback = []
    st.session_state.analysis_error = ''
    st.session_state.is_recording = False

# --- CALLBACKS & LOGIC ---
def handle_submit_questions():
    if not st.session_state.piece_name_input:
        st.warning("Please enter the name of the piece.")
        return
    with st.spinner("Searching for piece information..."):
        info = fetch_piece_info(st.session_state.piece_name_input)
        st.session_state.piece_info = info
        # Tempo Analysis
        if st.session_state.user_tempo_input and not info.get("notFound"):
            user_bpm = int(st.session_state.user_tempo_input)
            target_bpm = info['usualTempo']
            if abs(user_bpm - target_bpm) / target_bpm <= 0.08:
                st.session_state.tempo_feedback = "This is a great performance tempo!"
            elif user_bpm > target_bpm:
                st.session_state.tempo_feedback = "This is a bit faster than a typical performance tempo."
            else:
                st.session_state.tempo_feedback = "This is a solid practice tempo, good for working out tough spots."
        else:
            st.session_state.tempo_feedback = ''
    st.session_state.ui_stage = 'describing'

def handle_move_to_recording():
    st.session_state.ui_stage = 'recording'
    st.session_state.audio_frames = [] # Clear previous frames

def handle_start_new_analysis():
    # Reset all relevant states, keeping the saved audio
    st.session_state.ui_stage = 'questions'
    st.session_state.piece_name_input = ''
    st.session_state.piece_info = None
    st.session_state.tempo_feedback = ''
    st.session_state.audio_frames = []
    st.session_state.audio_bytes = None
    st.session_state.ai_feedback = []
    st.session_state.analysis_error = ''
    st.session_state.is_recording = False

def handle_clear_recording():
    st.session_state.audio_bytes = None
    st.session_state.audio_frames = []

# This is the new, robust callback for handling audio frames
def audio_frame_callback(frame):
    st.session_state.audio_frames.append(frame.to_ndarray().tobytes())
    return frame

# --- MAIN APP LAYOUT ---
st.set_page_config(layout="wide", page_title="Violin Studio")
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        .stButton>button {
            background-color: #ffffff; color: #000000; border-radius: 50px;
            padding: 10px 25px; font-weight: bold; border: none; transition: all 0.2s;
        }
        .stButton>button:hover { background-color: #dddddd; transform: scale(1.05); }
        .stButton>button:disabled { background-color: #555; color: #999; }
        .st-emotion-cache-1gulkj5 { list-style: none; padding-left: 0; } /* Removes bullet points */
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.image("public/violin1.jpg")
    st.image("public/violin2.jpg")

with col2:
    # --- WELCOME SCREEN ---
    if st.session_state.ui_stage == 'welcome':
        st.title("Violin Studio")
        st.markdown("### Welcome to the AI-Optimized Acoustic Enhancer Dashboard!")
        st.markdown("This application is designed to help you grow as a musician by providing cutting-edge tools to refine your sound...")
        if st.button("Start Your Analysis", key="start_welcome"):
            st.session_state.ui_stage = 'questions'
            st.rerun()

    # --- MAIN INTERACTIVE AREA ---
    if st.session_state.ui_stage != 'welcome':
        st.header("Practice Analysis")
        st.text_input("What piece of music are you playing?", key="piece_name_input", placeholder="e.g., Vivaldi Winter")
        st.number_input("What tempo (in BPM) are you taking it?", min_value=30, max_value=250, step=1, key="user_tempo_input")
        st.button("Submit for Description", on_click=handle_submit_questions)
        st.divider()

        # --- PIECE INFO SECTION ---
        if st.session_state.ui_stage in ['describing', 'recording', 'analyzing', 'feedback'] and st.session_state.piece_info:
            st.subheader(f"About: {st.session_state.piece_info['title']}")
            if st.session_state.tempo_feedback:
                st.info(f"**Tempo Note:** {st.session_state.tempo_feedback}")
            st.write(st.session_state.piece_info['description'])
            if not st.session_state.piece_info.get("notFound"):
                c1, c2 = st.columns(2)
                c1.metric("Suggested Practice", f"{st.session_state.piece_info['practiceTempo']} BPM")
                c2.metric("Typical Performance", f"{st.session_state.piece_info['usualTempo']} BPM")
            st.button("Move to Recording", on_click=handle_move_to_recording)
            st.divider()

        # --- RECORDER SECTION ---
        if st.session_state.ui_stage in ['recording', 'analyzing', 'feedback']:
            st.subheader("Record Your Performance")
            
            # The webrtc component now uses a callback to handle audio frames
            webrtc_ctx = webrtc_streamer(
                key="audio-recorder",
                mode=WebRtcMode.SENDONLY,
                audio_frame_callback=audio_frame_callback,
                media_stream_constraints={"audio": True, "video": False},
                rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            )
            
            # Convert and save audio only when recording stops
            if not webrtc_ctx.state.playing and len(st.session_state.audio_frames) > 0:
                # Save the current recording before clearing the buffer
                if st.session_state.audio_bytes:
                    st.session_state.saved_audio_bytes = st.session_state.audio_bytes

                # Get audio parameters from the component context
                audio_params = webrtc_ctx.audio_receiver.get_stats()["track"]
                sample_rate = audio_params["sampleRate"]
                sample_width = 2 # Assuming 16-bit audio
                channels = audio_params["channels"]
                
                # Combine frames and create WAV bytes
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(sample_width)
                    wf.setframerate(sample_rate)
                    wf.writeframes(b''.join(st.session_state.audio_frames))
                
                st.session_state.audio_bytes = wav_buffer.getvalue()
                st.session_state.audio_frames = [] # Clear buffer after processing
                st.rerun() # Rerun to display the audio player immediately
            
            # Display saved and current recordings
            if st.session_state.saved_audio_bytes:
                st.markdown("##### Previous Recording")
                st.audio(st.session_state.saved_audio_bytes, format='audio/wav')
            
            if st.session_state.audio_bytes:
                st.markdown("##### Current Recording")
                st.audio(st.session_state.audio_bytes, format='audio/wav')
                
                col_analyze, col_clear = st.columns(2)
                col_analyze.button("Analyze My Recording", on_click=handle_analyze, type="primary")
                col_clear.button("Clear Recording", on_click=handle_clear_recording)
            
            st.divider()

        # --- ANALYSIS & FEEDBACK SECTIONS ---
        if st.session_state.ui_stage == 'analyzing':
            status_placeholder = st.empty()
            try:
                with io.BytesIO(st.session_state.audio_bytes) as wav_f:
                    with wave.open(wav_f, 'rb') as wf:
                        duration = wf.getnframes() / float(wf.getframerate())
                feedback = get_advanced_ai_analysis(duration, st.session_state.piece_info['title'], status_placeholder)
                st.session_state.ai_feedback = feedback
                st.session_state.ui_stage = 'feedback'
                st.rerun()
            except ValueError as e:
                st.session_state.analysis_error = str(e)
                st.session_state.ui_stage = 'feedback'
                st.rerun()

        if st.session_state.ui_stage == 'feedback':
            st.subheader("Performance Analysis")
            if st.session_state.analysis_error:
                st.error(st.session_state.analysis_error)
            if st.session_state.ai_feedback:
                for item in st.session_state.ai_feedback:
                    st.markdown(f"- **Timestamp [{item['timestamp']}]**: {item['note']}")
            st.button("Start New Analysis", on_click=handle_start_new_analysis)

with col3:
    st.image("public/violin3.jpg")
    st.image("public/violin4.jpg")
