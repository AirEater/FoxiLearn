import time
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from check import check_transcript, extract_video_id, get_transcript, generate_mindmap
import graphviz
from IPython.display import Image, display
import tempfile
import PyPDF2
from fpdf import FPDF
from pdf import read_pdf, create_pdf, summarize_text
from chatbot import chatbot_response

st.set_page_config(page_title="FoxiLearn|Login", page_icon="🤖", layout="wide")
client = OpenAI(api_key=os.environ['OPEN_API_KEY'])


def home():  #main
    st.markdown("""
    <style>
        body {
            padding: 0px;
            margin: 0px;
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
        }
        .title {
            color: #ff5733;
            text-align: center;
            font-size: 40px; /* Reduced font size */
            font-weight: bold;
            margin-top: 30px; /* Reduced top margin */
        }
        .subtitle {
            color: #5a5a5a;
            text-align: center;
            font-size: 22px; /* Slightly smaller font size */
            margin-bottom: 20px; /* Reduced bottom margin */
        }
        .description {
            margin: 0 auto;
            max-width: 700px; /* Reduced max-width for compact design */
            color: white;
            font-size: 16px; /* Slightly smaller font */
            text-align: center;
            padding: 10px; /* Added some padding for breathing space */
        }
        .features {
            margin: 20px auto; /* Reduced margin */
            max-width: 1100px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }
        .feature-box {
            background-color: #2C3333;
            padding: 20px; /* Reduced padding */
            width: 220px; /* Slightly narrower box */
            text-align: center;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
            border: 8px dotted white; /* Slightly reduced border size */
            margin: 15px; /* Reduced margin */
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .feature-box:hover {
            transform: translateY(-5px);
            box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
        }
        .feature-title {
            font-size: 20px; /* Slightly smaller title font */
            font-weight: bold;
            color: #ff5733;
            margin-bottom: 8px; /* Reduced margin */
        }
        .get-started {
            margin: 30px auto; /* Reduced margin */
            text-align: center;
        }
        .get-started a {
            text-decoration: none;
            color: white;
            background-color: #ff5733;
            padding: 12px 25px; /* Reduced padding */
            border-radius: 20px;
            font-size: 16px; /* Slightly smaller font */
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        }
        .get-started a:hover {
            background-color: #ff451a;
        }

    </style>

    <div class="title">FoxiLearn</div>
    <div class="subtitle"><h2>Your Smart Learning Assistant</h2></div>

    <div class="description">
        FoxiLearn offers powerful tools to streamline your learning experience. Whether you're analyzing YouTube video content, generating mind maps, 
        summarizing PDF notes, or creating quizzes, we've got you covered. Enhance your productivity and make learning more efficient with FoxiLearn.
    </div>

    <div class="features">
        <div class="feature-box">
            <div class="feature-title">YouTube Topic Relevancy Checker</div>
            Analyze the relevance of YouTube videos to your study topics and get smart insights.
        </div>
        <div class="feature-box">
            <div class="feature-title">Mind Map Generator</div>
            Visualize complex ideas by generating mind maps from your study topics.
        </div>
        <div class="feature-box">
            <div class="feature-title">PDF Note Summarization</div>
            Summarize large PDF documents into concise notes to quickly grasp the key concepts.
        </div>
        <div class="feature-box">
            <div class="feature-title">Quiz Generation</div>
            Create quizzes based on your study materials to test your knowledge and reinforce learning.
        </div>
    </div>

    <div class="get-started">
        <a href="#start">Get Started with the SIDEBAR on the left!</a>
    </div>
    """,
                unsafe_allow_html=True)


def check():
    # Ensure the transcript is stored in session state
    if "transcript" not in st.session_state:
        st.session_state.transcript = None  # Initialize if not present

    st.title("FoxiLearn | Your Learning Assistant App")

    # Column initialization
    col1, col2 = st.columns([2, 1])

    # Store inputs in session_state
    if "topic" not in st.session_state:
        st.session_state.topic = ""  # Initialize if not present
    if "videoUrl" not in st.session_state:
        st.session_state.videoUrl = ""  # Initialize if not present

    with col1:
        with st.form(key="FoxiLearn"):
            st.markdown("## 💡Enter your topic below:")
            st.session_state.topic = st.text_input("Topic",
                                                   st.session_state.topic)
            st.markdown("## 📝 Enter the video link below:")
            st.session_state.videoUrl = st.text_input(
                "Video Link", st.session_state.videoUrl)
            submit = st.form_submit_button(label="Check")

    with col2.container(height=400):
        # Create a scrollable container
        with st.chat_message("user"):
            if submit:
                with st.spinner(
                        f"Checking video at {st.session_state.videoUrl}"):
                    time.sleep(3)
                    video_id = extract_video_id(st.session_state.videoUrl)
                    # Store the transcript in session state
                    st.session_state.transcript = get_transcript(video_id)
                    st.write(
                        f"Assistant: {check_transcript(st.session_state.topic, st.session_state.transcript)}"
                    )

    # Mindmap Generation
    if st.button(label="Generate Mindmap"):
        # Use the transcript from session state
        transcript = st.session_state.transcript
        if transcript:  # Check if the transcript is available
            mindmap_code = generate_mindmap(transcript).strip()
            st.write(mindmap_code)
            if mindmap_code:
                st.graphviz_chart(mindmap_code)
            else:
                st.error("Failed to generate a valid mindmap.")
        else:
            st.error("Transcript not available. Please check the video first.")


def pdf():
    st.title("PDF Summarizer")
    st.write("Upload your PDF file to get a summary.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        with st.spinner("Reading PDF..."):
            pdf_text = read_pdf(uploaded_file)

        if pdf_text:
            st.write("PDF successfully read. Generating summary...")
            summary = summarize_text(pdf_text)
            if summary:
                st.write("### Summary:")
                st.write(summary)
                if st.button("Download Summary as PDF"):
                    pdf_file_path = create_pdf(summary)
                    with open(pdf_file_path, "rb") as f:
                        st.download_button("PDF done. Download now",
                                           f,
                                           file_name="summary.pdf",
                                           mime="application/pdf")
            else:
                st.error("Failed to generate a summary.")
        else:
            st.error("No text found in the PDF.")


def chatbot():
    st.title("FoxiLearn Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is your message?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = chatbot_response(prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


def quiz():
    st.title("Quiz")
    st.write("This is the quiz page.")


# Sidebar navigation
st.sidebar.title("Navigation")
# Create buttons with unique keys
home_button = st.sidebar.button("Home", key="home_button")
check_button = st.sidebar.button("Check", key="check_button")
pdf_button = st.sidebar.button("Summarize PDF notes", key="pdf_button")
chatbot_button = st.sidebar.button("Chatbot", key="chatbot_button")
quiz_button = st.sidebar.button("Quiz", key="quiz_button")
# Page routing based on button clicks
if "page" not in st.session_state:
    st.session_state.page = "home"
if home_button:
    st.session_state.page = "home"
elif check_button:
    st.session_state.page = "check"
elif pdf_button:
    st.session_state.page = "pdf"
elif chatbot_button:
    st.session_state.page = "chatbot"
elif quiz_button:
    st.session_state.page = "quiz"
if st.session_state.page == "home":
    home()
elif st.session_state.page == "check":
    check()
elif st.session_state.page == "pdf":
    pdf()
elif st.session_state.page == "chatbot":
    chatbot()
elif st.session_state.page == "quiz":
    quiz()
