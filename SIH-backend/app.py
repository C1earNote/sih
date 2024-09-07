from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
API_KEY = os.getenv('API_KEY')

# Check if the API key is loaded properly
if not API_KEY:
    raise ValueError("API Key is missing. Please set it in the .env file.")

# Configure the generative AI client with the API key
genai.configure(api_key=API_KEY)

app = Flask(__name__)

# Function to communicate with the Google Generative AI API
def query_generative_ai(question):
    try:
        response = genai.chat(prompt=question, max_tokens=100)  # Adjust max_tokens as needed
        print(f"API Response: {response}")  # Print response for debugging
        return response
    except Exception as e:
        print(f"Error querying Generative AI API: {e}")
        return {'error': str(e)}

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('question', '')
    if not user_input:
        return jsonify({'error': 'Please provide a valid question.'}), 400

    # Query the Generative AI API
    genai_response = query_generative_ai(user_input)

    # Check for errors in the response
    if 'error' in genai_response:
        return jsonify({'answer': f"Sorry, there was an error processing your request: {genai_response['error']}. Please try again later."})

    # Extract and return the response
    answer = genai_response.get('candidates', [{}])[0].get('content', 'Sorry, I could not generate a response.')
    return jsonify({'answer': answer})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
