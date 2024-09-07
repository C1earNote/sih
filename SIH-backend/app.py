from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import os

# Load environment variables
load_dotenv()

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API Key is missing. Please set it in the .env file.")

# Configure Google Generative AI API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Load the CSV file
csv_file_path = 'COLLEGES.csv'
colleges_df = pd.read_csv(csv_file_path)

# Initialize Flask app
app = Flask(__name__)

# Function to query the Google Generative AI API
def query_generative_ai(question):
    try:
        response = model.generate_content(question)
        print(f"API Response: {response}")
        return {'text': response.text}
    except Exception as e:
        print(f"Error querying Generative AI API: {e}")
        return {'error': str(e)}

# Function to search colleges by name or filter by different parameters
def search_colleges(question):
    # Try matching the college name
    if 'college' in question.lower():
        college_name = question.split('college')[-1].strip()
        filtered_colleges = colleges_df[colleges_df['College Name'].str.contains(college_name, case=False, na=False)]
        if not filtered_colleges.empty:
            return filtered_colleges.to_dict(orient='records')
    
    # Check for filtering by other criteria such as city, state, rank
    if 'city' in question.lower():
        city_name = question.split('city')[-1].strip()
        filtered_colleges = colleges_df[colleges_df['City'].str.contains(city_name, case=False, na=False)]
        if not filtered_colleges.empty:
            return filtered_colleges.to_dict(orient='records')

    if 'state' in question.lower():
        state_name = question.split('state')[-1].strip()
        filtered_colleges = colleges_df[colleges_df['State'].str.contains(state_name, case=False, na=False)]
        if not filtered_colleges.empty:
            return filtered_colleges.to_dict(orient='records')

    if 'rank' in question.lower():
        rank_number = ''.join(filter(str.isdigit, question))
        if rank_number:
            filtered_colleges = colleges_df[colleges_df['Rank'] == int(rank_number)]
            if not filtered_colleges.empty:
                return filtered_colleges.to_dict(orient='records')

    return None

# Route for handling chat queries
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('question', '')
    if not user_input:
        return jsonify({'error': 'Please provide a valid question.'}), 400

    # First check if the query relates to the CSV data
    college_response = search_colleges(user_input)
    if college_response:
        return jsonify({'answer': college_response})

    # If the query doesn't relate to the college data, use Generative AI
    genai_response = query_generative_ai(user_input)
    if 'error' in genai_response:
        return jsonify({'answer': f"Sorry, there was an error processing your request: {genai_response['error']}. Please try again later."})

    answer = genai_response.get('text', 'Sorry, I could not generate a response.')
    return jsonify({'answer': answer})

# Home route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
