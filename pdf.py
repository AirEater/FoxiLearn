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

client = OpenAI(api_key=os.environ['OPEN_API_KEY'])

def summarize_text(text):
    system_prompt = """
  You are a PDF summarizer. You will summarize the content in the PDF to well-structured note for user to read. Highlight the key points, important concepts, and any relevant details that would help someone quickly understand the material. Make the summary concise, organized, and easy to read, ideally in bullet points or short paragraphs, so that a student can grasp the main ideas without needing to read the entire document.Please organize the key points into clearly defined sections, if possible. Each section should focus on a specific theme or topic for better clarity and understanding. Provide example if suitable.

  Provide explaination for the main idea for better understanding.

  """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role":
                "user",
                "content":
                f"Please summarize the following material:\n\n{text}"
            }],
            temperature=0.5,
            max_tokens=2000)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error occurred while generating the summary: {e}")
        return None


def read_pdf(file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        if not text.strip():
            raise ValueError("No text found in the PDF.")
    except Exception as e:
        st.error(f"Error occurred while reading the PDF: {e}")
    return text


def create_pdf(summary):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)

    pdf_file_path = "summary.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path
