import sqlite3
import hashlib
import os
import streamlit as st
import time




# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users VALUES (?, ?)",
                  (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username, ))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0] == hash_password(password)
    return False


def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid username or password")


def signup():
    st.title("Sign Up")
    new_username = st.text_input("Choose a username")
    new_password = st.text_input("Choose a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    if st.button("Sign Up"):
        if new_username and new_password and new_password == confirm_password:
            if add_user(new_username, new_password):
                st.success("Account created successfully! Please log in.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Username already exists")
        else:
            st.error("Please fill all fields and ensure passwords match")


def logout():
    st.session_state.authenticated = False
    st.session_state.username = ''
    st.success("Logged out successfully!")
    time.sleep(1)
    st.rerun()
