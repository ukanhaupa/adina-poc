import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from retriever import get_response, get_retriever

st.set_page_config(page_title="Adina Cosmetics Ingredients", page_icon="")
header = st.container()
header.title("Adina Cosmetics Ingredients")
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

### Custom CSS for the sticky header
st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
        position: sticky;
        top: 2.875rem;
        background-color: #0E1117;
        z-index: 999;
    }
    .fixed-header {
        border: 2px solid #262730;
        border-radius: 5px;
    }
</style>
    """,
    unsafe_allow_html=True
)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
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
last_uploaded_files = []
uploaded_files = st.sidebar.file_uploader(
    label="Upload files",
    type='pdf',
    accept_multiple_files=True
)
if uploaded_files == last_uploaded_files:
    retriever = get_retriever(uploaded_files=[])
else:
    retriever = get_retriever(uploaded_files)
    last_uploaded_files = uploaded_files