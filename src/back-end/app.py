from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI
from chatbot import RAG, GetLLM, GetCollection
from semantic_router import Route
from samples import product, chitchat
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.routers import SemanticRouter
import re

# Global variable to hold the RAG instance
global_rag = None

def initialize_rag(api_key, mongodb_uri):
    llm = GetLLM(
        llm_name='llama-3.1-8b-instant',
        api_key=api_key,
    )
    db_name = "product"
    collection_name = "sendo"
    client = GetCollection(mongodb_uri, db_name, collection_name)
    collection = client.get_collection()
    rag_instance = RAG(collection=collection, llm_model=llm)
    rag_instance.remove_history()
    return rag_instance

def check_keywords(text: str, keywords: list) -> bool:
    # Convert text to lowercase for case-insensitive matching
    text = text.lower()
    
    # Create regex pattern from keywords
    pattern = '|'.join(map(re.escape, keywords))
    
    # Return True if any keyword matches
    return bool(re.search(pattern, text))

def check_route(query):
    product_route = Route(name="product", utterances=product)
    chitchat_route = Route(name="chitchat", utterances=chitchat)
    routes = [product_route, chitchat_route]
    encoder = HuggingFaceEncoder()
    sr = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")
    result = sr(query)
    return result.name

def chatbot_response(query, rag):
    chat_history = rag.get_history()
    click_count = len(chat_history) // 2
    product_keywords = ['tìm','gợi ý','tư vấn']
    search_result = []  # Initialize to avoid potential UnboundLocalError
    prompt = "đây là một câu."

    # Determine the route
    route = check_route(query)
    if route == "chitchat" or (route is None and click_count != 0) or  not check_keywords(query, product_keywords):
        return "Xin lỗi, tôi chỉ trả lời các câu hỏi liên quan đến sản phẩm sàn thương mại điện tử AnhLong.", []

    if click_count == 0 or check_keywords(query, product_keywords):
        search_result = rag.full_text_search(query=query)
        prompt = rag.create_prompt(search_results=search_result, query=query)
    else:
        prompt = query

    if click_count > 3:
        rag.remove_message()

    rag.update_history(role='user', content=prompt)
    response = rag.answer_query()
    
    return response, search_result

# FastAPI application setup
origins = ["*"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    global global_rag
    global_rag = initialize_rag(
        api_key='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',
        mongodb_uri='mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs'
    )

@app.get("/")
def read_root():
    return {"message": "Shop AnhLong"}

@app.get("/rag/")
async def read_item(q: str | None = None):
    global global_rag
    try:
        if not q:
            return {
                "result": "No query provided",
                "sources": []
            }

        # Process query and get response
        result, search_result = chatbot_response(
            rag=global_rag,
            query=q,
        )
        
        return {
            "result": result,
            "sources": search_result
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "details": "An error occurred while processing the request."
        }
