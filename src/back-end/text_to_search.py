from pyvi.ViTokenizer import tokenize
from pymongo import MongoClient
from groq import Groq
import json
import re
class SearchAgent():
    def generate_query(self,query):
        """
        Generate a MongoDB query string based on the user query.

        Args:
        query (str): The user query.

        Returns:
        str: The MongoDB query string in the required format.
        """
        # Prepare the MongoDB query prompt
        prompt = f"""
            Hãy chuyển query của người dùng sau thành một câu lệnh MongoDB hợp lệ, chỉ đưa ra câu trả lời và KHÔNG TRẢ LỜI GÌ THÊM, giữ nguyên format của json, trả về đúng format nhé, KHÔNG LẶP LẠI QUERY. Chỉ dùng match với giá tiền. Không được dùng field không được cung cấp. Tôi sẽ cung cấp cho bạn các thuộc tính của dữ liệu và collection name:
            Example:
                "User Query: 'hãy tìm 10 chiếc đầm đẹp giá dưới 100000'
                Collection Name: "product"
                "properties": ['_id', 'id', 'name', 'price', 'price_max', 'weight', 'quantity', 'shop_free_shipping', 'stock_status', 'order_count', 'special_price', 'final_price', 'final_price_max', 'promotion_percent', 'required_options', 'attribute', 'description', 'rating_info', 'shop_info', 'return_policy', 'length_product', 'height_product', 'has_voucher', 'width_product'],
                "Answer":
                        [
                            {{
                                '$search': {{
                                    'index': 'default', 
                                    'text': {{
                                        'query': 'chiếc đầm đẹp',  # Sử dụng chuỗi đã tokenize
                                        'path': ['name','description'],  # Thay 'description' bằng field chứa mô tả sản phẩm
                                    }}
                                }}
                            }},
                            {{
                                '$match': {{
                                    'price': {{'$lt': 100000}}  # Điều kiện giá dưới 100,000
                                }}
                            }},
                            {{
                                '$project': {{
                                    '_id': 0,
                                    'embedding': 0            
                                }}
                            }},
                            {{
                                '$limit': 10  # Giới hạn số lượng kết quả
                            }}
                        ]
            
            User Query: "{query}"
            Collection Name: "product"
            "properties": ['_id', 'id', 'name', 'price', 'price_max', 'weight', 'quantity', 'shop_free_shipping', 'stock_status', 'order_count', 'special_price', 'final_price', 'final_price_max', 'promotion_percent', 'required_options', 'attribute', 'description', 'rating_info', 'shop_info', 'return_policy', 'length_product', 'height_product', 'has_voucher', 'width_product'],
            Answer:
                """
        # Call the chat completion model to process the query
        
        # Get the response from the model
        chat_completion = llm.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        response=chat_completion.choices[0].message.content
        
        return response

    def fix_json(self,json_like_string):
        # Step 1: Replace single quotes with double quotes
        json_str = json_like_string.replace("'", '"')
        
        # Step 2: Remove comments (lines starting with #)
        json_str = re.sub(r'#.*', '', json_str)
        
        # Step 3: Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Step 4: Validate and parse JSON
        try:
            pipeline=json.loads(json_str)
            return pipeline
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            return None
    def full_text_search(self,query):
        search_result=self.generate_query(query)
        json_like_string = f"""
            [{search_result}]
            """
        pipeline=self.fix_json(json_like_string)
        results =collection.aggregate(pipeline)
        return results
if __name__ == '__test__':
    # Load environment variables from .env file
    env = dotenv.dotenv_values(".env")
    mongodb_uri= env.get("MONGODB_URI")
    api_key = env.get("GEMINI_KEY")
    llm= Groq(api_key=api_key)
    db_name = "product"
    collection_name = "sendo"
    client=MongoClient(mongodb_uri)
    collection= client[db_name][collection_name]
    searchAgent=SearchAgent()
    query= "đầm dự tiệc dưới 100000"
    responses=searchAgent.full_text_search(query)
    for response in responses:
        print (response)
