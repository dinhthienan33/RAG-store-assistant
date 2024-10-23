import streamlit as st
from embeddings import SentenceTransformerEmbedding, EmbeddingConfig
from rag.core import RAG
import google.generativeai as genai
from semantic_router import SemanticRouter, Route
from reflection import Reflection
from semantic_router.samples import jobSample, chitchatSample

# Set the API key for Generative AI
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

# Initialize Google Generative AI
if "genai_configured" not in st.session_state:
    genai.configure(api_key=api_key)
    st.session_state.genai_configured = True

# Initialize Reflection and SemanticRouter
if "reflection" not in st.session_state:
    reflection = Reflection(api_key=api_key)
    st.session_state.reflection = reflection

if "semantic_router" not in st.session_state:
    JOB_ROUTE_NAME = 'jobs'
    CHITCHAT_ROUTE_NAME = 'chitchat'
    jobRoute = Route(name=JOB_ROUTE_NAME, samples=jobSample)
    chitchatRoute = Route(name=CHITCHAT_ROUTE_NAME, samples=chitchatSample)
    st.session_state.JOB_ROUTE_NAME = JOB_ROUTE_NAME
    st.session_state.CHITCHAT_ROUTE_NAME = CHITCHAT_ROUTE_NAME
    st.session_state.semantic_router = SemanticRouter(embedding_model, routes=[jobRoute, chitchatRoute])

# Page title
st.title("Career Advisor Chatbot")

# Initialize session state for storing chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to display chat messages
# Function to display chat messages
def display_chat():
    # Check if there are any messages to display
    if "messages" in st.session_state and st.session_state.messages:
        # Loop through each message in the chat history
        for message in st.session_state.messages:
            # Display user messages
            if message["role"] == "user":
                with st.chat_message("user"):
                    for part in message["parts"]:
                        st.markdown(part["text"])
            # Display assistant messages
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    for part in message["parts"]:
                        st.markdown(part["text"])

# Clear Chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()


# Display chat messages
display_chat()

# Input for user query
if prompt := st.chat_input("Ask me something?"):
    # Add user query to chat history
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Reflect the query to enhance the context and standalone meaning
    reflected_query = st.session_state.reflection(st.session_state.messages)

    # Determine the route using SemanticRouter with the reflected query
    guided_route, score = st.session_state.semantic_router.guide(reflected_query)

    # If no route is confidently selected, provide fallback response
    if guided_route is None:
        response = "I'm not sure how to assist with that. Could you provide more details?"
    else:
        # Perform vector search using RAG for knowledge retrieval
        search_results = st.session_state.rag.vector_search(reflected_query)

        # Generate content using the Gemini model (RAG) based on the selected route
        if guided_route == st.session_state.JOB_ROUTE_NAME:
            response = st.session_state.rag.generate_content(reflected_query, search_results)
        elif guided_route == st.session_state.CHITCHAT_ROUTE_NAME:
            response = st.session_state.rag.generate_content(reflected_query, search_results)

    # Add bot response to chat history and display it
        st.session_state.messages.append({"role": "assistant", "parts": [{"text": response}]})
        with st.chat_message("assistant"):
            st.markdown(response)

# Display chat messages again to update the UI
#display_chat()
