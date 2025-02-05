from chatbot import RAG, GetLLM, GetCollection
from semantic_router import Route
from samples import product, chitchat
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.routers import SemanticRouter

# Global variable to hold the RAG instance
rag_instance = None

def initialize_rag(api_key, mongodb_uri):
    llm = GetLLM(
        llm_name='llama-3.1-8b-instant',
        api_key=api_key,
    )
    mongodb_uri = mongodb_uri
    db_name = "product"
    collection_name = "sendo"
    client = GetCollection(mongodb_uri, db_name, collection_name)
    collection = client.get_collection()
    rag_instance = RAG(collection=collection, llm_model=llm)
    rag_instance.remove_history()
    return rag_instance

def check_route(query):
    product_route = Route(name="product", utterances=product)
    chitchat_route = Route(name="chitchat", utterances=chitchat)
    routes = [product_route, chitchat_route]
    encoder = HuggingFaceEncoder()
    sr = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")
    result = sr(query)
    return result.name

def chatbot_response(chat_history, query, rag):
    click_count = len(chat_history) // 2

    route = check_route(query)
    if route == "chitchat" or (route == None and click_count != 0):
        return "Xin lỗi, tôi chỉ trả lời các câu hỏi liên quan đến sản phẩm sàn thương mại điện tử AnhLong."

    if click_count == 0:
        search_result = rag.full_text_search(query=query)
        prompt = rag.create_prompt(search_results=search_result, query=query)
        if click_count > 3:
            rag.remove_message()
    else:
        prompt = query

    rag.update_history(role='user', content=prompt)
    response = rag.answer_query()
    return response
