from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API Key is missing. Please set it in the .env file.")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('models/gemini-1.5-flash')  # Using model Gemini 1.5 Flash

app = Flask(__name__)

def query_generative_ai(question):
    try:
        response = model.generate_content(question)
        
        print(f"API Response: {response}")

        return {'text': response.text}
    except Exception as e:
        print(f"Error querying Generative AI API: {e}")
        return {'error': str(e)}

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('question', '')
    if not user_input:
        return jsonify({'error': 'Please provide a valid question.'}), 400

    genai_response = query_generative_ai(user_input)

    if 'error' in genai_response:
        return jsonify({'answer': f"Sorry, there was an error processing your request: {genai_response['error']}. Please try again later."})

    answer = genai_response.get('text', 'Sorry, I could not generate a response.')
    return jsonify({'answer': answer})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
