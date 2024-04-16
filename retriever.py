from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings.azure import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.chat_models.azure import ChatOpenAI
from langchain.schema import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import shutil
from s3bucket import upload_to_s3
load_dotenv()

vector_database_name = "Adina_Vector_Database"
temp_pdf_folder = "temp-pdf-files"

def delete_temp_files():
    for item in os.listdir(temp_pdf_folder):
        file_path = os.path.join(temp_pdf_folder, item)
        os.remove(file_path)

def initialize_vector_db():
    embeddings = OpenAIEmbeddings()
    vector_database = FAISS.from_texts(["Adina Cosmetic Ingredients"], embeddings)
    vector_database.save_local(f"{vector_database_name}")

def get_vector_db(docs: list[Document]):
    embeddings = OpenAIEmbeddings()
    
    try:
        currentVectorDatabase = FAISS.from_documents(docs, embeddings)
        existingVectorDatabase = FAISS.load_local(f"{vector_database_name}", embeddings, allow_dangerous_deserialization=True)
        
        existingVectorDatabase.merge_from(currentVectorDatabase)
        existingVectorDatabase.save_local(f"{vector_database_name}")

        return existingVectorDatabase
    
    except :
        print("!Warning : Document is empty or not in the correct format. Thus provided pdf(s) are not added to the vector database.")
        return FAISS.load_local(f"{vector_database_name}", embeddings, allow_dangerous_deserialization=True)

def load_and_split(uploaded_files):
    if not os.path.exists(temp_pdf_folder):
        os.makedirs(temp_pdf_folder)

    docs = []
    for file in uploaded_files:
        local_filepath = os.path.join(temp_pdf_folder, file.name)
        with open(local_filepath, "wb") as f:
            f.write(file.getvalue())

        if upload_to_s3(file_path=local_filepath, file_name=file.name):
            print(f"\n{file.name} uploaded successfully.")
        else:
            print(f"\nFailed to upload {file.name}.")

        loader = PyPDFLoader(local_filepath)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap=200
        )
        temp_docs = text_splitter.split_documents(docs)
        docs.extend(temp_docs)
    delete_temp_files()
    return docs

def get_retriever(uploaded_files):
    if os.path.exists(f"{vector_database_name}") == False:
        initialize_vector_db()

    if len(uploaded_files) == 0:
        embeddings = OpenAIEmbeddings()
        vectorDatabase = FAISS.load_local(f"{vector_database_name}", embeddings, allow_dangerous_deserialization=True)

        retriever = vectorDatabase.as_retriever()
        return retriever
    
    docs = load_and_split(uploaded_files)
    vector_database = get_vector_db(docs=docs)
    
    retriever = vector_database.as_retriever()
    return retriever

def get_response(user_query, chat_history):
    retriever = get_retriever(uploaded_files=[])
    docs = retriever.invoke(user_query)

    template = """
    <rules> 
    You name is ADINA, who provides helpful information about Adina Consmetic Ingredients. 
    </rules>
    Execute the below mandatory considerations when responding to the inquiries:
    --- Tone - Respectful, Patient, and Encouraging:
        Maintain a tone that is not only polite but also encouraging. Positive language can help build confidence, especially when they are trying to learn something new.
        Be mindful of cultural references or idioms that may not be universally understood or may date back to a different era, ensuring relatability.
    --- Clarity - Simple, Direct, and Unambiguous:
        Avoid abbreviations, slang, or colloquialisms that might be confusing. Stick to standard language.
        Use bullet points or numbered lists to break down instructions or information, which can aid in comprehension.
    --- Structure - Organized, Consistent, and Considerate:
        Include relevant examples or analogies that relate to experiences common in their lifetime, which can aid in understanding complex topics.
    --- Empathy and Understanding - Compassionate and Responsive:
        Recognize and validate their feelings or concerns. Phrases like, “It’s completely normal to find this challenging,” can be comforting.
        Be aware of the potential need for more frequent repetition or rephrasing of information for clarity.

    Answer the following questions considering the history of the conversation and retrieved information.
    You must have to answer the question based on the retrieved information.
    
    Chat history: {chat_history}

    retrieved information: {retrieved_info}
    
    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(
        model='gpt-3.5-turbo-0125',
        streaming=True
    )
        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "retrieved_info": docs,
        "user_question": user_query,
    })

