import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64 # Needed to "inject" audio into the webpage
import time
import os
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# Set up the model
model = genai.GenerativeModel('gemini-2.5-flash-lite')
# =========================
# 📚 SYLLABUS DATA
# =========================
syllabus = {
    "SCIENCE": [
        "Photosynthesis",
        "Nutrition in Animals",
        "Heat and Temperature",
        "Acids, Bases and Salts",
        "Physical and Chemical Changes"
    ],
    "MATHEMATICS": [
        "Integers",
        "Fractions and Decimals",
        "Data Handling",
        "Simple Equations",
        "Lines and Angles"
    ],
    "ENGLISH": [
        "Reading Skills",
        "Writing Skills",
        "Grammar",
        "Literature",
        "Vocabulary"
    ]
}

# =========================
# 🤖 AI CHARACTER + PROMPT
# =========================
char = r"Ascora/assests/character1.png"
#character_path = os.path.join(parent_dir, "assests", "character1.png")
ROBOT_PROMPT = """
You are Ascora, a friendly robot teacher appearing on a student's screen. 
IMPORTANT: Do NOT write stage directions, visual descriptions, or "(Visuals)". 
ONLY write the actual words you are saying to the student.

Your tone: Exciting, helpful, and simple (Class 7 level).
Structure: 
1. Greet the student.
2. Explain the topic using a real-world story.
3. Ask ONE specific question at the end to check their understanding.
Generate lecture based on this and character this {char} in a way it's interesting even without visuals'
"""

# =========================
# ⚙️ APP CONFIGURATION
# =========================
st.set_page_config(page_title="Ascora", page_icon="🤖", layout="wide")

# =========================
# 🧠 SESSION STATE INITIALIZATION
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

if "notebooks" not in st.session_state:
    st.session_state.notebooks = {
        "Science": "Science Notes...",
        "Math": "Math Notes...",
        "English": "English Notes...",
        "General": ""
    }

if "active_sub" not in st.session_state:
    st.session_state.active_sub = "General"

if "notice_board" not in st.session_state:
    st.session_state.notice_board = "Math Lecture at 2:00 PM | Science Quiz tomorrow!"

if "is_live" not in st.session_state:
    st.session_state.is_live = False

if "current_lecture" not in st.session_state:
    st.session_state.current_lecture = ""

if "active_topic" not in st.session_state:
    st.session_state.active_topic = ""

if "attendance_list" not in st.session_state:
    st.session_state.attendance_list = []

if "live_subject" not in st.session_state:
    st.session_state.live_subject = None

# =========================
# 📌 SIDEBAR NAVIGATION
# =========================
st.sidebar.title("🤖 Ascora Hub")
st.sidebar.image(r"Ascora/assests/logo.png")
#logo_path = os.path.join(parent_dir, "assests", "logo.png")
#if os.path.exists(logo_path):
#    st.sidebar.image(logo_path)
#else:
   # st.sidebar.warning("Logo file not found at the path.")
#st.sidebar.image("assests/logo.png")
if st.session_state.logged_in:
    st.sidebar.success(f"User: {st.session_state.user_role}")
    
    menu_options = ["Home", "Teacher Assistant"] if st.session_state.user_role == "Teacher" else ["Home", "Student Dashboard"]
    role = st.sidebar.radio("Go to:", menu_options)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
else:
    role = "Home"
    st.sidebar.warning("Please Login")

st.sidebar.markdown("---")
st.sidebar.caption("Contact: support@ascora.edu.in")

# =========================
# 🏠 HOME PAGE
# =========================
if role == "Home":
    st.title("🌟 Welcome to Ascora")
    
    if not st.session_state.logged_in:
        col1, _ = st.columns([1, 1])
        
        with col1:
            user_id = st.text_input("User ID", placeholder="T- or S-")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if user_id.upper().startswith("T"):
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Teacher"
                elif user_id.upper().startswith("S"):
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Student"
                st.rerun()
    else:
        st.success(f"Logged in as {st.session_state.user_role}.")

