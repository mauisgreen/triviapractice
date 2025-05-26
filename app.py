import streamlit as st
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz

st.set_page_config(page_title="Pub Trivia Practice", layout="centered")

st.title("Pub Trivia Practice")

# Load questions
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv")[["question_text", "answer_text", "source"]]
    return df

# Generate the same quiz each day, cached by date + mode
@st.cache_data
def get_daily_quiz(df, mode, date_str):
    import hashlib
    def generate_seed(s):
        return int(hashlib.sha256(s.encode()).hexdigest(), 16) % (2**32)

    seed = generate_seed(date_str + mode)
    filtered_df = df if mode == "All Questions" else df[df["source"].str.lower() == "pub"]
    quiz_qs = filtered_df.sample(n=min(15, len(filtered_df)), random_state=seed).reset_index(drop=True)
    return quiz_qs

# Load question data
df = load_questions()

# Quiz mode selection
mode = st.radio("Choose Quiz Type:", ["All Questions", "Previous Pub Trivia Questions Only"])

# Get today’s date string
today_str = datetime.now().strftime("%Y-%m-%d")

# Display quiz date info
st.info(f"This quiz was last updated on **{today_str}** and will refresh daily.")

# Get today's quiz
quiz_qs = get_daily_quiz(df, mode, today_str)

# Ask questions
user_answers = []
st.subheader("Answer the following questions:")

with st.form("quiz_form"):
    for i, row in quiz_qs.iterrows():
        answer = st.text_input(f"{i+1}. {row['question_text']}", key=f"q_{i}")
        user_answers.append((row["answer_text"], answer))
    submitted = st.form_submit_button("Submit Answers")

# Scoring
# After scoring
if submitted:
    score = 0
    detailed_results = []
    st.subheader("Results:")

    for idx, (correct, user) in enumerate(user_answers):
        correct_clean = str(correct).strip().lower().replace("&", "and")
        user_clean = str(user).strip().lower().replace("&", "and")
        similarity = fuzz.ratio(correct_clean, user_clean)
        is_correct = similarity >= 85
        if is_correct:
            score += 1
        detailed_results.append({
            "Question #": idx + 1,
            "Your Answer": user,
            "Correct Answer": correct,
            "Match (%)": similarity,
            "Result": "✅ Correct" if is_correct else "❌ Incorrect"
        })

    st.success(f"Your Score: {score} / {len(user_answers)}")

    # Save results to session state to preserve across reruns
    st.session_state["detailed_results"] = detailed_results
    st.session_state["show_details"] = False

# After form section
if "detailed_results" in st.session_state:
    if st.button("Show Detailed Answers"):
        st.session_state["show_details"] = True

    if st.session_state.get("show_details", False):
        st.subheader("Detailed Results")
        for res in st.session_state["detailed_results"]:
            st.markdown(
                f"""
                **Q{res['Question #']}**  
                📝 Your Answer: `{res['Your Answer']}`  
                ✅ Correct Answer: `{res['Correct Answer']}`  
                🔍 Match: {res['Match (%)']}% → **{res['Result']}**
                ---
                """
            )
