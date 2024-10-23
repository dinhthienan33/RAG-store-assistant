import pymongo
import google.generativeai as genai  # gemini
from IPython.display import Markdown
import textwrap
from embeddings import SentenceTransformerEmbedding, EmbeddingConfig

class RAG:
    def __init__(self, 
                 mongodbUri: str,
                 dbName: str,
                 dbCollection: str,
                 llm_name=None,
                 embeddingName: str = 'thenlper/gte-large',
                 api_key: str = None):
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
        self.mongo_uri = mongodbUri
        self.dbName = dbName
        self.collection_name = dbCollection
        self.client = None
        self.db = None
        self.collection = None
        self.embedding_model = SentenceTransformerEmbedding(
            EmbeddingConfig(name=embeddingName)
        )
        self.api_key = api_key
        self.llm = genai.GenerativeModel(llm_name)
        self.get_mongo_client()

    def get_mongo_client(self):
        """
        Establish a connection to the MongoDB database.
        """
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            print("Connection to MongoDB successful")
            self.db = self.client[self.dbName]
            self.collection = self.db[self.collection_name]
            print("Done !!")
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
            return None

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

        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def vector_search(self, user_query: str, limit=4):
        """
        Perform a vector search in the MongoDB collection based on the user query.

        Args:
        user_query (str): The user's query string.
        limit (int, optional): The number of top matches to return. Default is 4.

        Returns:
        list: A list of matching documents.
        """
        # Generate embedding for the user query
        query_embedding = self.get_embedding(user_query)

        if query_embedding is None:
            return "Invalid query or embedding generation failed."

        # Define the vector search pipeline
        vector_search_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 400,  # Number of candidate matches to consider
                "limit": limit  # Return top 'limit' matches
            }
        }

        unset_stage = {
            "$unset": "embedding"  # Exclude the 'embedding' field from the results
        }

        project_stage = {
            "$project": {
                "job_requirements": 1,  # Include the job_requirements field
                "job_description": 1,  # Include the job_description field
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }

        pipeline = [vector_search_stage, unset_stage, project_stage]

        # Execute the search
        results = self.collection.aggregate(pipeline)
        return list(results)

    @staticmethod
    def create_prompt(user_query, search_results):
        """
        Create a prompt for the language model based on the user query and search results.

        Args:
        user_query (str): The user's query string.
        search_results (list): The search results from the vector search.

        Returns:
        str: The generated prompt.
        """
        # Combine search results into a single string
        requirements = "\n".join([f"- {result['job_requirements']}" for result in search_results])
        descriptions = "\n".join([f"- {result['job_description']}" for result in search_results])
        # Create the prompt
        prompt = f"""
        You are an expert in job requirements and qualifications. Based on the following requirements, answer the user's question BUT WRITE SHORTER THAT YOU CAN:

        Question: {user_query}
        
        Job Requirements:
        {requirements}
        Job descriptions:
        {descriptions}

        Answer:
        """
        return prompt

    def generate_content(self, user_query, search_results):
        """
        Generate content using the language model based on the user query and search results.

        Args:
        user_query (str): The user's query string.
        search_results (list): The search results from the vector search.

        Returns:
        str: The generated content.
        """
        prompt = self.create_prompt(user_query, search_results)
        if self.llm:
            return self.llm.generate_content(prompt).text
        else:
            return "LLM is not initialized."

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