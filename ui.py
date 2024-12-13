import gradio as gr

# Define the chatbot's response function
def chatbot_response(user_input, history=[]):
    """
    Simulate chatbot response based on user input and chat history.

    Args:
    user_input (str): User's message.
    history (list): Conversation history.

    Returns:
    tuple: Updated chatbot response and conversation history.
    """
    # Simulate a response
    response = f"Chatbot: I'm here to help with your query about '{user_input}'. Please provide more details if needed!"
    
    # Update the chat history
    history.append(("User: " + user_input, response))
    return history, history

# Build the Gradio interface
with gr.Blocks() as chatbot_interface:
    gr.Markdown(
        """
        # 🤖 Welcome to Chatbot Land!
        Ask me anything, and I'll do my best to assist you.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            chat_box = gr.Chatbot(label="Chat History").style(height=400)
        with gr.Column(scale=1):
            user_input = gr.Textbox(
                label="Your Message", placeholder="Type your message here...", lines=2
            )
            submit_button = gr.Button("Send")
    
    # Bind the response function
    submit_button.click(chatbot_response, inputs=[user_input, chat_box], outputs=[chat_box, chat_box])

# Launch the interface
chatbot_interface.launch()
