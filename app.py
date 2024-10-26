import streamlit as st
from transformers import pipeline
from PIL import Image
import sqlite3
import pandas as pd

# Load sentiment analysis model
sentiment_model = pipeline("sentiment-analysis")

# Connect to SQLite database
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    height INTEGER,
                    weight INTEGER,
                    feedback TEXT)''')

# Create daily entries table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS daily_entries (
                    username TEXT,
                    date TEXT,
                    height INTEGER,
                    weight INTEGER,
                    feedback TEXT,
                    FOREIGN KEY (username) REFERENCES users (username))''')

conn.commit()

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Function to analyze sentiment
def analyze_sentiment(feedback):
    result = sentiment_model(feedback)
    return result[0]

# Register a new user
def register_user(username, password, height, weight, feedback):
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (username, password, height, weight, feedback))
    conn.commit()

# Authenticate a user
def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return cursor.fetchone()

# Add a daily entry
def add_daily_entry(username, date, height, weight, feedback):
    cursor.execute("INSERT INTO daily_entries VALUES (?, ?, ?, ?, ?)", (username, date, height, weight, feedback))
    conn.commit()

# Get daily entries for a user
def get_daily_entries(username):
    cursor.execute("SELECT * FROM daily_entries WHERE username = ?", (username,))
    return cursor.fetchall()

# Main App Layout
st.title("Glow & Grow E-Journal")
st.write("Welcome to your body positivity journey! Track your daily progress and see your growth.")
st.write("We are focusing on a holistic approach to becoming the best version of yourself, both physically and mentally <3")

# Check login status
if not st.session_state.logged_in:
    # User Authentication
    auth_choice = st.radio("Choose an option:", ["Login", "Register"])

    if auth_choice == "Register":
        with st.form("registration_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            height = st.number_input("Height (cm)", min_value=100, max_value=250)
            weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
            feedback = st.text_area("Share your thoughts and feelings:")
            register_button = st.form_submit_button("Register")

        # Ensure fields are filled
        if register_button:
            if not username or not password or not feedback:
                st.error("Please fill in all fields before registering.")
            else:
                register_user(username, password, height, weight, feedback)
                st.success("Registration successful! Please log in.")

    elif auth_choice == "Login":
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

        if login_button:
            if not username or not password:
                st.error("Please fill in all fields before logging in.")
            else:
                user_data = login_user(username, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()  # Rerun to update the state
                else:
                    st.error("Invalid username or password. Please try again.")

# Home Screen for Logged-In Users
if st.session_state.logged_in:
    st.header("Home Screen")
    st.write(f"Welcome, {st.session_state.username}! Log your daily progress below:")

    # Daily Entry Form
    with st.form("daily_entry_form"):
        today_date = st.date_input("Date")
        daily_height = st.number_input("Height (cm)", min_value=100, max_value=250)
        daily_weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
        daily_feedback = st.text_area("How are you feeling today?")
        submit_daily_entry = st.form_submit_button("Submit Daily Entry")

    if submit_daily_entry:
        add_daily_entry(st.session_state.username, today_date, daily_height, daily_weight, daily_feedback)
        st.success("Daily entry added successfully!")

    # Display Daily Entries and Progress
    st.subheader("Your Progress")
    daily_entries = get_daily_entries(st.session_state.username)
    if daily_entries:
        df = pd.DataFrame(daily_entries, columns=["Username", "Date", "Height", "Weight", "Feedback"])

        # Show Data
        st.write("Here’s a record of your daily entries:")
        st.dataframe(df[["Date", "Height", "Weight", "Feedback"]])

        # Sentiment Analysis on Daily Feedback
        st.subheader("Sentiment Analysis on Feedback")
        df['Sentiment'] = df['Feedback'].apply(lambda x: analyze_sentiment(x)['label'])
        st.write(df[["Date", "Feedback", "Sentiment"]])

        # Plot weight over time
        st.subheader("Weight Over Time")
        st.line_chart(df.set_index("Date")["Weight"])

    else:
        st.info("No daily entries found. Start by submitting an entry above!")
