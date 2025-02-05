from getClient.core import RAG
import dotenv
# MongoDB connection details

db_name = "product"
db_collection = "sendo"

# Language model and embedding details
llm_name = "llama-3.1-8b-instant"
embedding_name = "dangvantuan/vietnamese-embedding"
# Initialize history
# Load environment variables from .env file
env = dotenv.dotenv_values(".env")
mongodb_uri= env.get("MONGODB_URI")
api_key = env.get("GROQ_KEY")

history = [
    {
        "role": "system",
        "content": (
            "Bạn tên Lan, là một người tư vấn sản phẩm cho sàn thương mại điện tử AnhLong. "
            "Dựa vào thông tin được cung cấp từ hệ thống và câu hỏi của khách hàng, bạn sẽ đưa ra câu trả lời tốt nhất, ngắn gọn nhất. "
            "Hãy nhớ rằng bạn cần thể hiện sự chuyên nghiệp và tận tâm. "
            "Chỉ đưa ra 5 sản phẩm đầu tiên thôi. Nếu khách cần thêm, hãy đưa ra những cái còn lại"
            "đừng lặp lại sản phẩm đã tư vấn "
            f"Xưng hô là 'em' và khách là anh."
        )
    }
]
# Initialize the RAG class
rag_system = RAG(
    mongodbUri=mongodb_uri,
    dbName=db_name,
    dbCollection=db_collection,
    llm_name=llm_name,
    embeddingName=embedding_name,
    api_key=api_key,
    history=history
)

# Example user query
user_query = "Tôi cần tìm quà tặng sinh nhật cho bé gái 5 tuổi."
print(f"User: {user_query}")

# Step 1: Perform vector search
search_results = rag_system.vector_search(user_query)
for result in search_results:
    print(result['name'])
# Step 2: Create a prompt from search results
prompt = rag_system.create_prompt(search_results)
#Step 3: Update the history with the user's query
rag_system.update_history("system", prompt)

# Step 4: Update the history with assistant's product information
rag_system.update_history("user", user_query)

# Step 5: Generate a response
response = rag_system.generate_content()
print(f"Assistant: {response}")

# Step 6: Handle a follow-up question from the user
follow_up_query = "Bạn còn gợi ý nào khác không?"
print(f"User: {follow_up_query}")

# Update history with the follow-up query
rag_system.update_history("user", follow_up_query)

# Generate a new response
new_response = rag_system.generate_content()
print(f"Assistant: {new_response}")