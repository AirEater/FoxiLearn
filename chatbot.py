import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPEN_API_KEY'])


def chatbot_response(user_input):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                'role':
                'system',
                'content':
                f"""
                You are an expert lecturer. Please solve the question by the user. Output it in the format of:
                ```
                Answer (if have)
                Explanation
                Example
                ``` Otherwise if it is a non-academic problems, output 'Sorry, I cannot help with this''"""
            },
            {
                'role': 'user',
                'content': f'{user_input}'
            },
        ],
    )
    mindmap_code = response.choices[0].message.content
    return mindmap_code
