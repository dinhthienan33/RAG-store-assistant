import gradio as gr
from rag import RAG, GetLLM, GetCollection

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
    
    # Clear all history upon initialization
    rag_instance.remove_all_history()

    return rag_instance

# Function to handle user queries
def chatbot_interface(query):
    # Reinitialize RAG on each interaction (simulating reset)
    rag = initialize_rag()
    
    # Perform vector search and create prompt
    search_result = rag.vector_search(query=query)
    prompt = rag.create_prompt(search_results=search_result, query=query)
    rag.update_history(role='user', content=prompt)  # Add user query to history

    # Get response from the model
    response = rag.answer_query()
    rag.update_history(role='assistant', content=response)  # Add response to history

    # Stream response back to the user
    full_response = ""
    for chunk in response.split(". "):
        full_response += chunk + ". "
        yield full_response

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as iface:
    gr.Markdown(
        """
        # 🛒 **E-commerce Chatbot**
        **Ask me about products, and I'll provide professional advice tailored to your needs!**
        """
    )
    with gr.Row():
        with gr.Column(scale=2):
            user_input = gr.Textbox(
                lines=2, 
                placeholder="Enter your query here...", 
                label="Your Query",
                interactive=True,
            )
            submit_button = gr.Button("💬 Ask")
            gr.Markdown(
                """
                ### **Sample Questions**
                - **Shop có bán quần short không?**
                - **Áo thun nam giá bao nhiêu vậy?**
                - **Có đồ cho bé gái 3 tuổi không?**
                - **Shop có nhận giao hàng không? Phí ship là bao nhiêu?**
                """
            )
        with gr.Column(scale=3):
            chatbot_output = gr.Textbox(
                label="Chatbot Response", 
                lines=8, 
                interactive=False,
            )

    gr.Markdown(
        """
        ---
        **💡 Tip:** Ask about products using specific queries like "Find me a dress under 200,000 VND."
        """
    )

    # Add Reset Button
    reset_button = gr.Button("🔄 Restart Chat")

    # Connect Submit and Reset Buttons
    submit_button.click(
        fn=chatbot_interface,
        inputs=user_input,
        outputs=chatbot_output,
    )

    reset_button.click(
        fn=lambda: ("", ""),  # Clear user input and chatbot output
        inputs=None,
        outputs=[user_input, chatbot_output],
    )

if __name__ == "__main__":
    iface.launch()
