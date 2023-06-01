import os
import streamlit as st
from vidgest.date_helper import DateHelper
from vidgest.openaivideosummarizer import OpenAiVideoSummarizer
from vidgest.youtubeloader import YoutubeLoader


# read youtube API key from environment variables.  If they are not present, prompt them in the app
ENV_YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
ENV_OPENAI_KEY = os.environ.get('OPENAI_KEY')
TARGET_MODEL = 'gpt-3.5-turbo'
NUM_PREVIOUS_DAYS_TO_SEARCH = 5
NUM_VIDEOS_TO_SHOW = 5

def main():
    st.title('Vidgest')

    # Determine if the keys were in the environment variables, if not prompt for them
    if ENV_YOUTUBE_API_KEY and ENV_OPENAI_KEY:
        st.session_state.summarizer = OpenAiVideoSummarizer(TARGET_MODEL, ENV_OPENAI_KEY)
        st.session_state.video_loader = YoutubeLoader(ENV_YOUTUBE_API_KEY)
    
    elif "summarizer" not in st.session_state or "video_loader" not in st.session_state:
        openai_api_key = st.text_input("Your OpenAI API key here", type="password")
        youtube_api_key = st.text_input("Your YouTube API key here", type="password")
        
        if st.button('Submit'):
            st.session_state.summarizer = OpenAiVideoSummarizer(TARGET_MODEL, openai_api_key)
            st.session_state.video_loader = YoutubeLoader(youtube_api_key)


    search_query = st.text_input('YouTube search query')

    # get the videos from the youtube api
    if st.button('Search'):
        with st.spinner('Retriving Videos...'):
            try:
                st.session_state.videos_search_result = st.session_state.video_loader.get_videos(search_query, NUM_PREVIOUS_DAYS_TO_SEARCH)
            except Exception as e:
                st.write(f"Error getting videos: {e}")
                st.session_state.videos_search_result = []

    # Display the search results
    if "videos_search_result" in st.session_state and st.session_state.videos_search_result:

        # sort videos by view count
        sorted_videos = sorted(st.session_state.videos_search_result, key=lambda x: x['view_count'], reverse=True)

        # display the top {NUM_VIDEOS_TO_SHOW} videos
        for i, video in enumerate(sorted_videos[:NUM_VIDEOS_TO_SHOW]):
            st.markdown(f'### {video["title"]}')
            st.image(video['thumbnail_url'])
            st.caption(f'Duration {DateHelper.duration_to_human_readable(video["duration"])}')
            st.caption(f"Channel: {video['channel_title']} :: Posted {DateHelper.get_days_ago(video['published_at'])} days ago  :: Views: {video['view_count']}")
            st.markdown(f'*{video["description"]}*')
            
            if f"transcript-{video['video_id']}" not in st.session_state:
                if st.button('Get Transcript', key=video['video_id']):
                    with st.spinner(f'Fetching Transcript for {video["video_id"]}...'):
                        st.session_state[f"transcript-{video['video_id']}"] = get_video_transcript(video['video_id'])
                        st.write('Generating Summary...')
                        error, summary = get_video_summary(st.session_state[f"transcript-{video['video_id']}"])
                        st.subheader('Summary')
                        if error:
                            st.write(f"**Error summarizing transcript**: *{error}*")
                        else:
                            st.session_state[f"summary-{video['video_id']}"] = summary
                            st.write(st.session_state[f"summary-{video['video_id']}"])
            else:
                st.subheader('Summary')
                st.write(st.session_state[f"summary-{video['video_id']}"])

        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = ''


@st.cache_data
def get_video_summary(transcript: str):
    return st.session_state.summarizer.generate_summary(transcript)

@st.cache_data
def get_video_transcript(video_id: str):
    return st.session_state.video_loader.get_transcript(video_id)


if __name__ == "__main__":
    main()