# =========================
# 🎒 STUDENT DASHBOARD
# =========================
elif role == "Student Dashboard":
    st.title("🎒 My Learning Workspace")
    
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("📝 School Diary")
        st.text_area("What did you learn today?", height=100, key="st_diary")

    with row1_col2:
        st.subheader("📌 Notice Board")
        st.warning(st.session_state.notice_board)

    st.write("---")
    st.subheader("📚 My Subjects")

    c1, c2, c3 = st.columns(3)

    if c1.button("🧪 Science +"):
        st.session_state.active_sub = "SCIENCE"

    if c2.button("📐 Math +"):
        st.session_state.active_sub = "MATHEMATICS"

    if c3.button("📖 English +"):
        st.session_state.active_sub = "ENGLISH"

    if st.session_state.active_sub != "General":
        st.divider()
        
        zoom_mode = st.toggle("🔍 Zoom Lecture (Full Screen)", value=False)
        
        if zoom_mode:
            with st.container(border=True):
                st.subheader(f"📺 {st.session_state.active_sub} Stage")
        else:
            lec_col, note_col = st.columns([2, 1])

            # =========================
            # 📺 LECTURE PANEL
            # =========================
            with lec_col:
                with st.container(border=True):
                    t1, t2, t3 = st.tabs(["🔴 Live Stream", "📚 Textbooks", "📜 Transcript"])

                    with t1:
                        if st.session_state.is_live and st.session_state.live_subject == st.session_state.active_sub:
                            st.success("🔴 LIVE CLASS")
                            st.subheader(f"Topic: {st.session_state.active_topic}")

                            col1, col2 = st.columns([1, 2])

                            with col1:
                                st.image(char, use_container_width=True)
                                #if os.path.exists(character_path):
                                    # st.image(character_path, width=300) # You can adjust the width as needed
                                #else:
                                    #st.write("Character image coming soon!")

                            with col2:
                                st.markdown("### 🎙️ Ascora Speaking...")
                                audio_file = open("lecture.mp3", "rb")
                                audio_bytes = audio_file.read()
                                st.audio(audio_bytes, format="audio/mp3")

                            st.divider()
                            st.info("💡 Tip: You can ask doubts in the chat box below!")

                        else:
                            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                            st.caption("Waiting for the Facilitator to start the AI Robot session...")

                    with t2:
                        st.write(f"Digital Textbooks for {st.session_state.active_sub}")

                    with t3:
                        if st.session_state.is_live:
                            st.write("Live Transcript Feed...")
                            st.write(st.session_state.current_lecture)

            # =========================
            # 📓 NOTES PANEL
            # =========================
            with note_col:
                with st.container(border=True):
                    st.subheader("📓 Notes")

                    subject = st.session_state.active_sub

                    if subject not in st.session_state.notebooks:
                        st.session_state.notebooks[subject] = ""

                    st.session_state.notebooks[subject] = st.text_area(
                        "Notes",
                        value=st.session_state.notebooks[subject],
                        height=460,
                        label_visibility="collapsed",
                        key=f"note_{subject}"
                    )

        # =========================
        # 📖 SYLLABUS EXPLORER
        # =========================
        ta, tb = st.tabs(["🔴 Live Stream", "📖 Syllabus Explorer"])

        with ta:
            pass

        with tb:
            st.subheader("📖 Syllabus Explorer")

            if st.session_state.active_sub in syllabus:
                st.write(f"Showing topics for: **{st.session_state.active_sub}**")

                for chapter in syllabus[st.session_state.active_sub]:
                    with st.expander(f"📘 {chapter}"):
                        st.write(f"Topic: {chapter}")

                        if st.button(f"Self-Study {chapter}", key=f"{st.session_state.active_sub}_{chapter}"):
                            study_resp = model.generate_content(
                                f"Explain {chapter} in a simple way for Class 7 students in 3 points."
                            )
                            st.info(study_resp.text)
    else:
        st.warning("⚠️ Please select a subject first.")

    # =========================
    # 💬 CHATBOT SECTION
    # =========================
    st.write("---")
    st.subheader("💬 Ask Ascora")

    user_query = st.chat_input("Ask anything about your topic...")

    if user_query:
        response = model.generate_content(
            f"You are teaching {st.session_state.active_topic}. Answer simply for Class 7:\n{user_query}"
        )
        st.write("🤖", response.text)

# =========================
# 👨‍🏫 TEACHER ASSISTANT
# =========================
elif role == "Teacher Assistant":
    st.title("👨‍🏫 Facilitator Command Center")

    facil_col, sched_col = st.columns([2, 1])

    with facil_col:
        with st.container(border=True):
            st.subheader("🛠️ Class Management")
            t_notice, t_books, t_live = st.tabs(["📌 Notice Board", "📚 Update Books", "💬 Facilitate Class"])

            with t_notice:
                updated_notice = st.text_area("Notice Text", value=st.session_state.notice_board, height=150)

                if st.button("Broadcast to Students", use_container_width=True):
                    st.session_state.notice_board = updated_notice
                    st.success("Notice Board Updated for all students!")

            with t_books:
                st.selectbox("Target Subject", ["Science", "Math", "English"])
                st.file_uploader("Upload Chapter PDF / Reading Material")
                st.text_input("Document Name")
                st.button("Push to Student Dashboard", use_container_width=True)

            with t_live:
                st.info("Answer student doubts or send real-time alerts.")
                st.text_input("Send a global alert (Pop-up):")
                st.button("Push Alert")

    with sched_col:
        with st.container(border=True):
            st.subheader("🗓️ Scheduling")
            st.date_input("Schedule Date")
            st.time_input("Start Time")
            st.selectbox("Lecture Type", ["Theory", "Practical", "Exam Prep", "Quiz"])
            st.button("Confirm & Sync Calendar", use_container_width=True)

            st.divider()
            st.subheader("📝 Live Attendance")

        if st.session_state.attendance_list:
            for idx, name in enumerate(st.session_state.attendance_list):
                st.write(f"{idx+1}. 👤 {name}")

            st.divider()

            if st.button("🗑️ Reset for Next Class"):
                st.session_state.attendance_list = []
                st.rerun()
        else:
            st.info("Waiting for students to join...")

    # =========================
    # 🤖 AI LECTURE CONTROL
    # =========================
    with t_live:
        st.subheader("🤖 Trigger AI Robot Teacher")

        subject = st.selectbox("Select Subject", list(syllabus.keys()))
        topic = st.selectbox("Select Topic", syllabus[subject])

        if st.button("🚀 START AI LECTURE", use_container_width=True):
            full_prompt = f"{ROBOT_PROMPT}\nSubject: {subject}\nTopic: {topic}"
            response = model.generate_content(full_prompt)

            st.session_state.current_lecture = response.text
            st.session_state.active_topic = topic
            st.session_state.is_live = True
            st.session_state.live_subject = subject

            tts = gTTS(text=st.session_state.current_lecture, lang='en')
            tts.save("lecture.mp3")

            st.rerun()
