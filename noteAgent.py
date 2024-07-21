from together import Together
from dotenv import load_dotenv
import os
from llama_index.core import VectorStoreIndex, Document
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

def connectLLM(response):
    collected_response = ""
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "You are an expert at explaining topics in detail."},
            {"role": "user", "content": f"Based on this information: {response}, explain these topics to me in detail"}
        ],
        stream=True,
    )
    for chunk in stream:
        collected_response += chunk.choices[0].delta.content or ""
        
    st.write(collected_response)
    st.session_state['history'].append(f"\n{collected_response}")
    return collected_response

    
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
    
    # Parse the collected_response into questions and answers
    qa_pairs = []
    lines = collected_response.split('\n')
    current_question = None
    for line in lines:
        if line.startswith('Q'):
            current_question = line
        elif line.startswith('A') and current_question:
            qa_pairs.append((current_question, line))
            current_question = None
    
    return qa_pairs, collected_response


def generateFlashcards(response):
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
    
    # Parse the collected_response into flashcards
    flashcards = []
    lines = collected_response.split('\n')
    current_question = None
    for line in lines:
        if line.startswith('Q'):
            current_question = line[line.index(':')+1:].strip()
        elif line.startswith('A') and current_question:
            answer = line[line.index(':')+1:].strip()
            flashcards.append((current_question, answer))
            current_question = None
    
    return flashcards, collected_response  # Return both flashcards and the raw response

mindmapFormat = '''
Main Topic
|
|-- Subtopic 1
|   |-- Detail 1.1
|   |-- Detail 1.2
|   |-- Detail 1.3
|
|-- Subtopic 2
|   |-- Detail 2.1
|   |-- Detail 2.2
|   |-- Detail 2.3
|
|-- Subtopic 3
|   |-- Detail 3.1
|   |-- Detail 3.2
|   |-- Detail 3.3
|
|-- Subtopic 4
    |-- Detail 4.1
    |-- Detail 4.2
    |-- Detail 4.3''' 

def generateMindMap(response):
    collected_response = ""
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": f"You are an expert at generating mind maps based on this format: {mindmapFormat} Based on the information I provide, create a descriptive and organized mind map."},
            {"role": "user", "content": f"Please create a mind map using this format: {mindmapFormat} and based on the following information: {response}"}
        ],
        stream=True,
    )
    for chunk in stream:
        collected_response += chunk.choices[0].delta.content or ""
    
    # The collected_response is already in the desired format, so we can return it directly
    return collected_response

def converseWithRag(prompt, history, documents):
    messages = [{"role": "user", "content": p} for p in history]
    messages.append({"role": "user", "content": prompt})

    try:
        response = run_rag_completion(documents, prompt)
        responseLLM = connectLLM(response)
        return responseLLM
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'documents' not in st.session_state:
    st.session_state['documents'] = []
    st.session_state['pdf_processed'] = False


# st.markdown("""
#     <style>
#     .main {
#         background-color: #f5f5f5;
#         padding: 2rem;
#         border-radius: 10px;
#         color: black;
#     }
#     .sidebar .sidebar-content {
#         background-color: #f0f0f0;
#         padding: 1rem;
#         border-radius: 10px;
#     }
#     .reportview-container .main .block-container {
#         max-width: 800px;
#         padding-top: 2rem;
#     }
#     h1, h2, h3, h4, h5, h6 {
#         color: black;
#     }
#     </style>
# """, unsafe_allow_html=True)

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_text(text):
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    return splitter.get_nodes_from_documents([Document(text=text)])

