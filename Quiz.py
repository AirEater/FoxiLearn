import streamlit as st
import os
from openai import OpenAI
import json
from youtube_transcript_api import YouTubeTranscriptApi
import webbrowser
import requests
#only to wrap the colab output
#from IPython.display import HTML, display
import random
import ast

client = OpenAI(api_key=st.secrets['OPEN_API_KEY'])
choice = ''
result = []
pre_result = []


def Quiz():
  Input = st.text_input("Welcome to the Quiz! Press enter a topic:")
  if Input:
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{
            "role":
            "system",
            "content":
            "You are a quiz genetator that generate proper, suitable quiz questions based on input subject given. You only generate ONE question, option and answer at a time. You will breakdown and solve the question on your own knowledge, and provide the answer in a Python Dict format. Do not mention 'Dict' in your response."
        }, {
            "role": "user",
            "content": "primary school math multiplication"
        }, {
            "role":
            "assistant",
            "content":
            """
                      {
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Rome"],
                        "answer": "Paris"
                      }"""
        }, {
            "role": "user",
            "content": f"{Input}"
        }],
        max_tokens=1000,
        temperature=1.2)
  
    #st.write(response.choices[0].message.content)
    result.append(response.choices[0].message.content)
    
    display_question(result)

  # if isinstance(result, list):
  #    st.write("This is a valid Python List.")
  #st.write(result)
  #return json.loads(response.choices[0].message.content)


def display_question(result):
  col1, col2 = st.columns([2, 1])
  with col1:

    st.markdown("##  Pick Your Choice:")
    # Display the question and options using radio buttons
    #  st.write(result)
    #options_list = list(result["options"].values())
    result = json.loads(result[0])
    st.write("Question:")

    with st.form(key='quiz_form'):
      user_answer = st.radio(result["question"], result['options'])
      submit_button = st.form_submit_button("Submit")

      # Check if the user answer is correct
      if submit_button:
     
        if user_answer == result["answer"]:
          st.success("Correct!")
        else:
          st.error(f"Wrong! The correct answer is {result['answer']}.")


# def Layout(response):
#   st.write("Select your best answer:")
#   # Replace single quotes with double quotes
#   st.write(response)
#   if isinstance(response, dict):
#      st.write("This is a valid Python dictionary.")
#   choice = st.radio(f"{response[0]}", [
#       f"{response[1][0]}", f"{response[1][1]}", f"{response[1][2]}",
#       f"{response[1][3]}"])
# submit = st.form_submit_button(label="Check", type="primary")

# store = json.loads(response.choices[0].message.content)
# print("\n", store['question'])

# Col init

if "__name__" == "__main__":
  
    # Display the question and options using radio buttons
    Quiz()
    display_question(result)
  # Submit button within the form

  # topic = st.text_input("Topic")
  # st.markdown("## 📝 Enter the video link below:")
  # videoUrl = st.text_input("Video Link")
  # submit = st.form_submit_button(label="Check", type="primary")

# with col2.container(height=400):
#   # Create a scrollable container
#   with st.chat_message("user"):
#     if submit:
#       with st.spinner(f"Checking video at {videoUrl}"):
#         time.sleep(3)
#       st.write(
#           f"Assistant: {check_transcript(topic, extract_video_id(videoUrl))}")

# css = '''
# <style>
# section.main > div:has(~ footer ) {
#   padding-bottom: 5px;
# }
# </style>
# '''
# st.markdown(css, unsafe_allow_html=True)
