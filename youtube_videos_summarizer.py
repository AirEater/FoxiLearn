import json
import re
import requests
import streamlit as st
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ["OPEN_API_KEY"])


def get_link_from_prompt(prompt):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=[
                                                  {
                                                      "role":
                                                      "system",
                                                      "content":
                                                      '''
                Monitor user input for potential YouTube links.
                Extract any YouTube links provided by the user.
                Store the extracted YouTube links in a JSON list format: ["youtube_link1", "youtube_link2", ...].
                Only return the list as a JSON string.
                '''
                                                  },
                                                  {
                                                      "role": "user",
                                                      "content": f"{prompt}"
                                                  },
                                              ],
                                              temperature=0.3,
                                              max_tokens=3000)

    response_content = response.choices[0].message.content.strip()

    try:
        links_list = json.loads(response_content)
    except json.JSONDecodeError:
        st.error("Failed to decode JSON. Response: " + response_content)
        links_list = []

    return links_list


def extract_youtube_ids(youtube_links):
    youtube_ids = []
    pattern = r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"

    for link in youtube_links:
        match = re.search(pattern, link)
        if match:
            youtube_ids.append(match.group(1))  # Extract the video ID

    return youtube_ids


def transcript_video(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except TranscriptsDisabled:
        return None
    except NoTranscriptFound:
        return None


def get_transcripts(youtube_links, video_ids):
    transcripts = []

    for i, video_id in enumerate(video_ids):
        transcript = transcript_video(video_id)
        if transcript:
            transcripts.append(transcript)
        else:
            transcripts.append(
                f"No transcript available for video: {youtube_links[i]}")
    return transcripts


def extract_text_from_transcript(transcript):
    return " ".join([entry['text'] for entry in transcript])


def process_transcripts(transcripts, youtube_links):
    processed_transcripts = []

    for i, transcript in enumerate(transcripts):
        if isinstance(transcript, str):
            processed_transcripts.append(transcript)
        else:
            transcript_text = extract_text_from_transcript(transcript)
            if transcript_text.strip() == "":
                processed_transcripts.append(
                    f"No transcription available for video: {youtube_links[i]}."
                )
            else:
                processed_transcripts.append(transcript_text)

    return processed_transcripts


def get_youtube_title(youtube_link):
    header = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    pattern = r'<title>(.*?)</title>'

    try:
        response = requests.get(youtube_link, headers=header)
        response.raise_for_status()

        if response.status_code == 200:
            title_match = re.search(pattern, response.text, re.IGNORECASE)
            if title_match:
                return title_match.group(1).strip()
            else:
                return "Title element not found using regex."
        else:
            return f"Failed to retrieve video page. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Error fetching the video: {e}"


def summarize_video_transcript(processed_transcripts, titles):
    summarization_prompt = '''
    You are an expert summarizer. Based on the given transcript, please provide a concise and insightful summary.
    Output the results in HTML format.
    Don't show the output ```html...```.


    Ensure you:
    - Highlight the key points and main ideas.
    - Use bullet points for clarity.
    - Format the output in HTML using darker shades for text, such as navy blue, dark gray, or black, to enhance readability. Avoid using any light colors.
    - If a transcript is unavailable for a specific video, do not summarize it; instead,, clearly inform the user about it and show it in a visually distinct manner, using bold or colored text that stands out against the background.

    '''

    summaries = []

    for i, transcript_text in enumerate(processed_transcripts):
        video_title = titles[i] if i < len(titles) else "Unknown Title"
        user_prompt = f"{video_title} - {transcript_text}" if transcript_text.strip(
        ) else f"{video_title} - No transcript available."

        response = client.chat.completions.create(model='gpt-3.5-turbo',
                                                  messages=[{
                                                      "role":
                                                      "system",
                                                      "content":
                                                      summarization_prompt
                                                  }, {
                                                      "role":
                                                      "user",
                                                      "content":
                                                      user_prompt
                                                  }],
                                                  max_tokens=3000,
                                                  temperature=0.7)

        summary = response.choices[0].message.content
        formatted_summary = f"**Video: {video_title}**\n" + summary + "\n"
        summaries.append(formatted_summary)

    return summaries


def answer_based_on_summaries(summaries, user_prompt):
    summary = "\n\n".join(summaries)

    evaluation_prompt = f"""
    The user is asking: "{user_prompt}".
    Below are the summaries of several videos provided by the user. 
    Please carefully read each summary and evaluate which video(s) are most suitable to answer the user's query.

    Summaries:
    {summary}

    In your response, please:
    1. Identify all video(s) that are suitable for the user's question. If multiple videos fit, list all of them.
    2. For each suitable video, provide a brief explanation of why it is a good choice, highlighting key aspects from the summary.
    3. If no video is suitable, clearly explain why none of the videos address the user's question (keep this explanation concise).

    Make sure your response is clear, structured, and easy to read. Use bullet points if necessary for clarity.
    """

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{
            "role":
            "system",
            "content":
            "You are an expert in evaluating content based on user queries."
        }, {
            "role": "user",
            "content": evaluation_prompt
        }],
        max_tokens=500,
        temperature=1)

    answer = response.choices[0].message.content
    return answer




