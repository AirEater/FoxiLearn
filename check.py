import time
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from graphviz import Digraph
from IPython.display import Image, display

client = OpenAI(api_key=os.environ['OPEN_API_KEY'])


# Function init()
## To extract video ID from the video link
def extract_video_id(url):
    # Find the index of 'v=' in the URL and get the substring after it
    if "v=" in url:
        start = url.index(
            "v=") + 2  # Start of the video ID (2 characters after 'v=')
        return url[start:start + 11]  # Video IDs are 11 characters long
    else:
        return None


def get_transcript(inputVideoID):
    inputTranscript = YouTubeTranscriptApi.get_transcript(inputVideoID)
    return inputTranscript


def check_transcript(topic, inputTranscript):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                'role':
                'system',
                'content':
                f"""You will help the user to check whether the input is relevent to the subset topic of {topic}. 
          Please output in the format of:
          In the provided text, the section related to supervised learning can be found at the following timestamps:

- 0:00:00 - 0:01:10: Introduction to the tutorial discussing supervised learning as one of the machine learning topics covered.
- 0:01:11 - 0:02:00: Definition and explanation of supervised learning, including the use of labeled data.
- 0:02:01 - 0:03:20: Examples of supervised learning tasks such as image classification and model training using labeled data.
- 0:03:21 - 0:04:00: Discussion on various algorithms under supervised learning like linear regression, logistic regression, etc.
- 0:04:01 - 0:04:50: Application scenarios of supervised learning in solving classification and regression problems like weather prediction or cancer diagnosis.

Please refer to these timestamps for content related to supervised learning in the provided text.``` The time should be in the format of ```hours:minutes:seconds```. Otherwise if it is not related, output 'This video is unrelated to the topic'"""
            },
            {
                'role': 'user',
                'content': f'{inputTranscript}'
            },
        ],
    )
    return response.choices[0].message.content


egCode = """
    digraph G {{
        graph [size="20,15!", ratio=fill];  // Use large size and fill the space
        node [shape=box, fontsize=14];  // Node shape and font size
        "Supervised Learning" -> "Uses labeled data to train models";
        "Unsupervised Learning" -> "Uses unlabeled data to discover patterns";
        "Reinforcement Learning" -> "Trains machine to take actions for rewards";
        // Add your other nodes and edges here...
    }}
    
"""
# digraph G {
#     graph [size="20,15!"];
#     node [shape=box, fontsize=14];
#     "Topic" -> "Subtopic 1";
#     "Topic" -> "Subtopic 2";
#     "Subtopic 1" -> "Detail 1";
#     "Subtopic 2" -> "Detail 2";
#     ...
# }
def generate_mindmap(transcript):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                'role':
                'system',
                'content':
                f"""
                You are an expert assistant. Please generate a mindmap using only the graphviz code with the size of size="8,5!" based on the following transcript.
                Output only the graphviz code. Otherwise, nothing. Example: {egCode}
                
"""
            },
            {
                'role': 'user',
                'content': f'{transcript}'
            },
        ],
    )
    mindmap_code = response.choices[0].message.content
    return mindmap_code
