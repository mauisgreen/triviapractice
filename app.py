import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Pub Trivia Practice", layout="centered")

st.title("Pub Trivia Practice")

# Load questions
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv")
    return df

df = load_questions()

# Quiz Mode
mode = st.radio("Choose Quiz Type:", ["All Questions", "Previous Pub Trivia Questions Only"])

# Filter questions
if mode == "Previous Pub Trivia Questions Only":
    filtered_df = df[df["source"].str.lower() == "pub"]
else:
    filtered_df = df

# Get 15 random questions
quiz_qs = filtered_df.sample(n=min(15, len(filtered_df)), random_state=42).reset_index(drop=True)

user_answers = []
st.subheader("Answer the following questions:")

with st.form("quiz_form"):
    for i, row in quiz_qs.iterrows():
        answer = st.text_input(f"{i+1}. {row['question']}", key=f"q_{i}")
        user_answers.append((row["answer"], answer))
    submitted = st.form_submit_button("Submit Answers")

from fuzzywuzzy import fuzz

# Scoring with fuzzy match + answer review toggle
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

    st.success(f"🎉 Your Score: {score} / {len(user_answers)}")

    # Show details only if user clicks
    if st.toggle("Show Detailed Answers & Match Scores"):
        for res in detailed_results:
            st.markdown(
                f"""
                **Q{res['Question #']}**  
                📝 Your Answer: `{res['Your Answer']}`  
                ✅ Correct Answer: `{res['Correct Answer']}`  
                🔍 Match: {res['Match (%)']}% → **{res['Result']}**
                ---
                """
            )

