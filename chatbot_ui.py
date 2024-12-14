import gradio as gr
from rag import RAG, GetLLM, GetCollection
import time

# Global variable to hold the RAG instance
rag_instance = None

# Function to initialize RAG (always initializes a new instance)
def initialize_rag():
    global rag_instance
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

# Function to handle user queries
def chatbot_interface(chat_history, click_count, query):
    # Increment the click counter
    click_count += 1
    if click_count == 1:   
        # Perform vector search and create prompt
        search_result = rag.hybrid_search(query=query)
        prompt = rag.create_prompt(search_results=search_result, query=query)
    else:
        prompt = query
    rag.update_history(role='user', content=prompt)  # Add user query to history

    # Get response from the model
    response = rag.answer_query()
    rag.update_history(role='assistant', content=response)  # Add response to history

    # Update chat history
    chat_history.append(("You", query))
    chat_history.append(("Assistant", ""))

    # Stream response back to the user slowly
    for i in range(len(response)):
        chat_history[-1] = ("Assistant", response[:i+1])
        time.sleep(0.05)  # Adjust the delay as needed
        yield chat_history, click_count, ""  # Clear input box after submit

def clear_history():
    rag_instance.remove_history()

# Gradio Interface
with gr.Blocks(theme=gr.themes.Monochrome()) as iface:
    gr.Markdown(
        """
        # 🛒 **E-commerce Chatbot**
        **Chatbot hỗ trợ mua hang tại shop AnhLong!**
        """
    )

    chat_history = gr.Chatbot(label="Chat History")  # Chatbot component for scrolling
    user_input = gr.Textbox(
        lines=2, 
        placeholder="Enter your query here...", 
        label="Your Query",
    )
    click_counter = gr.State(value=0)  # State to track button clicks
    click_display = gr.Textbox(
        label="Submit Button Click Count", 
        interactive=False,
        value="0",
    )

    submit_button = gr.Button("💬 Ask")
    reset_button = gr.Button("🔄 Restart Chat")

    gr.Markdown(
        """
        ### **Sample Questions**
        - **Shop có bán quần short không?**
        - **Áo thun nam giá bao nhiêu vậy?**
        - **Có đồ cho bé gái 3 tuổi không?**
        - **Shop có nhận giao hàng không? Phí ship là bao nhiêu?**
        - **Tôi cần tư vấn quà tặng sinh nhật ngừoi yêu?**
        
        """
    )

    # Connect submit button
    submit_button.click(
        fn=chatbot_interface,
        inputs=[chat_history, click_counter, user_input],
        outputs=[chat_history, click_counter, user_input],
    )

    # Update the click count display
    submit_button.click(
        fn=lambda click_count: str(click_count),
        inputs=[click_counter],
        outputs=[click_display],
    )

    # Connect reset button to clear chat history, counter, and input
    reset_button.click(
        fn=lambda: ([], 0, ""),  # Clear chat history, reset counter, and input
        inputs=None,
        outputs=[chat_history, click_counter, user_input],
    )
    reset_button.click(
        fn=clear_history,
        inputs=None,
        outputs=None,
    )
    # Reset the click count display
    reset_button.click(
        fn=lambda: "0",
        inputs=None,
        outputs=click_display,
    )

if __name__ == "__main__":
    iface.launch()