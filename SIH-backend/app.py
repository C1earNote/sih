from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd  # For loading and querying the CSV dataset

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API Key is missing. Please set it in the .env file.")

genai.configure(api_key=API_KEY)

# Load the CSV data
df = pd.read_csv('c:/Users/KIIT/Documents/GitHub/sih/SIH-backend/COLLEGES.csv')

# Filter Rajasthan-specific data
df_rajasthan = df[df['State'].str.lower() == 'rajasthan']

model = genai.GenerativeModel('models/gemini-1.5-flash')  # Using model Gemini 1.5 Flash

app = Flask(__name__)

def query_colleges_in_rajasthan(question):
    """
    Query the dataset to find relevant college info based on the user's question.
    """
    # Convert the question to lowercase for easier matching
    question = question.lower()

    # Check for college names or keywords in the question
    for _, row in df_rajasthan.iterrows():
        if row['College Name'].lower() in question or row['City'].lower() in question:
            # Prepare a response using college data
            response = {
                'College Name': row['College Name'],
                'Genders Accepted': row['Genders Accepted'],
                'Campus Size': row['Campus Size'],
                'Total Student Enrollments': row['Total Student Enrollments'],
                'Total Faculty': row['Total Faculty'],
                'Established Year': row['Established Year'],
                'Rating': row['Rating'],
                'University': row['University'],
                'Courses': row['Courses'],
                'Facilities': row['Facilities'],
                'City': row['City'],
                'Average Fees': row['Average Fees'],
            }
            return response

    return None  # No match found in the dataset

def query_generative_ai(question):
    """
    First, check if the question is related to Rajasthan colleges.
    If not, use the Generative AI model.
    """
    # Check if the question is about colleges in Rajasthan
    college_info = query_colleges_in_rajasthan(question)

    if college_info:
        return {'text': f"Here is some information about {college_info['College Name']} in {college_info['City']}, Rajasthan:\n"
                        f"Genders Accepted: {college_info['Genders Accepted']}\n"
                        f"Campus Size: {college_info['Campus Size']}\n"
                        f"Total Student Enrollments: {college_info['Total Student Enrollments']}\n"
                        f"Total Faculty: {college_info['Total Faculty']}\n"
                        f"Established Year: {college_info['Established Year']}\n"
                        f"Rating: {college_info['Rating']}\n"
                        f"University: {college_info['University']}\n"
                        f"Courses: {college_info['Courses']}\n"
                        f"Facilities: {college_info['Facilities']}\n"
                        f"Average Fees: {college_info['Average Fees']}\n"}

    # If no relevant data is found in the dataset, fall back to Generative AI model
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
