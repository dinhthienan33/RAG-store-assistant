from IPython.display import Markdown
import textwrap
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize
from getCollection import GetCollection
from getLLM import GetLLM
class RAG:
    def __init__(self,
                 embeddingName: str = 'dangvantuan/vietnamese-embedding',
                 llm_model: GetLLM = None,
                 collection: GetCollection =None, 
                 history: list = None):
        """
        Initialize the RAG class.

        Args:
        mongodbUri (str): MongoDB URI for connecting to the database.
        dbName (str): Name of the database.
        dbCollection (str): Name of the collection within the database.
        llm_name (str, optional): Name of the language model to use.
        embeddingName (str, optional): Name of the embedding model to use.
        api_key (str, optional): API key for the language model.
        """
        self.llm = llm_model
        self.collection = collection
        self.embedding_model = SentenceTransformer(embeddingName)
        self.tokenize = tokenize
        self.chat_history = history or [
    {
        "role": "system",
        "content": (
            "Bạn tên Lan, là một người tư vấn sản phẩm cho sàn thương mại điện tử AnhLong. "
            "Dựa vào thông tin được cung cấp từ hệ thống và câu hỏi của khách hàng, bạn sẽ đưa ra câu trả lời tốt nhất, ngắn gọn nhất. "
            "Hãy nhớ rằng bạn cần thể hiện sự chuyên nghiệp và tận tâm. "
            "Chỉ đưa ra 5 sản phẩm đầu tiên thôi. Nếu khách cần thêm, hãy đưa ra những cái còn lại"
            "đừng lặp lại sản phẩm đã tư vấn "
            "nếu khách hỏi về hàng hóa thì hãy trả lời, còn không thì bạn hãy nói kiến thức của bạn chỉ dành cho tư vấn khách hàng"
            f"Xưng hô là 'em' và khách là anh."
        )
    }
]
    def get_embedding(self, text):
        """
        Generate an embedding for the given text.

        Args:
        text (str): The text to generate an embedding for.

        Returns:
        list: The generated embedding as a list.
        """
        if not text.strip():
            return []
        tokenized_text = self.tokenize(text)
        embedding = self.embedding_model.encode(tokenized_text)
        return embedding.tolist()

    def vector_search(self, query):
        """
        Perform vector search in the MongoDB collection.

        Args:
        query (str): The query text.

        Returns:
        list: A list of search results from the collection.
        """
        embeddings = self.get_embedding(query)
        pipeline = [
            {
                "$vectorSearch": {
                "index": "vector_index",
                "queryVector": embeddings,
                "path": "embedding",
                "numCandidates": 1000,  # Number of candidate matches to consider
                "limit": 10  # Return top 'limit' matches
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'name': 1,
                    'price': 1,
                    'final_price': 1,
                    'shop_free_shipping': 1,
                    'attribute': 1,
                    'description': 1
                }
            }
        ]

        # Execute the aggregation pipeline
        results = list(self.collection.aggregate(pipeline))
        return results

    def create_prompt(self,search_results,query):
        """
        Create a prompt from search results.

        Args:
        search_results (list): The search results.

        Returns:
        str: The generated prompt.
        """
        # Map each document using the projection fields
        info = []
        for item in search_results:
            # Safely extract fields with fallback values
            mapped_item = {
                'name': item.get('name', 'Không có tên sản phẩm'),
                'price': item.get('price', 'Không có thông tin giá'),
                'final_price': item.get('final_price', 'Không có thông tin giá cuối'),
                'shop_free_shipping': 'Có' if item.get('shop_free_shipping', 0) else 'Không',
                'attribute': item.get('attribute', 'Không có thông tin thuộc tính'),
                'description': item.get('description', 'Không có mô tả'),
            }
            info.append(mapped_item)

        # Build the prompt text
        product_details = "\n".join(
            [f"- Tên sản phẩm: {prod['name']}, Giá: {prod['price']}, Giá sau giảm: {prod['final_price']}, "
             f"Miễn phí giao hàng: {prod['shop_free_shipping']}, Thuộc tính: {prod['attribute']}, "
             f"Mô tả: {prod['description']}" for prod in info]
        )

        # Generate the final prompt
        prompt = f"""
        Thông tin bạn nhận được, dùng cái này kèm với câu hỏi từ khách hàng để TƯ VẤN, nếu ở đây không có, hãy dựa vào thông tin ban đầu nhận được. Hạn chế sử dụng thông tin không được cung cấp, không được trả lời sản phẩm trùng với sản phẩm đã tư vấn trước đó, trả lời CHÍNH XÁC tên được cung cấp:
        {product_details}
        Khách hàng: 
        {query}
        Answer:
        """
        return prompt
    def update_history(self, role, content):
        """
        Update the conversation history.

        Args:
        role (str): The role of the participant ('user' or 'assistant').
        content (str): The message content.

        Returns:
        list: The updated history.
        """
        self.chat_history.append({"role": role, "content": content})
        return self.chat_history
    def remove_history(self, role, content):
        """
        Remove a message from the conversation history.

        Args:
        role (str): The role of the participant ('user' or 'assistant').
        content (str): The message content.

        Returns:
        list: The updated history.
        """
        self.chat_history = [msg for msg in self.chat_history if not (msg["role"] == role and msg["content"] == content)]
        return self.chat_history
    def remove_all_history(self):
        """
        Remove all messages from the conversation history.

        Returns:
        list: An empty history.
        """
        self.chat_history = [
    {
        "role": "system",
        "content": (
            "Bạn tên Lan, là một người tư vấn sản phẩm cho sàn thương mại điện tử AnhLong. "
            "Dựa vào thông tin được cung cấp từ hệ thống và câu hỏi của khách hàng, bạn sẽ đưa ra câu trả lời tốt nhất, ngắn gọn nhất. "
            "Hãy nhớ rằng bạn cần thể hiện sự chuyên nghiệp và tận tâm. "
            "Chỉ đưa ra 5 sản phẩm đầu tiên thôi. Nếu khách cần thêm, hãy đưa ra những cái còn lại"
            "đừng lặp lại sản phẩm đã tư vấn "
            "nếu khách hỏi về hàng hóa thì hãy trả lời, còn không thì bạn hãy nói kiến thức của bạn chỉ dành cho tư vấn khách hàng"
            f"Xưng hô là 'em' và khách là anh."
        )
    }
]
    def answer_query(self):
        """
        Generate content using the generative AI model.

        Returns:
        str: The generated response.
        """
        prompt_structure = self.chat_history
        response = self.llm.generate_content(prompt_structure)
        self.update_history("assistant", response)
        return response

    @staticmethod
    def _to_markdown(text):
        """
        Convert text to Markdown format.

        Args:
        text (str): The text to convert.

        Returns:
        Markdown: The converted Markdown text.
        """
        text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
if __name__ == '__test__':
    llm= GetLLM(llm_name='llama-3.1-8b-instant',api_key = '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')
    mongodb_uri = "mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs"
    db_name = "product"
    collection_name = "sendo"
    client = GetCollection(mongodb_uri, db_name, collection_name)
    collection=client.get_collection()
    rag=RAG(collection=collection,llm_model=llm)
    query='đầm dự tiệc'
    print(query)
    search_result=rag.vector_search(query=query)
    prompt=rag.create_prompt(search_results=search_result,query=query)
    rag.update_history(role='user',content=prompt)
    respone=rag.answer_query()
    print(respone)
    query = 'trong những sản phẩm trên, có sản phẩm nào giảm giá không'
    print(query)
    rag.update_history(role='user',content=query)
    respone=rag.answer_query()
    print(respone)
    