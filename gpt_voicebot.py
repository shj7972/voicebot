import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
from datetime import datetime
import numpy as np
from gtts import gTTS
import base64

##### Function implementation functions #####
def STT(audio):
    # file save
    filename = "input.mp3"
    wav_file = open(filename, "wb")
    wav_file.write(audio.tobytes())
    wav_file.close()

    # Open music file
    audio_file = open(filename, "rb")
    # Obtaining text using the whisper model
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()
    # file remove
    os.remove(filename)
    return transcript["text"]

def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model=model, messages=prompt)
    system_message = response["choices"][0]["message"]
    return system_message["content"]

def TTS(response):
    # Create voice files using gTTS
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)

    # Automatic playback of sound files
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>    
            """
        st.markdown(md, unsafe_allow_html=True)
    # file remove
    os.remove(filename)

##### main function #####
def main():
    # basic config
    st.set_page_config(
        page_title="Voice Assistant Program",
        layout="wide"
    )

    flag_start = False

    # session state reset
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in Korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []

    # title
    st.header("Voice Assistant Program")

    # dividing line
    st.markdown("---")

    # basic description
    with st.expander("About the voice assistant program...", expanded=True):
        st.write(
        """
        - The UI of the voice assistant program utilized Streamlet.
        - STT (Speech-To-Speech) utilized OpenAI's Whisper AI.
        - The answer utilized OpenAI's GPT model.
        - TTS (Text-To-Speech) utilized Google's Google Translate TTS.
        """    
        )

        st.markdown("")

    # side bar
    with st.sidebar:

        # Open AI API Key Input
        openai.api_key = st.text_input(label="OPENAI API Key", placeholder="Enter Your API Key", value="", type="password")

        st.markdown("---")

        # Create radio button to select GPT model
        model = st.radio(label="GPT Model", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        # Reset Button
        if st.button(label="Reset"):
            # Reset Logic
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in Korea"}]

    # Function implementation
    col1, col2 = st.columns(2)
    with col1:
        # left area
        st.subheader("Ask a question")
        # voice record icon
        audio = audiorecorder("Click to record", "recording...")
        if len(audio) > 0 and not np.array_equal(audio, st.session_state["check_audio"]): # When you start recording
            # voice playback
            st.audio(audio.tobytes())
            # Extract text from sound files
            question = STT(audio)

            # Save questions to visualize chat
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            # Save question content
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]
            # Store audio information to check audio buffer
            st.session_state["check_audio"] = audio
            flag_start = True

    with col2:
        # right area
        st.subheader("Question/Answer")
        if flag_start:
            # Get answers from chatGPT
            response = ask_gpt(st.session_state["messages"], model)

            # Save answers for prompts to put into GPT model
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]

            # Save answers for chat visualization
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            # Visualize in chat format
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:    
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")

            # Create and play voice files using gTTS
            TTS(response)

if __name__=="__main__":
    main()        