def main():
    
    st.title("Study Buddy")
    st.markdown("""
        ## How to Use
        1. Upload your PDFs on the left sidebar.
        2. Click "Generate Flashcards" or "Generate Questions" or "Generate mind map" to create study aids.
        3. Enter a query in the prompt box on the left sidebar and click "Submit Query" to converse with the system.
        4. View the response in the main area.
        
    """)

    # File uploader can be placed outside the tabs, perhaps in a sidebar
    st.header("Upload Documents")
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)


    if uploaded_files:
        if not st.session_state['pdf_processed']:
            with st.spinner('Processing PDFs...'):
                all_documents = []
                for uploaded_file in uploaded_files:
                    pdf_text = read_pdf(uploaded_file)
                    nodes = split_text(pdf_text)
                    all_documents.append(Document(text=pdf_text))
                    all_documents.extend(Document(text=node.text) for node in nodes)
                
                st.session_state['documents'] = all_documents
                st.success("PDFs uploaded and processed.")
                st.session_state['pdf_processed'] = True
    if st.session_state['pdf_processed']:

    # Assuming you've already set up your RAG model and other necessary imports

        tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Flashcards", "Questions", "Mind Map"])

        with tab1:
            st.header("Chat with AI")
            with st.chat_message(name="user"):
                prompt = st.text_input("What topic do you need help with?")
            with st.chat_message(name="ai"): 
                if st.button("Submit Query"):
                    if prompt:
                        with st.spinner('Processing...'):
                            st.session_state['history'].append(prompt)
                            response = converseWithRag(prompt, st.session_state['history'], st.session_state['documents'])
                            if response:
                                st.session_state['history'].append(response)
                                st.success("Response received:")
                                st.write(response)
                            else:
                                st.error("Failed to get a response. Please try again.")

                    else:
                        st.error("Please enter a topic or question.")

        with tab2:
            st.header("Flashcards")
            if st.button("Generate Flashcards"):
                with st.spinner('Generating flashcards...'):
                    response = run_rag_completion(st.session_state['documents'], "Generate flashcards based on the content")
                    flashcards, raw_response = generateFlashcards(response)
                    if flashcards:
                        for i, (question, answer) in enumerate(flashcards):
                            with st.expander(f"Flashcard {i+1}: {question}"):
                                st.write(answer)
                    else:
                        st.warning("No flashcards were generated. Please try again.")

                # Add to history
                st.session_state['history'].append("Generate Flashcards")
                st.session_state['history'].append(f"**Generated Flashcards:**\n{raw_response}")

        with tab3:
            st.header("Generated Questions")
            if st.button("Generate Questions"):
                with st.spinner('Generating questions...'):
                    response = run_rag_completion(st.session_state['documents'], "Generate questions based on the content")
                    qa_pairs, raw_response = generateQuestions(response)
                    if qa_pairs:
                        for i, (question, answer) in enumerate(qa_pairs):
                            st.write(f"{question}")
                            with st.expander("Show Answer"):
                                st.write(answer)
                    else:
                        st.warning("No questions were generated. Please try again.")

                # Add to history
                st.session_state['history'].append("Generate Questions")
                st.session_state['history'].append(f"**Generated Questions:**\n{raw_response}")

        with tab4:
            st.header("Mind Map")
            if st.button("Generate Mind Map"):
                with st.spinner('Generating a mind map...'):
                    response = run_rag_completion(st.session_state['documents'], "Generate a mind map based on the content")
                    mind_map = generateMindMap(response)
                    if mind_map:
                        st.markdown(f"```\n{mind_map}\n```")  # Display the mind map as text
                    else:
                        st.warning("Failed to generate a mind map. Please try again.")

                # Add to history
                st.session_state['history'].append("Generate Mind Map")
                st.session_state['history'].append(f"**Generated Mind Map:**\n{mind_map}")

    st.markdown("***")
    with st.expander("Conversation"):
        for i in range(0, len(st.session_state['history']), 2):
            st.markdown(f"**You:** {st.session_state['history'][i]}")
            if i + 1 < len(st.session_state['history']):
                st.markdown(f"**Assistant:** {st.session_state['history'][i + 1]}")


    st.markdown("""
        ---
        **Student Multi-Agent System** | Developed by ???
    """)

if __name__ == "__main__":
    main()
