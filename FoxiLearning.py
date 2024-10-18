#!pip install youtube-transcript-api
#!pip install openai

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

client = OpenAI(api_key="OpenAI_API_KEY")
API_KEY = os.environ["YOUTUBE"] # Replace with your YouTube Data API key
# Set up the title and instructions

# pages = {
#     "Page 1":
#     "Welcome to Page 1! This is the first page of our multi-page application.",
#     "Page 2": "This is Page 2! Here we have some different content.",
#     "Page 3":
#     "You've reached Page 3! More interesting information can be found here.",
#     "Page 4": "This is the last page, Page 4! Thank you for browsing!"
# }

# if 'page_index' not in st.session_state:
#     st.session_state.page_index = 0

# # Function to go to the next page
# def next_page():
#     if st.session_state.page_index < len(pages) - 1:
#         st.session_state.page_index += 1
#         current_page_title = list(pages.keys())[st.session_state.page_index]
#         st.write(current_page_title)

# # Function to go to the previous page
# def previous_page():
#     if st.session_state.page_index > 0:
#         st.session_state.page_index -= 1
#         current_page_title = list(pages.keys())[st.session_state.page_index]
#         st.write(current_page_title)


def Youtube_search(user_input):
    # YouTube API endpoint and parameters
    api_url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': user_input,
        'type': 'video',
        'key': API_KEY,
        'maxResults': 20  # Number of videos to retrieve
    }
    # Make a request to YouTube API
    response = requests.get(api_url, params=params)
    #print(response)
    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()

        # Create an HTML file to display the videos
        with open('youtube_videos.html', 'w') as f:
            f.write(
                '<html><head><style>body{color:black}</style></head><body>\n')
            f.write(f'<h1>Search results for "{user_input}"</h1>\n')

            videos = data['items']
            random.shuffle(videos)
            # Select the top 'num_to_select' videos
            selected_videos = videos[:5]

            # Loop through each video in the response and embed it
            for item in selected_videos:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                description = item['snippet']['description']

                # Embed the video using an iframe
                f.write(f'<h3>{title}</h3>\n')
                f.write(
                    f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>\n'
                )
                f.write(f'<p>{description}</p>\n')
                f.write('<hr>\n')
                f.write('</body></html>\n')


if __name__ == "__main__":
    
    st.title("Video Content Search ")

    # Ask the user to input their search query
    user_input = st.text_input("Enter the topic you are interested in:")

    if st.button("Submit"):
        Youtube_search(user_input)
        # Path to the HTML file
        html_file_path = os.path.abspath('youtube_videos.html')
        # Check if the HTML file exists
        if os.path.exists(html_file_path):
            # Read the HTML file content
            with open(html_file_path, 'r') as f:
                html_content = f.read()

            # Display the HTML content in Streamlit
            st.components.v1.html(html_content, height=600, scrolling=True)

        else:
            st.error("HTML file not found.")


# def TimeLine(inputTranscript):
#     response = client.chat.completions.create(
#         model='gpt-4o',
#         messages=[{
#             'role':
#             'system',
#             'content':
#             """You will help the user to check whether the input is a subset of user input . Please mention at which timeline in the video in the form of hours:minutes:seconds it is related and how it is related in the format of line by line."""
#         }, {
#             'role': 'user',
#             'content': f'{user_input}'
#         }],
#         max_tokens=2048,
#     )


# def Summarization(inputTranscript):
#     response = client.chat.completions.create(
#         model='gpt-4o',
#         messages=[{
#             'role':
#             'system',
#             'content':
#             """You are a good story point retriever. You concludes all the important points that are from different timeline that is mentioned in the input. Please come out with as detailed as possible conclusion to help user understand the content key points."""
#         }, {
#             'role': 'user',
#             'content': f'{user_input}'
#         }],
#         max_tokens=2048,
#     )


# def Display(current_page_title):
#     if current_page_title == "Page 2":
#         # Path to the HTML file
#         if (html_file_path == ''):
#             st.write("No Page Found")
#             return

#         with open(html_file_path, 'r') as f:
#             html_content = f.read()

#             # Display the HTML content in Streamlit
#         st.components.v1.html(html_content, height=600, scrolling=True)

# Define Youtube API Key and search query

# Navigation buttons
# col1, col2 = st.columns(2)

# with col1:
#     if st.button("Back"):
#         previous_page()
#         Display(current_page_title)

# with col2:
#     if st.button("Next"):
#         next_page()
#         Display(current_page_title)

#current_page_content = pages[current_page_title]

