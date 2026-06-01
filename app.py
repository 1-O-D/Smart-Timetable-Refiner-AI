import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.parser import parse
import requests

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="FROST Scheduler AI",
    page_icon="❄️",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    return pd.read_csv("time.csv")

@st.cache_data
def load_exam():
    return pd.read_csv("exam_config.csv")

df = load_data()
exam_df = load_exam()

# =========================
# BOARD COUNTDOWN
# =========================

exam_date = parse(exam_df.loc[0, "exam_date"])
today = datetime.now()

days_left = (exam_date - today).days

# =========================
# SUBJECT PROGRESS
# =========================

trackable_df = df[df["trackable"] == True]

subjects = ["Physics", "Chemistry", "Maths", "Biology"]

subject_progress = {}

for subject in subjects:

    sub = trackable_df[trackable_df["subject"] == subject]

    if len(sub) > 0:
        progress = sub["completion_percent"].mean()
    else:
        progress = 0

    subject_progress[subject] = round(progress, 2)

# =========================
# BOARD READINESS
# =========================

board_readiness = round(
    sum(subject_progress.values()) / len(subject_progress),
    2
)

# =========================
# WEAK / STRONG SUBJECT
# =========================

weak_subject = min(subject_progress, key=subject_progress.get)
strong_subject = max(subject_progress, key=subject_progress.get)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("⚙️ FROST Controls")

mode = st.sidebar.selectbox(
    "Select Mode",
    [
        "Normal",
        "Smoke",
        "Pit Stop",
        "Ice Drift"
    ]
)

# =========================
# HEADER
# =========================

st.title("❄️ FROST Scheduler AI")

st.caption(
    "Smart Timetable • Progress Analytics • Board Tracking"
)

# =========================
# METRICS
# =========================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "📅 Days Left",
    days_left
)

c2.metric(
    "🎯 Board Readiness",
    f"{board_readiness}%"
)

c3.metric(
    "⚠️ Weak Subject",
    weak_subject
)

c4.metric(
    "🏆 Strong Subject",
    strong_subject
)

st.divider()

# =========================
# SUBJECT PROGRESS
# =========================

st.subheader("📈 Subject Progress")

progress_df = pd.DataFrame({
    "Subject": list(subject_progress.keys()),
    "Progress": list(subject_progress.values())
})

fig = px.bar(
    progress_df,
    x="Subject",
    y="Progress",
    title="Subject Completion Percentage"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# MODE ENGINE
# =========================

st.subheader("🧠 Smart Mode Engine")

if mode == "Normal":

    st.success(
        "Normal Mode Active"
    )

elif mode == "Smoke":

    st.warning(
        """
        Smoke Mode Activated

        • Reduce optional work
        • Focus on PCM + Biology
        • Skip extra tasks
        • Preserve core study blocks
        """
    )

elif mode == "Pit Stop":

    st.info(
        """
        Pit Stop Mode Activated

        • Lower intensity
        • Focus on revision
        • Keep timetable unchanged
        """
    )

elif mode == "Ice Drift":

    st.error(
        """
        Ice Drift Mode Activated

        • Increase accountability
        • Focus on unfinished tasks
        • Add extra revision checks
        """
    )

# =========================
# MISSED TASKS
# =========================

st.divider()

st.subheader("🔄 Missed Task Recovery")

missed = df[df["status"] == "Skipped"]

if len(missed) == 0:

    st.success(
        "No missed tasks found."
    )

else:

    st.dataframe(missed)

    st.warning(
        """
        Recovery Suggestion:

        Move missed tasks into:
        • Sunday Recovery
        • Revision Blocks
        """
    )

# =========================
# WEEKLY ANALYTICS
# =========================

st.divider()

st.subheader("📊 Weekly Analytics")

completed = len(
    df[df["status"] == "Completed"]
)

pending = len(
    df[df["status"] == "Pending"]
)

skipped = len(
    df[df["status"] == "Skipped"]
)

analytics_df = pd.DataFrame({
    "Status": [
        "Completed",
        "Pending",
        "Skipped"
    ],
    "Count": [
        completed,
        pending,
        skipped
    ]
})

pie = px.pie(
    analytics_df,
    names="Status",
    values="Count",
    title="Task Status Overview"
)

st.plotly_chart(
    pie,
    use_container_width=True
)

# =========================
# TIMETABLE VIEW
# =========================

st.divider()

st.subheader("📅 Master Timetable")

day_filter = st.selectbox(
    "Select Schedule",
    [
        "MWF",
        "TTS",
        "SUNDAY"
    ]
)

filtered = df[
    df["day_group"] == day_filter
]

st.dataframe(
    filtered,
    use_container_width=True
)

# =========================
# AI COACH
# =========================

st.divider()

st.subheader("🤖 AI Coach")

user_prompt = st.text_area(
    "Ask AI",
    placeholder="How should I improve Physics before boards?"
)

if st.button("Generate AI Advice"):

    if user_prompt.strip() == "":
        st.warning("Enter a prompt.")

    else:

        try:

            headers = {
               "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}" ,
                "Content-Type": "application/json" 
            }

            payload = {
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""
You are a study planning assistant.

Days Left:
{days_left}

Board Readiness:
{board_readiness}

Weak Subject:
{weak_subject}

Strong Subject:
{strong_subject}
"""
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            result = response.json()

            ai_text = result["choices"][0]["message"]["content"]

            st.success(ai_text)

        except Exception as e:

            st.error(
                f"AI Error: {e}"
            )

# =========================
# RAW DATA
# =========================

with st.expander("🗂 Raw Dataset"):

    st.dataframe(
        df,
        use_container_width=True
    )
