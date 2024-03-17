from openai import OpenAI
import streamlit as st
import time

# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
#     "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
#     "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
#     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

openai_api_key = "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"
assistant_id = "asst_HDT4d6Jr7eoidbJXdjvmt2IH"
client = OpenAI(api_key=openai_api_key)

with st.sidebar:    
    thread_id  = st.text_input("Thread ID", value="thread_c4yTpTidybBcW0C7qS1e1M3C")
    thread_btn = st.button("Create a new Thred")
    
    if thread_btn :
        thread = client.beta.threads.create()
        thread_id = thread.id

        st.subheader(f"{thread_id}",divider="rainbow")
        st.info("스레드가 생성되었습니다.")


st.title("💬 Chatbot")
# st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    if not thread_id:
        st.info("Please add your thread ID key to continue.")
        st.stop()


    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=prompt,
    )
    print(response)

    run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = assistant_id
    )

    print(run)
    run_id = run.id
    while True :
        run = client.beta.threads.runs.retrieve(
            thread_id = thread_id,
            run_id = run_id
        )
        if run.status == "completed": 
            break
        else :
            time.sleep(2)            
        print(run)

        thread_messages = client.beta.threads.messages.list(thread_id)
        msg = thread_messages.data[0].content[0].text.value
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

        

    

    # response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    # msg = response.choices[0].message.content
    # st.session_state.messages.append({"role": "assistant", "content": msg})
    # st.chat_message("assistant").write(msg)
