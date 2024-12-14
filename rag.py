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
            "đừng lặp lại sản phẩm đã tư vấn "
            " chỉ trả lời những câu hỏi liên quan tới hàng hóa, nếu có  câu hỏi nào khác hãy trả lời : 'Tôi không có thông tin gì về câu hỏi của anh'"
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
                "limit": 5  # Return top 'limit' matches
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
    def full_text_search(self, query):
        """
        Perform full-text search in the MongoDB collection.
        """
        pipeline=[{
            '$search': {
                'index': 'default', 
                'text': {
                    'query': query, 
                    'path': ['name','description'],  
                }
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
        },
        {
            '$limit': 5
        }]
        results = list(self.collection.aggregate(pipeline))
        return results

    def hybrid_search(self, query):
        """
        Perform a hybrid search combining vector search and full-text search.

        Args:
        query (str): The query text.

        Returns:
        list: A combined list of search results from vector and full-text search.
        """
        # Perform vector search
        vector_results = self.vector_search(query)

        # Perform full-text search
        text_results = self.full_text_search(query)

        # Combine results
        combined_results = vector_results + text_results

        # Deduplicate results based on 'name'
        seen = set()
        unique_results = []
        for result in combined_results:
            if result['name'] not in seen:
                unique_results.append(result)
                seen.add(result['name'])

        # Optionally sort or rank results if needed
        # For example, prioritize vector results
        # unique_results = sorted(unique_results, key=lambda x: x.get('source', 'text') == 'vector', reverse=True)

        return unique_results
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

    def remove_message(self, role=None, content=None):
        """
        Remove the first message from the conversation history.

        Args:
        role (str, optional): The role of the participant ('user' or 'assistant'). If provided, only messages with this role will be considered.
        content (str, optional): The message content. If provided, only messages with this content will be considered.

        Returns:
        list: The updated history.
        """
        if role is None and content is None:
            # Remove the second message if no role or content is specified
            if self.chat_history:
                self.chat_history.pop(1)
        else:
            # Remove the first message that matches the role and/or content
            for i, msg in enumerate(self.chat_history):
                if (role is None or msg["role"] == role) and (content is None or msg["content"] == content):
                    self.chat_history.pop(i)
                    break
        return self.chat_history
    def remove_history(self):
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
            "đừng lặp lại sản phẩm đã tư vấn "
            "nếu khách hỏi về hàng hóa thì hãy trả lời, còn không thì bạn hãy nói kiến thức của bạn chỉ dành cho tư vấn khách hàng về những sản phẩm"
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
if __name__ == '__main__':
    llm= GetLLM(llm_name='llama-3.1-8b-instant',api_key = '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')
    mongodb_uri = "mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs"
    db_name = "product"
    collection_name = "sendo"
    client = GetCollection(mongodb_uri, db_name, collection_name)
    collection=client.get_collection()
    rag=RAG(collection=collection,llm_model=llm)
    query='đầm dự tiệc'
    #print(query)
    search_result=rag.hybrid_search(query=query)
    for item in search_result:
        print(item['name'])
    # prompt=rag.create_prompt(search_results=search_result,query=query)
    # rag.update_history(role='user',content=prompt)
    # respone=rag.answer_query()
    # print(respone)
    #print(rag.remove_message())
    #print(respone)
    # query = 'trong những sản phẩm trên, có sản phẩm nào giảm giá không'
    # #print(query)
    # rag.update_history(role='user',content=query)
    # respone=rag.answer_query()
    
    #print(respone)
    