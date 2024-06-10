import requests
import streamlit as st
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 

ASSISTANT_ID = "asst_por4rAgGvlqY9JAkvi5T52GN"
VECTOR_STORE_ID = "vs_gS5WxC9skamdxq97gKHCZnky"


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)

def download_file(file_id, filename):
    try:
        url = f'https://api.openai.com/v1/files/{file_id}/content'
        response = requests.get(url, headers={'Authorization': f'Bearer {OPENAI_API_KEY}'}, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success(f"{filename} 다운로드 완료")
        else:
            st.error(f"파일 다운로드 실패: {response.status_code}")
    except Exception as e:
        st.error(f"파일 다운로드 중 오류 발생: {e}")
        

if "file_list" not in st.session_state:
    st.session_state.file_list = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None

with st.sidebar:
     st.markdown("# 백터스토어 등록된 파일")          
     filelist_btn = st.button("조회")

     if filelist_btn :         
        all_files = list(client.beta.vector_stores.files.list(VECTOR_STORE_ID))
        st.session_state.file_list = []
        for file in all_files:    
            url = f'https://api.openai.com/v1/files/{file.id}'
            response = requests.get(url, headers={'Authorization': f'Bearer {st.secrets["OPENAI_API_KEY"]}'})
            file_info = response.json()
            st.session_state.file_list.append(file_info['filename'])
        
        st.subheader(f"",divider="rainbow")
        st.info("파일목록이 생성되었습니다.")
          
     if st.session_state.file_list:
        st.subheader("파일 목록")
        for filename in st.session_state.file_list:            
            st.markdown(filename)
        
     st.markdown("---")
     uploaded_files = st.file_uploader(        
        label="Vector Stores 파일등록",     
        accept_multiple_files=True,
        type=[".pdf"]
     )
     if uploaded_files and st.session_state.uploaded_files is None:
        st.session_state.uploaded_files = uploaded_files         
        if st.session_state.uploaded_files:
            try: 
                #print(uploaded_files.getvalue())
                file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=VECTOR_STORE_ID, files=st.session_state.uploaded_files
                )
                uploaded_files = None
                st.session_state.uploaded_files = None
                st.subheader(f"",divider="rainbow")
                st.info(file_batch.status)
                if(file_batch.status=="completed") :
                    client.beta.assistants.update(
                        assistant_id=ASSISTANT_ID,
                        tool_resources={"file_search": {"vector_store_ids": [VECTOR_STORE_ID]}},
                    )
                    st.success("파일 업로드 및 벡터 저장소 업데이트 완료")                
            except Exception as e:
                st.error(f"처리 중 오류 발생: {e}")
            
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 타이틀
st.title("Demo: OpenAI Assistants API Streaming")

# messages history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Textbox
if user_query := st.chat_input("Ask me a question"):

    # Create a new thread
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # user_query
    with st.chat_message("user"):
        st.markdown(user_query)

    # Store the user's query into the history
    st.session_state.chat_history.append({"role": "user","content": user_query})
    
    # thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_query
        )

    # reply
    with st.chat_message("assistant"):
        stream = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID,
            stream=True
        )
        
        assistant_reply_box = st.empty()
        
        assistant_reply = ""

        # stream 
        for event in stream:
            # streaming events
            # 참조 : https://platform.openai.com/docs/api-reference/assistants-streaming/events
            
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    # empty the container
                    assistant_reply_box.empty()
                    # add the new text
                    assistant_reply += event.data.delta.content[0].text.value
                    # display the new text
                    assistant_reply_box.markdown(assistant_reply)
        
        # update chat history
        st.session_state.chat_history.append({"role": "assistant","content": assistant_reply})
