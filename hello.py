##### 기본 정보 입력 #####
import streamlit as st
# audiorecorder 패키지 추가
# OpenAI 패키기 추가
import openai
# 파일 삭제를 위한 패키지 추가
import os
# 시간 정보를 위핸 패키지 추가
from datetime import datetime
# 오디오 array 비교를 위한 numpy 패키지 추가
# TTS 패키기 추가
from gtts import gTTS
# 음원파일 재생을 위한 패키지 추가
import base64

##### 기능 구현 함수 #####
def STT(audio):
    # 파일 저장
    filename='input.mp3'
    wav_file = open(filename, "wb")
    wav_file.write(audio.tobytes())
    wav_file.close()

    # 음원 파일 열기
    audio_file = open(filename, "rb")
    #Whisper 모델을 활용해 텍스트 얻기
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()
    # 파일 삭제
    os.remove(filename)
    return transcript["text"]

def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model=model, messages=prompt)
    system_message = response["choices"][0]["message"]
    return system_message["content"]

def TTS(response):
    # gTTS 를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text=response,lang="ko")
    tts.save(filename)

    # 음원 파일 자동 재성
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md,unsafe_allow_html=True,)
    # 파일 삭제
    os.remove(filename)

##### 메인 함수 #####
def main():
    # 기본 설정
    st.set_page_config(
        page_title="📱채팅 비서 프로그램",
        layout="wide")

    flag_start = False

    # session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []

    # 제목 
    st.header("📱채팅 비서 프로그램")
    # 구분선
    st.markdown("---")

    # 기본 설명
    with st.expander("📱채팅비서 프로그램에 관하여", expanded=True):
        st.write(
        """     
        - 채팅비서 프로그램의 UI는 스트림릿을 활용했습니다.
        - 이승윤과 이희찬의 합동 콜라보 개성있는 답변 보여드립니다. 
        - 답변은 OpenAI의 GPT 모델을 활용했습니다. 
        - 질문 맛깔나게 해보십쇼.
        """
        )

        st.markdown("")

    # 사이드바 생성
    with st.sidebar:

        # Open AI API 키 입력받기
        openai.api_key = st.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value="", type="password")

        st.markdown("---")

        # GPT 모델을 선택하기 위한 라디오 버튼 생성
        model = st.radio(label="GPT 모델",options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        # 리셋 버튼 생성
        if st.button(label="초기화"):
            # 리셋 코드 
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a has personality assistant. Respond to all input in 25 words and answer in korea"}]

    # 기능 구현 공간
    col1, col2 =  st.columns(2)
    with col1:
        # 왼쪽 영역 작성
        st.subheader("🙋질문하기")
        
        # 텍스트 입력 상자 추가
        question = st.text_input("질문을 입력하세요", "")

        if st.button("질문"):
            if question:
                # 채팅을 시각화하기 위해 질문 내용 저장
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"] = st.session_state["chat"] + [("🙋", now, question)]
                # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
                st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]
                flag_start = True
            else:
                st.warning("질문을 입력하세요.")

    with col2:
        # 오른쪽 영역 작성
        st.subheader("🙋질문/🙇답변")
        if flag_start:
            #ChatGPT에게 답변 얻기
            response = ask_gpt([{"role": "user", "content": question}], model)

            # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
            st.session_state["messages"] = st.session_state["messages"]+ [{"role": "system", "content": response}]

            # 채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"]+ [("🙇",now, response)]

            # 채팅 형식으로 시각화 하기
            for sender, time, message in st.session_state["chat"]:
                if sender == "🙋":
                    color = "color: black;"
                    st.write('<p style="{}">🙋-질문-🙋</p>'.format(color), unsafe_allow_html=True)
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:black;color:white;border-radius:12px;padding:8px 8px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray; >{time}</div></div>', unsafe_allow_html=True)
                    
                else:
                    color = "color: pink;"
                    st.write('<p style="{}">🙇-답변-🙇</p>'.format(color), unsafe_allow_html=True)
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end width = "30px";"><div style="background-color:pink;border-radius:12px;padding:4px 8px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                   
            
            # gTTS 를 활용하여 음성 파일 생성 및 재생
            TTS(response)

if __name__=="__main__":
    
    main()