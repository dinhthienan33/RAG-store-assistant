# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.rag import get_response
from text_to_search import search_text

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    response = get_response(message)
    return jsonify({'response': response})

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    results = search_text(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)