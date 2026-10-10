
import os
import re
import json
import time
import sqlite3
from datetime import datetime

import fitz
import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="InterviewAI | Preparation Portal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "interview.db"
UPLOAD_DIR = "uploads"
TEST_DURATION = 300

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# 2. DATABASE
# ============================================================

def initialize_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                subject TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)


def save_result(username, subject, score, total):
    percentage = round(score / total * 100, 2) if total else 0

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO results
            (username, subject, score, total, percentage, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            subject,
            score,
            total,
            percentage,
            datetime.now().strftime("%d-%m-%Y %I:%M %p")
        ))


def get_history(username):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT id, subject, score, total, percentage, date
            FROM results
            WHERE username = ?
            ORDER BY id DESC
        """, (username,)).fetchall()


initialize_database()


# ============================================================
# 3. PROFESSIONAL DARK MODE
# ============================================================

st.markdown("""
<style>
    /* Overall application */
    .stApp {
        background: #0B0D12;
        color: #E5E7EB;
    }

    [data-testid="stMain"] {
        background: #0B0D12;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #11131B;
        border-right: 1px solid #282C3B;
    }

    [data-testid="stSidebar"] * {
        color: #E5E7EB;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #F8FAFC !important;
    }

    p, li, label {
        color: #D1D5DB;
    }

    /* Custom headings */
    .hero-title {
        color: #A78BFA;
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        color: #9CA3AF;
        font-size: 15px;
        margin-bottom: 22px;
    }

    .section-title {
        color: #C4B5FD;
        font-size: 22px;
        font-weight: 700;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #171A24;
        padding: 20px;
        border: 1px solid #303449;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        color: #A5B4FC !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        background: #7C3AED;
        color: #FFFFFF !important;
        border: 1px solid #8B5CF6;
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
        transition: 0.2s;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #6D28D9;
        border-color: #A78BFA;
    }

    /* Input fields */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        background: #171A24 !important;
        color: #FFFFFF !important;
        border: 1px solid #3B4057 !important;
        border-radius: 8px;
    }

    /* Select boxes */
    [data-baseweb="select"] > div {
        background: #171A24;
        border-color: #3B4057;
        color: #FFFFFF;
    }

    /* Radio controls */
    [data-testid="stRadio"] label {
        color: #E5E7EB !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #171A24;
        border: 1px dashed #7C3AED;
        border-radius: 12px;
        padding: 12px;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #303449;
        border-radius: 10px;
    }

    /* Progress */
    [data-testid="stProgressBar"] > div > div {
        background: #8B5CF6;
    }

    /* Separators */
    hr {
        border-color: #303449;
    }

    /* Containers */
    [data-testid="stExpander"] {
        background: #141721;
        border: 1px solid #303449;
        border-radius: 10px;
    }

    /* Links */
    a {
        color: #A78BFA !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 4. TECHNICAL QUESTION BANK
# ============================================================

QUESTION_BANK = {
    "Python": [
        {
            "question": "Which keyword is used to define a function in Python?",
            "options": ["function", "def", "fun", "define"],
            "answer": "def",
            "explanation": "The def keyword defines a function."
        },
        {
            "question": "Which data type stores key-value pairs?",
            "options": ["List", "Tuple", "Dictionary", "Set"],
            "answer": "Dictionary",
            "explanation": "A dictionary stores data as key-value pairs."
        },
        {
            "question": "What is the output of len('Python')?",
            "options": ["5", "6", "7", "Error"],
            "answer": "6",
            "explanation": "Python contains six characters."
        },
        {
            "question": "Which symbol begins a single-line comment?",
            "options": ["//", "#", "/*", "$"],
            "answer": "#",
            "explanation": "Python uses # for single-line comments."
        },
        {
            "question": "Which collection stores unique elements?",
            "options": ["List", "Tuple", "Set", "String"],
            "answer": "Set",
            "explanation": "A set stores distinct elements."
        },
        {
            "question": "What is the result of 10 // 3?",
            "options": ["3", "3.33", "1", "4"],
            "answer": "3",
            "explanation": "The // operator performs floor division."
        },
        {
            "question": "Which function converts a valid numeric string to an integer?",
            "options": ["str()", "float()", "int()", "input()"],
            "answer": "int()",
            "explanation": "int() converts a valid numeric string to an integer."
        },
        {
            "question": "Which keyword is used to handle exceptions?",
            "options": ["catch", "try", "check", "error"],
            "answer": "try",
            "explanation": "The try block contains code that may raise an exception."
        }
    ],

    "Java": [
        {
            "question": "Which keyword creates an object in Java?",
            "options": ["class", "new", "this", "static"],
            "answer": "new",
            "explanation": "The new keyword creates an object."
        },
        {
            "question": "What is the usual entry-point method in Java?",
            "options": ["start()", "run()", "main()", "init()"],
            "answer": "main()",
            "explanation": "Java applications normally begin execution in main()."
        },
        {
            "question": "Which type stores true or false?",
            "options": ["int", "char", "boolean", "String"],
            "answer": "boolean",
            "explanation": "The boolean type represents true or false."
        },
        {
            "question": "Which concept allows a class to inherit another class?",
            "options": [
                "Inheritance", "Encapsulation", "Compilation", "Casting"
            ],
            "answer": "Inheritance",
            "explanation": "Inheritance lets a class derive from another class."
        },
        {
            "question": "Which keyword prevents a method from being overridden?",
            "options": ["static", "final", "private", "void"],
            "answer": "final",
            "explanation": "A final method cannot be overridden in a subclass."
        }
    ],

    "DBMS": [
        {
            "question": "What does SQL stand for?",
            "options": [
                "Structured Query Language",
                "Simple Question Language",
                "System Query Logic",
                "Sequential Query Language"
            ],
            "answer": "Structured Query Language",
            "explanation": "SQL is used to query and manage relational databases."
        },
        {
            "question": "Which key uniquely identifies a row in a table?",
            "options": [
                "Foreign key", "Primary key", "Duplicate key", "Common key"
            ],
            "answer": "Primary key",
            "explanation": "A primary key uniquely identifies each row."
        },
        {
            "question": "Which SQL command retrieves records?",
            "options": ["GET", "OPEN", "SELECT", "FETCHALL"],
            "answer": "SELECT",
            "explanation": "SELECT retrieves records from database tables."
        },
        {
            "question": "What is database normalization?",
            "options": [
                "Organizing data to reduce redundancy",
                "Deleting all tables",
                "Encrypting every record",
                "Creating duplicate rows"
            ],
            "answer": "Organizing data to reduce redundancy",
            "explanation": "Normalization organizes relational data to reduce redundancy."
        }
    ],

    "OOP": [
        {
            "question": "Which concept hides internal implementation details?",
            "options": [
                "Inheritance", "Encapsulation", "Iteration", "Compilation"
            ],
            "answer": "Encapsulation",
            "explanation": "Encapsulation bundles data and methods and controls access."
        },
        {
            "question": "Which concept allows different implementations of an interface?",
            "options": [
                "Polymorphism", "Recursion", "Iteration", "Linking"
            ],
            "answer": "Polymorphism",
            "explanation": "Polymorphism allows the same interface to have different behavior."
        },
        {
            "question": "What is a class?",
            "options": [
                "A blueprint for objects",
                "A database",
                "A loop",
                "An operating system"
            ],
            "answer": "A blueprint for objects",
            "explanation": "A class describes the properties and behavior of objects."
        },
        {
            "question": "Which OOP concept represents an IS-A relationship?",
            "options": [
                "Inheritance", "Encapsulation", "Abstraction", "Overloading"
            ],
            "answer": "Inheritance",
            "explanation": "Inheritance represents an IS-A relationship between classes."
        }
    ],

    "Operating Systems": [
        {
            "question": "Which component manages core operating system resources?",
            "options": ["Browser", "Kernel", "Compiler", "Editor"],
            "answer": "Kernel",
            "explanation": "The kernel manages processes, memory and hardware resources."
        },
        {
            "question": "What is a deadlock?",
            "options": [
                "A successful process",
                "Processes waiting indefinitely for resources",
                "A type of memory",
                "A file format"
            ],
            "answer": "Processes waiting indefinitely for resources",
            "explanation": "Deadlock occurs when processes cannot proceed because of resource dependencies."
        },
        {
            "question": "Which is a CPU scheduling algorithm?",
            "options": ["Round Robin", "HTML", "SQL", "HTTP"],
            "answer": "Round Robin",
            "explanation": "Round Robin allocates CPU time in successive time slices."
        },
        {
            "question": "Which memory is generally fastest?",
            "options": ["Hard disk", "RAM", "CPU registers", "DVD"],
            "answer": "CPU registers",
            "explanation": "CPU registers provide extremely fast access to values."
        }
    ],

    "Computer Networks": [
        {
            "question": "What does IP stand for?",
            "options": [
                "Internet Protocol",
                "Internal Program",
                "Internet Process",
                "Input Port"
            ],
            "answer": "Internet Protocol",
            "explanation": "IP handles addressing and routing of packets."
        },
        {
            "question": "Which protocol is commonly used for secure web browsing?",
            "options": ["HTTP", "HTTPS", "FTP", "SMTP"],
            "answer": "HTTPS",
            "explanation": "HTTPS uses TLS to protect web communication."
        },
        {
            "question": "How many layers are in the OSI model?",
            "options": ["4", "5", "7", "8"],
            "answer": "7",
            "explanation": "The OSI reference model has seven layers."
        },
        {
            "question": "Which protocol is commonly used to send email?",
            "options": ["SMTP", "HTTP", "ARP", "DHCP"],
            "answer": "SMTP",
            "explanation": "SMTP is used to send email between clients and servers."
        }
    ]
}


# ============================================================
# 5. OPTIONAL AI QUESTION GENERATOR
# ============================================================

def generate_ai_questions(subject, count):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    prompt = f"""
Create {count} multiple-choice interview questions about {subject}.

Return only a valid JSON array in this exact structure:
[
  {{
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "answer": "Exact correct option text",
    "explanation": "Short explanation"
  }}
]

Requirements:
- Exactly four options per question.
- The answer must exactly match one option.
- Questions must be technically accurate.
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {
                        "role": "system",
                        "content": "Generate accurate technical interview questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3
            },
            timeout=35
        )

        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            return None

        raw_questions = json.loads(match.group())
        valid_questions = []

        for q in raw_questions:
            if not isinstance(q, dict):
                continue

            options = q.get("options")
            answer = q.get("answer")
            question = q.get("question")

            if (
                isinstance(question, str)
                and isinstance(options, list)
                and len(options) == 4
                and all(isinstance(x, str) for x in options)
                and answer in options
            ):
                valid_questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": str(q.get("explanation", ""))
                })

        return valid_questions[:count] or None

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


# ============================================================
# 6. RESUME ANALYZER
# ============================================================

SKILLS = [
    "python", "java", "c++", "sql", "html", "css",
    "javascript", "machine learning", "deep learning",
    "artificial intelligence", "data analysis", "pandas",
    "numpy", "scikit-learn", "tensorflow", "flask",
    "streamlit", "git", "communication", "problem solving",
    "database", "data structures", "algorithms", "power bi",
    "excel", "natural language processing", "computer vision",
    "statistics", "linux", "django", "pytorch"
]


def analyze_resume(pdf_bytes):
    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        extracted_text = "\n".join(
            page.get_text() for page in document
        )
        document.close()

        if not extracted_text.strip():
            return None, []

        text = extracted_text.lower()

        found_skills = [
            skill for skill in SKILLS
            if re.search(
                r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])",
                text
            )
        ]

        return extracted_text, found_skills

    except Exception:
        return None, []


# ============================================================
# 7. SESSION STATE
# ============================================================

DEFAULTS = {
    "username": "",
    "page": "Dashboard",
    "resume_text": "",
    "resume_skills": [],
    "questions": [],
    "subject": "Python",
    "test_started": 0.0,
    "test_active": False,
    "test_submitted": False,
    "result_saved": False,
    "last_result": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 8. LOGIN SCREEN
# ============================================================

if not st.session_state.username:
    st.markdown(
        '<div class="hero-title">🎯 InterviewAI</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-subtitle">'
        'Your personal technical interview preparation platform'
        '</div>',
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        username = st.text_input(
            "Your name",
            placeholder="Enter your name"
        )

        start = st.form_submit_button(
            "Enter Dashboard →",
            use_container_width=True
        )

        if start:
            if username.strip():
                st.session_state.username = username.strip()[:60]
                st.rerun()
            else:
                st.error("Please enter your name.")

    st.stop()


# ============================================================
# 9. SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div style="font-size:27px;font-weight:800;color:#A78BFA">'
        '🎯 InterviewAI</div>',
        unsafe_allow_html=True
    )

    st.caption("PREPARATION PORTAL")
    st.divider()

    st.write(f"Welcome, **{st.session_state.username}**")

    pages = [
        "Dashboard",
        "Resume Analyzer",
        "Practice Interview",
        "Test Results",
        "Interview History"
    ]

    selected_page = st.radio(
        "NAVIGATION",
        pages,
        index=pages.index(st.session_state.page)
        if st.session_state.page in pages else 0
    )

    st.session_state.page = selected_page

    st.divider()
    st.caption("PYTHON • STREAMLIT • SQLITE")

    if st.button("Sign Out", use_container_width=True):
        st.session_state.username = ""
        st.session_state.test_active = False
        st.session_state.test_submitted = False
        st.rerun()


# ============================================================
# 10. DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":
    history = get_history(st.session_state.username)

    st.markdown(
        '<div class="hero-title">Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-subtitle">'
        'Track your preparation and sharpen your technical skills.'
        '</div>',
        unsafe_allow_html=True
    )

    total_tests = len(history)
    average = (
        round(sum(row[4] for row in history) / total_tests, 1)
        if total_tests else 0
    )
    best = max((row[4] for row in history), default=0)

    c1, c2, c3 = st.columns(3)
    c1.metric("📝 Tests Completed", total_tests)
    c2.metric("📊 Average Score", f"{average}%")
    c3.metric("🏆 Best Score", f"{best}%")

    st.divider()
    st.markdown(
        '<div class="section-title">Quick Actions</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📄 Resume Analyzer")
        st.write("Extract resume text and identify relevant skill keywords.")

        if st.button("Analyze Resume", use_container_width=True):
            st.session_state.page = "Resume Analyzer"
            st.rerun()

    with c2:
        st.markdown("### 💻 Technical Practice")
        st.write("Practise technical MCQs under a five-minute time limit.")

        if st.button("Start Practice", use_container_width=True):
            st.session_state.page = "Practice Interview"
            st.rerun()

    st.divider()
    st.markdown(
        '<div class="section-title">Preparation Tips</div>',
        unsafe_allow_html=True
    )

    st.write("✅ Practise coding questions daily.")
    st.write("✅ Revise DBMS, OOP, operating systems and networking.")
    st.write("✅ Explain your answers in your own words.")
    st.write("✅ Review mistakes after each assessment.")

    if history:
        st.subheader("Recent Tests")

        df = pd.DataFrame([
            {
                "Subject": row[1],
                "Score": f"{row[2]}/{row[3]}",
                "Percentage": f"{row[4]}%",
                "Date": row[5]
            }
            for row in history[:5]
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# 11. RESUME ANALYZER
# ============================================================

elif st.session_state.page == "Resume Analyzer":
    st.markdown(
        '<div class="hero-title">Resume Analyzer</div>',
        unsafe_allow_html=True
    )
    st.write("Upload a PDF resume to extract text and find skill keywords.")

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf"]
    )

    if uploaded_file and st.button("Analyze Resume", type="primary"):
        with st.spinner("Reading your resume..."):
            text_content, found_skills = analyze_resume(
                uploaded_file.getvalue()
            )

        if text_content is None:
            st.error(
                "No readable text was found. Please upload a text-based PDF."
            )
        else:
            st.session_state.resume_text = text_content
            st.session_state.resume_skills = found_skills

            safe_name = re.sub(
                r"[^a-zA-Z0-9_-]",
                "_",
                st.session_state.username
            )

            with open(
                os.path.join(UPLOAD_DIR, safe_name + "_resume.pdf"),
                "wb"
            ) as f:
                f.write(uploaded_file.getvalue())

            st.success("Resume text extracted successfully!")

    if st.session_state.resume_text:
        skills = st.session_state.resume_skills

        c1, c2 = st.columns(2)
        c1.metric("Recognized Skills", len(skills))
        c2.metric(
            "Text Length",
            f"{len(st.session_state.resume_text):,} characters"
        )

        st.subheader("Recognized Skills")

        if skills:
            for skill in skills:
                st.markdown(f"- 🟣 {skill.title()}")
        else:
            st.info("No matching skill keywords were detected.")

        st.caption(
            "This tool matches predefined keywords. It does not determine "
            "whether your resume is truthful or suitable for a specific job."
        )

        st.subheader("Extracted Resume Text")
        st.text_area(
            "Text preview",
            value=st.session_state.resume_text,
            height=280
        )

        st.subheader("Suggested Preparation")

        if skills:
            st.write(
                "Prepare examples and interview answers for: "
                + ", ".join(skills)
            )
        else:
            st.write(
                "Consider including your technical skills, projects, "
                "education and relevant experience."
            )


# ============================================================
# 12. PRACTICE INTERVIEW
# ============================================================

elif st.session_state.page == "Practice Interview":
    st.markdown(
        '<div class="hero-title">Technical Interview</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.test_active and not st.session_state.test_submitted:
        st.write("Select a subject and begin your timed assessment.")

        subject = st.selectbox(
            "Select technical subject",
            list(QUESTION_BANK.keys())
        )

        count = st.slider(
            "Number of questions",
            min_value=3,
            max_value=8,
            value=5
        )

        use_ai = st.checkbox(
            "Generate questions using AI API",
            help="Requires a configured GROQ_API_KEY environment variable."
        )

        st.info("⏱️ Five minutes • One mark per correct answer")

        if st.button("Start Test", type="primary", use_container_width=True):
            questions = None

            if use_ai:
                with st.spinner("Generating AI questions..."):
                    questions = generate_ai_questions(subject, count)

                if not questions:
                    st.warning(
                        "AI generation is unavailable. Using built-in questions."
                    )

            if not questions:
                questions = QUESTION_BANK[subject].copy()

            # Clear answers from the previous attempt.
            for i in range(8):
                st.session_state.pop(f"answer_{i}", None)

            st.session_state.questions = questions[:count]
            st.session_state.subject = subject
            st.session_state.test_started = time.time()
            st.session_state.test_active = True
            st.session_state.test_submitted = False
            st.session_state.result_saved = False
            st.session_state.last_result = None
            st.rerun()

    if st.session_state.test_active:
        elapsed = int(time.time() - st.session_state.test_started)
        remaining = max(0, TEST_DURATION - elapsed)

        if remaining == 0:
            st.session_state.test_active = False
            st.session_state.test_submitted = True
            st.rerun()

        # Refresh the page while the test is running.
        st_autorefresh(
            interval=1000,
            limit=TEST_DURATION,
            key="test_countdown"
        )

        mins, secs = divmod(remaining, 60)

        st.subheader(f"Subject: {st.session_state.subject}")
        st.metric("Time Remaining", f"{mins:02d}:{secs:02d}")
        st.progress(remaining / TEST_DURATION)

        with st.form("mcq_form"):
            for i, question in enumerate(st.session_state.questions):
                st.markdown(
                    f"**Question {i + 1}: {question['question']}**"
                )

                st.radio(
                    "Choose an answer",
                    question["options"],
                    index=None,
                    key=f"answer_{i}",
                    label_visibility="collapsed"
                )

                st.divider()

            submitted = st.form_submit_button(
                "Submit Test",
                type="primary",
                use_container_width=True
            )

        if submitted:
            st.session_state.test_active = False
            st.session_state.test_submitted = True
            st.rerun()

    if st.session_state.test_submitted:
        questions = st.session_state.questions

        answers = {
            i: st.session_state.get(f"answer_{i}")
            for i in range(len(questions))
        }

        score = sum(
            1 for i, question in enumerate(questions)
            if answers[i] == question["answer"]
        )

        total = len(questions)
        percentage = round(score / total * 100, 2) if total else 0

        st.divider()
        st.subheader("🏆 Assessment Result")

        c1, c2, c3 = st.columns(3)
        c1.metric("Correct Answers", f"{score}/{total}")
        c2.metric("Percentage", f"{percentage}%")
        c3.metric(
            "Performance",
            "Excellent" if percentage >= 80
            else "Good" if percentage >= 60
            else "Keep Practising"
        )

        st.progress(percentage / 100)

        if percentage >= 80:
            st.success("Excellent work! Keep improving your skills.")
        elif percentage >= 60:
            st.info("Good effort. Review the incorrect answers.")
        else:
            st.warning("Keep practising. You will improve with revision.")

        st.subheader("Answer Review")

        for i, question in enumerate(questions):
            correct = answers[i] == question["answer"]

            if correct:
                st.success(f"Question {i + 1}: Correct")
            else:
                st.error(f"Question {i + 1}: Incorrect")

            st.write(question["question"])
            st.write(f"Your answer: {answers[i] or 'Not answered'}")
            st.write(f"Correct answer: {question['answer']}")
            st.caption(question["explanation"])
            st.divider()

        if not st.session_state.result_saved:
            save_result(
                st.session_state.username,
                st.session_state.subject,
                score,
                total
            )

            st.session_state.last_result = {
                "subject": st.session_state.subject,
                "score": score,
                "total": total,
                "percentage": percentage
            }

            st.session_state.result_saved = True

        if st.button("Start Another Test", type="primary"):
            for i in range(8):
                st.session_state.pop(f"answer_{i}", None)

            st.session_state.test_active = False
            st.session_state.test_submitted = False
            st.session_state.questions = []
            st.session_state.result_saved = False
            st.session_state.last_result = None
            st.rerun()


# ============================================================
# 13. TEST RESULTS
# ============================================================

elif st.session_state.page == "Test Results":
    st.markdown(
        '<div class="hero-title">Performance Analytics</div>',
        unsafe_allow_html=True
    )

    result = st.session_state.last_result

    if result:
        c1, c2, c3 = st.columns(3)
        c1.metric("Subject", result["subject"])
        c2.metric("Score", f"{result['score']}/{result['total']}")
        c3.metric("Percentage", f"{result['percentage']}%")
    else:
        st.info("Complete a test to see your latest result.")

    history = get_history(st.session_state.username)

    if history:
        df = pd.DataFrame([
            {
                "Subject": row[1],
                "Score": row[2],
                "Total": row[3],
                "Percentage": row[4],
                "Date": row[5]
            }
            for row in history
        ])

        st.subheader("Score by Subject")
        chart_df = df.groupby("Subject")["Percentage"].mean()
        st.bar_chart(chart_df)

        st.subheader("All Recorded Results")
        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# 14. INTERVIEW HISTORY
# ============================================================

elif st.session_state.page == "Interview History":
    st.markdown(
        '<div class="hero-title">Interview History</div>',
        unsafe_allow_html=True
    )

    history = get_history(st.session_state.username)

    if history:
        df = pd.DataFrame([
            {
                "Subject": row[1],
                "Score": f"{row[2]}/{row[3]}",
                "Percentage": f"{row[4]}%",
                "Date": row[5]
            }
            for row in history
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)

        if st.button("Clear My History"):
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute(
                    "DELETE FROM results WHERE username = ?",
                    (st.session_state.username,)
                )

            st.session_state.last_result = None
            st.success("Interview history cleared.")
            st.rerun()
    else:
        st.info("No results yet. Start a technical practice test!")
