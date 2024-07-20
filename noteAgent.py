from together import Together
from dotenv import load_dotenv
import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.together import TogetherEmbedding
from llama_index.llms.together import TogetherLLM
from llama_index.core import Settings
import streamlit as st
import fitz
import re

load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")

Settings.llm = TogetherLLM(model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo", api_key=api_key)
Settings.embed_model = TogetherEmbedding(
    model_name="togethercomputer/m2-bert-80M-8k-retrieval", api_key=api_key
)
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
Settings.num_output = 512
Settings.context_window = 3900

def run_rag_completion(documents, query_text: str) -> str:
    index = VectorStoreIndex.from_documents(documents)
    response = index.as_query_engine(similarity_top_k=5).query(query_text)
    return response

client = Together(api_key=api_key)

def generateQuestions(response):
    collected_response = ""
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "You generate questions and answers based on the information I provide. Be descriptive and helpful."},
            {"role": "user", "content": f"Based on this information: {response}, provide me with 10 question and answers with format the response format is Q1: ..., A1: ..., Q2: ..., A2: ..."}
        ],
        stream=True,
    )
    for chunk in stream:
        collected_response += chunk.choices[0].delta.content or ""
    st.write(collected_response)

def flashCards(response):
    collected_response = ""
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "You generate flashcards based on the information I provide you. Be descriptive and helpful."},
            {"role": "user", "content": f"Based on this information: {response}, provide me with 10 flashcards with format the response format is Q1: ..., A1: ..., Q2: ..., A2: ..."}
        ],
        stream=True,
    )
    for chunk in stream:
        collected_response += chunk.choices[0].delta.content or ""
    st.write("Raw Flashcards Response:")
    st.write(collected_response)
    # Assuming the response format is "Q1: ..., A1: ..., Q2: ..., A2: ..."
    flashcards = re.findall(r'(Q\d+:.*?)(?=Q\d+:|$)', collected_response, re.DOTALL)
    st.write("Parsed Flashcards:")
    st.write(flashcards)

    question_answer_pairs = []
    for card in flashcards:
        parts = re.split(r'(A\d+:)', card)
        if len(parts) == 3:
            question = parts[0].strip()
            answer = parts[2].strip()
            question_answer_pairs.append((question, answer))

    if not question_answer_pairs:
        st.warning("No valid flashcards found in the response.")
    else:
        for question, answer in question_answer_pairs:
            with st.expander(question):
                st.write(answer)
                
                
             
def generateMindMap(response):
    collected_response = ""
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "You generate a pictorial mindmap based on the information I provide. Be descriptive and helpful."},
            {"role": "user", "content": f"Based on this information: {response}, provide me with a pictorial mind map based on this topic"}
        ],
        stream=True,
    )
    for chunk in stream:
        collected_response += chunk.choices[0].delta.content or ""
    st.write(collected_response)                
def converseWithRag(prompt, history, documents):
    messages = [{"role": "user", "content": p} for p in history]
    messages.append({"role": "user", "content": prompt})

    try:
        response = run_rag_completion(documents, prompt)
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'documents' not in st.session_state:
    st.session_state['documents'] = []

st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 2rem;
        border-radius: 10px;
        color: black;
    }
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 10px;
    }
    .reportview-container .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    h1, h2, h3, h4, h5, h6 {
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_text(text):
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    return splitter.get_nodes_from_documents([Document(text=text)])

uploaded_files = st.sidebar.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
if uploaded_files:
    with st.spinner('Processing PDFs...'):
        all_documents = []
        for uploaded_file in uploaded_files:
            pdf_text = read_pdf(uploaded_file)
            nodes = split_text(pdf_text)
            all_documents.append(Document(text=pdf_text))
            all_documents.extend(Document(text=node.text) for node in nodes)
        
        st.session_state['documents'] = all_documents
        st.sidebar.success("PDFs uploaded and processed.")
        
        if st.sidebar.button("Generate Flashcards"):
            with st.spinner('Generating flashcards...'):
                response = run_rag_completion(st.session_state['documents'], "Generate flashcards based on the content")
                flashCards(response)
        
        if st.sidebar.button("Generate Questions"):
            with st.spinner('Generating questions...'):
                response = run_rag_completion(st.session_state['documents'], "Generate questions based on the content")
                generateQuestions(response)
        
        st.sidebar.write("Enter a prompt to converse with RAG:")
        prompt = st.sidebar.text_input("Prompt:")
        if st.sidebar.button("Submit Query"):
            with st.spinner('Processing...'):
                if prompt:
                    st.session_state['history'].append(prompt)
                    response = converseWithRag(prompt, st.session_state['history'], st.session_state['documents'])
                    if response:
                        st.session_state['history'].append(response)
                        st.success("Response received:")
                    else:
                        st.error("Failed to get a valid response from the system.")
                else:
                    st.error("Please enter a prompt.")

st.title("Student Multi-Agent System")
st.subheader("RAG based note taking application")

st.markdown("### Conversation")
for i in range(0, len(st.session_state['history']), 2):
    st.markdown(f"**You:** {st.session_state['history'][i]}")
    if i + 1 < len(st.session_state['history']):
        st.markdown(f"**Assistant:** {st.session_state['history'][i + 1]}")

st.markdown("""
    ## How to Use
    1. Upload your PDFs on the left sidebar.
    2. Click "Generate Flashcards" or "Generate Questions" to create study aids.
    3. Enter a query in the prompt box on the left sidebar and click "Submit Query" to converse with the system.
    4. View the response in the main area.

    ## Examples
    - "Can you help me with calculus integration?"
    - "What’s on my schedule for today?"
    - "I need help studying for my biology exam."
""")

st.markdown("""
    ---
    **Student Multi-Agent System** | Developed by ???
""")

