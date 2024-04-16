import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from retriever import get_response, get_retriever
st.set_page_config(page_title="Adina Cosmetic Ingredients", page_icon="")
st.title("Adina Cosmetic Ingredients")

# last uploaded files
if "last_uploaded_files" not in st.session_state:
    st.session_state.last_uploaded_files = []

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am Adina. How can I help you?"),
    ]

# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = st.write_stream(
                        get_response(
                            user_query=user_query,
                            chat_history=st.session_state.chat_history
                        )
                    )

    st.session_state.chat_history.append(AIMessage(content=response))

# File uploader
uploaded_files = st.sidebar.file_uploader(
    label="Upload files",
    type='pdf',
    accept_multiple_files=True
)

to_be_vectorised_files = [item for item in uploaded_files if item not in st.session_state.last_uploaded_files]
retriever = get_retriever(to_be_vectorised_files)
st.session_state.last_uploaded_files.extend(to_be_vectorised_files)
