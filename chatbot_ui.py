import gradio as gr
from chatbot import RAG, GetLLM, GetCollection
from semantic_router import Route
from samples import product, chitchat
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.routers import SemanticRouter

# Global variable to hold the RAG instance
rag_instance = None

# Function to initialize RAG
def initialize_rag():
    llm = GetLLM(
        llm_name='llama-3.1-8b-instant',
        api_key='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',
    )
    mongodb_uri = "mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs"
    db_name = "product"
    collection_name = "sendo"
    client = GetCollection(mongodb_uri, db_name, collection_name)
    collection = client.get_collection()
    rag_instance = RAG(collection=collection, llm_model=llm)
    rag_instance.remove_history()
    return rag_instance

rag = initialize_rag()

# Route checking
def check_route(query):
    product_route = Route(name="product", utterances=product)
    chitchat_route = Route(name="chitchat", utterances=chitchat)
    routes = [product_route, chitchat_route]
    encoder = HuggingFaceEncoder()
    sr = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")
    result = sr(query)
    return result.name

# Chatbot logic
def chatbot_interface(chat_history, query):
    global rag  # Access global RAG instance
    click_count = len(chat_history) // 2  # Count user messages as clicks

    # Check route for chitchat
    route = check_route(query)
    if route == "chitchat"  or route == None and click_count != 0:
        response = "Xin lỗi, tôi chỉ trả lời các câu hỏi liên quan đến sản phẩm sàn thương mại điện tử AnhLong."
        chat_history.append(("You", query))
        chat_history.append(("Assistant", response))
        return chat_history, ""

    # Logic for RAG response
    if click_count == 0 or click_count > 5:
        search_result = rag.full_text_search(query=query)
        prompt = rag.create_prompt(search_results=search_result, query=query)
        if click_count > 3:
            rag.remove_message()
    else:
        prompt = query

    rag.update_history(role='user', content=prompt)
    response = rag.answer_query()
    chat_history.append(("You", query))
    chat_history.append(("Assistant", response))
    return chat_history, ""

# Restart function to clear history
def restart_chat():
    global rag
    rag = initialize_rag()
    return [], ""

# Gradio UI
with gr.Blocks(theme=gr.themes.Monochrome()) as iface:
    gr.Markdown("# 🛒 **E-commerce Chatbot**\n**Chatbot hỗ trợ mua hàng tại shop AnhLong!**")

    chat_history = gr.Chatbot(label="Lịch sử hội thoại")
    user_input = gr.Textbox(placeholder="Nhập câu hỏi và nhấn Enter...", label="Câu hỏi của bạn")
    submit_button = gr.Button("💬 Gửi")
    restart_button = gr.Button("🔄 Restart")

    # Event: Submit message
    user_input.submit(
        fn=chatbot_interface,
        inputs=[chat_history, user_input],
        outputs=[chat_history, user_input],
    )
    submit_button.click(
        fn=chatbot_interface,
        inputs=[chat_history, user_input],
        outputs=[chat_history, user_input],
    )

    # Event: Restart chat
    restart_button.click(
        fn=restart_chat,
        inputs=None,
        outputs=[chat_history, user_input],
    )

    gr.Markdown("### **Ví dụ câu hỏi**\n- *Shop có bán đầm đen không?*\n- *Áo thun nam giá bao nhiêu?*\n- *Tôi muốn xem thêm sản phẩm.*")

if __name__ == "__main__":
    iface.launch()
