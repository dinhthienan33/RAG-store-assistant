import gradio as gr
from test.backend import initialize_rag, chatbot_logic

# Function to initialize RAG with user-provided API details
def initialize_rag_with_api(api_key, mongodb_uri):
    return initialize_rag(api_key, mongodb_uri)

# Function to handle user queries
def chatbot_interface(chat_history, query):
    global rag
    response = chatbot_logic(chat_history, query, rag)
    chat_history.append(("You", query))
    chat_history.append(("Assistant", response))
    return chat_history, ""

# Function to restart chat
def restart_chat():
    global rag
    rag = initialize_rag()
    return [], ""

# First interface to get API details from the user
def get_api_details(api_key, mongodb_uri):
    global rag
    rag = initialize_rag_with_api(api_key, mongodb_uri)
    return gr.update(visible=True), gr.update(visible=True)

with gr.Blocks(theme=gr.themes.Monochrome()) as iface:
    gr.Markdown("# 🛒 **E-commerce Chatbot**\n**Chatbot hỗ trợ mua hàng tại shop AnhLong!**")

    # API details input
    api_key_input = gr.Textbox(placeholder="Enter your API key...", label="API Key")
    mongodb_uri_input = gr.Textbox(placeholder="Enter your MongoDB URI...", label="MongoDB URI")
    submit_api_button = gr.Button("Submit API Details")

    # Main chatbot interface (initially hidden)
    chat_history = gr.Chatbot(label="Lịch sử hội thoại", visible=False)
    user_input = gr.Textbox(placeholder="Nhập câu hỏi và nhấn Enter...", label="Câu hỏi của bạn", visible=False)
    submit_button = gr.Button("💬 Gửi", visible=False)
    restart_button = gr.Button("🔄 Restart", visible=False)

    submit_api_button.click(
        fn=get_api_details,
        inputs=[api_key_input, mongodb_uri_input],
        outputs=[chat_history, user_input]
    )

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

    restart_button.click(
        fn=restart_chat,
        inputs=None,
        outputs=[chat_history, user_input],
    )

    gr.Markdown("### **Ví dụ câu hỏi**\n- *Shop có bán đầm đen không?*\n- *Áo thun nam giá bao nhiêu?*\n- *Tôi muốn xem thêm sản phẩm.*")

if __name__ == "__main__":
    iface.launch()