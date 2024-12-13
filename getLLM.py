
from groq import Groq

class GetLLM:
    def __init__(self,
                 llm_name:str ,
                 api_key: str = None):
        """
        Initialize the RAG class.

        Args:
        api_key (str, optional): API key for the language model.
        """
        self.Groqclient=Groq(api_key=api_key)
        self.llm_name=llm_name

    def generate_content(self, prompt_structure):
        """
        Generate content using the generative AI model.

        Returns:
        str: The generated response.
        """
        # Prepare the data payload for the API request
        data = {
            "model": self.llm_name,
            "messages": prompt_structure,
        }

        # Generate the response using the generative AI model
        chat_completion = self.Groqclient.chat.completions.create(**data)
        response = chat_completion.choices[0].message.content
        return response
    



if __name__ == "__test__":
    llm= GetLLM(llm_name='llama-3.1-8b-instant',api_key = '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')
    prompt_structure = [
        {
            "role": "system",
            "content": "You are a helpful assistant! Your name is Bob."
        },
        {
            "role": "user",
            "content": "What is your name?"
        }
    ]
    print(llm.generate_content(prompt_structure))
    