if __name__ == "__main__":
    # Streamlit app layout
    st.markdown("""
        <style>
        .summary-box {
            background-color: #f0f0f5;
            border: 1px solid #ccc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-family: Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            color: #333333;  /* Darker text for better readability */
        }
        .video-title {
            font-size: 20px;
            font-weight: bold;
            color: #1a73e8;  /* Adjusted color to a more visible shade of blue */
        }
        .evaluation {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 5px solid #1a73e8;  /* Matching the title color for consistency */
            color: #333333;  /* Dark text for evaluation section as well */
        }
        .youtube-title {
            font-size: 36px; /* Adjust font size as needed */
            font-weight: bold;
            color: #FF0000; /* YouTube Red */
            text-align: center; /* Center the title */
            margin-bottom: 20px; /* Add some space below the title */
        }
        </style>
        """,
                unsafe_allow_html=True)
    
    st.markdown('<h1 class="youtube-title">🎥 YouTube Video Summarizer</h1>',
                unsafe_allow_html=True)
    st.subheader(
        "Analyze and summarize YouTube content to find the best video for your needs."
    )

    # User input section
    st.markdown("### 📝 Please enter your question and provide YouTube links")
    user_input = st.text_area(
        "Type your question and YouTube links:",
        height=50,
        help="You can enter one or multiple YouTube links.")

    # Get Summaries button
    if st.button("Get Summaries"):
        if user_input:
            # Step 1: Extract YouTube links from the user prompt
            youtube_links = get_link_from_prompt(user_input)

            if not youtube_links:
                st.error("No valid YouTube links found in the prompt.")
            else:
                # Step 2: Extract video IDs from the links
                extracted_ids = extract_youtube_ids(youtube_links)

                # Step 3: Get transcripts for the videos
                transcripts = get_transcripts(youtube_links, extracted_ids)

                # Step 4: Process transcripts
                processed_transcripts = process_transcripts(
                    transcripts, youtube_links)

                # Step 5: Get titles for the videos
                titles = [get_youtube_title(link) for link in youtube_links]

                # Step 6: Summarize the transcripts
                summaries = summarize_video_transcript(processed_transcripts,
                                                       titles)

                # Step 7: Answer based on summaries
                answer = answer_based_on_summaries(summaries, user_input)

                # Display summaries in a user-friendly design
                st.header("🔍 Video Summaries")
                for summary in summaries:
                    st.markdown(f'<div class="summary-box">{summary}</div>',
                                unsafe_allow_html=True)

            # Display the evaluation and recommendation for videos
            st.header("🎯 Evaluation of Videos")
            st.markdown(f'<div class="evaluation">{answer}</div>',
                        unsafe_allow_html=True)
        else:
            st.error(
                "⚠️ Please enter a question and YouTube links to proceed.")
