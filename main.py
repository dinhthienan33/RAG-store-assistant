import streamlit as st
from embeddings import SentenceTransformerEmbedding, EmbeddingConfig
from rag.core import RAG  # Assuming the RAG class is in a file named core.py
import google.generativeai as genai
from semantic_router import SemanticRouter, Route
from reflection import Reflection
from semantic_router.samples import jobSample, chitchatSample


api_key = "AIzaSyD7JnSPUV2_ERRN_y2MV-vA_QbJiKpwbRU"
embedding_model = SentenceTransformerEmbedding(
            EmbeddingConfig(name='thenlper/gte-large')
)
# Initialize the RAG class and Gemini model only once
if "rag" not in st.session_state:
    st.session_state.rag = RAG(
        mongodbUri="mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs",
        dbName="test_db",
        dbCollection="test_cl",
        llm_name='gemini-1.5-flash',
        embeddingName='thenlper/gte-large'
    )

if "genai_configured" not in st.session_state:
   
    genai.configure(api_key=api_key)
    st.session_state.genai_configured = True

if "semantic_router" not in st.session_state:
    llm = genai.GenerativeModel("gemini-1.5-flash")
    reflection = Reflection(api_key=api_key)
    JOB_ROUTE_NAME = 'jobs'
    CHITCHAT_ROUTE_NAME = 'chitchat'
    productRoute = Route(name=JOB_ROUTE_NAME, samples=jobSample)
    chitchatRoute = Route(name=CHITCHAT_ROUTE_NAME, samples=chitchatSample)
    st.session_state.reflection = reflection
    st.session_state.JOB_ROUTE_NAME = JOB_ROUTE_NAME
    st.session_state.CHITCHAT_ROUTE_NAME = CHITCHAT_ROUTE_NAME
    st.session_state.semantic_router = SemanticRouter(embedding_model, routes=[productRoute, chitchatRoute])

st.title("Career Advisor Chatbot")

# Initialize session state for storing chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to display chat messages
def display_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            for part in message["parts"]:
                st.markdown(part["text"])

# Display chat messages
display_chat()

# Input for user query
if prompt := st.chat_input("Ask me something?"):
    # Add user query to chat history
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determine the route using SemanticRouter
    guided_route = st.session_state.semantic_router.guide(prompt)[1]

    if guided_route == st.session_state.JOB_ROUTE_NAME:
        # Initialize data if not already done
        if "data" not in st.session_state:
            st.session_state.data = []

        # Ensure combined_information is defined
        search_results = st.session_state.rag.vector_search(prompt)


        # Append user query to data
        st.session_state.data.append({
            "role": "user",
            "parts": [
                {
                    "text": search_results,
                }
            ]
        })

        # Add user query to chat history
        st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})

        # Get the last message from chat history
        data = st.session_state.messages[-1]

        # Use Reflection to enhance the query
        reflected_query = st.session_state.reflection(data["parts"][0]["text"])

        # Update the prompt with the reflected query
        prompt = reflected_query

    # Perform vector search
    search_results = st.session_state.rag.vector_search(prompt)

    # Generate content using the Gemini model
    response = st.session_state.rag.generate_content(prompt, search_results)

    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "parts": [{"text": response}]})

    # Display bot response
    with st.chat_message("assistant"):
        st.markdown(response)

# Display chat messages again to update the UI
display_chat()