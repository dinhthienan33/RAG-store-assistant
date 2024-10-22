from embeddings import SentenceTransformerEmbedding, EmbeddingConfig
from rag.core import RAG  # Assuming the RAG class is in a file named core.py
import google.generativeai as genai
from semantic_router import SemanticRouter, Route
from reflection import Reflection
from semantic_router.samples import jobSample, chitchatSample


llm = genai.GenerativeModel("gemini-1.5-flash")
reflection = Reflection(llm=llm)
# Initialize the RAG class
rag = RAG(
    mongodbUri="mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs",
    dbName="test_db",
    dbCollection="test_cl",
    llm_name='gemini-1.5-flash',
    embeddingName='thenlper/gte-large'
)
JOB_ROUTE_NAME = 'jobs'
CHITCHAT_ROUTE_NAME = 'chitchat'

productRoute = Route(name=JOB_ROUTE_NAME, samples=jobSample)
chitchatRoute = Route(name=CHITCHAT_ROUTE_NAME, samples=chitchatSample)
semanticRouter = SemanticRouter(llm, routes=[productRoute, chitchatRoute])
# Initialize the Gemini model with your API key
api_key = "AIzaSyD7JnSPUV2_ERRN_y2MV-vA_QbJiKpwbRU"
genai.configure(api_key=api_key)
query='What are the key requirements for a The IT Data Engineer?'
guidedRoute = semanticRouter.guide(query)[1]

if guidedRoute == JOB_ROUTE_NAME:
    # Decide to get new info or use previous info
    # Guide to RAG system
    print("Guide to RAGs")

    reflected_query = reflection(#chathistory)

    # print('====query', query)
    # print('reflected_query', reflected_query)

    query = reflected_query
    #source_information = rag.enhance_prompt(query).replace('<br>', '\n')
    #combined_information = f"Hãy trở thành chuyên gia tư vấn bán hàng cho một cửa hàng điện thoại. Câu hỏi của khách hàng: {query}\nTrả lời câu hỏi dựa vào các thông tin sản phẩm dưới đây: {source_information}."
    data.append({
        "role": "user",
        "parts": [
            {
                "text": combined_information,
            }
        ]
    })
    response = rag.generate_content(data)
else:
    # Guide to LLMs
    print("Guide to LLMs")
    response = llm.generate_content(data)


# Define a function to create a prompt pattern for QA about job requirements


# Example usage
user_query = "What are the key requirements for a The IT Data Engineer?"
search_results = rag.vector_search(user_query)

# # Create the prompt using the search results
# prompt = create_prompt(user_query, search_results)
#prompt='hello'
# # Generate content using the Gemini model
response = rag.generate_content(user_query, search_results)

# # Extract the generated content
# # Display the generated content
# print("Generated Answer:")
print(response)
#print(search_results)