import google.generativeai as genai

class Reflection:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)

    def _concat_and_format_texts(self, data):
        concatenatedTexts = []
        for entry in data:
            role = entry.get('role', '')
            all_texts = ' '.join(part['text'] for part in entry['parts'])
            concatenatedTexts.append(f"{role}: {all_texts} \n")
        return ''.join(concatenatedTexts)

    def __call__(self, chatHistory, lastItemsConsidereds=100):
        if len(chatHistory) >= lastItemsConsidereds:
            chatHistory = chatHistory[len(chatHistory) - lastItemsConsidereds:]

        historyString = self._concat_and_format_texts(chatHistory)

        higherLevelSummariesPrompt = f"""Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question in English which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is. {historyString}
        """

        print(higherLevelSummariesPrompt)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(higherLevelSummariesPrompt)
    
        return response.text

# Example usage
if __name__ == "__main__":
    api_key = "AIzaSyD7JnSPUV2_ERRN_y2MV-vA_QbJiKpwbRU"
    reflection = Reflection(api_key=api_key)
    
    chat_history = [
        {
            "role": "assistant",
            "parts": [{"text": "Hello, how can I help you today?"}]
        },
        {
            "role": "user",
            "parts": [{"text": "Capital of Franch"}]
            
        },
        {
            "role": "assistant",
            "parts": [{"text": "Paris"}]
        },
        {
            "role": "user",
            "parts": [{"text": "VietNam?"}]
        }
    ]
    
    result = reflection(chat_history)
    print("Generated Question:")
    print(result)