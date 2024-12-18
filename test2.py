import gradio as gr
from chatbot import RAG, GetLLM, GetCollection
import time
from semantic_router import Route
from samples import product, chitchat
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.routers import SemanticRouter


# Global variable to hold the RAG instance
rag_instance = None

# Function to initialize RAG (always initializes a new instance)
def initialize_rag():
    # Initialize the LLM
    llm = GetLLM(
        llm_name='llama-3.1-8b-instant',
        api_key='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',
    )
    # Set up the MongoDB connection
    mongodb_uri = "mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs"
    db_name = "product"
    collection_name = "sendo"
    client = GetCollection(mongodb_uri, db_name, collection_name)
    collection = client.get_collection()
    
    # Initialize the RAG instance
    rag_instance = RAG(collection=collection, llm_model=llm)
    rag_instance.remove_history()  # Clear all history upon initialization
    return rag_instance

rag = initialize_rag()

def check_route(query):
    product_route = Route(
        name="product",
        utterances=product,
    )
    chitchat_route = Route(
        name="chitchat",
        utterances=chitchat,
    )

    routes = [product_route, chitchat_route]
    encoder = HuggingFaceEncoder()
    sr = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")
    result = sr(query)
    return result.name

# Function to handle user queries
def chatbot_interface(click_count, query):
    # Check the route of the query
    route = check_route(query)
    if route == "chitchat" and click_count !=0:
        response = "Xin lỗi, tôi chỉ trả lời các câu hỏi liên quan đến sản phẩm sàn thương mại điện tử AnhLong."
        return response

    # Increment the click counter
    click_count += 1
    # if click_count == 1 or click_count > 5:
    #     # Perform vector search and create prompt
    #     search_result = rag.hybrid_search(query=query)
    #     prompt = rag.create_prompt(search_results=search_result, query=query)
    #     if click_count > 3:
    #         rag.remove_message()
    # else:
    #     prompt = query
     # Perform vector search and create prompt
    search_result = rag.hybrid_search(query=query)
    prompt = rag.create_prompt(search_results=search_result, query=query)
    rag.update_history(role='user', content=prompt)  # Add user query to history

    # Get response from the model
    response = rag.answer_query()
    return response
click_count=0
query='cho tôi xem vài sản phẩm đầm đen'
click_count +=1
response = chatbot_interface(click_count, query)
query = 'cho tôi xem thêm nhiều sản phẩm đi'
click_count +=1
response = chatbot_interface(click_count, query)
query = ' cho tôi xem thông tin về sản phầm đầu tiên'
click_count +=1
response = chatbot_interface(click_count, query)
print(rag.get_history())