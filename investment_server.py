from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

app = Flask(__name__)

# Load environment variables
load_dotenv()

def load_prompt_template():
    """Load the investment projection prompt template"""
    with open('investment_projection_prompt_monthly.txt', 'r', encoding='utf-8') as f:
        return f.read()

# Cache prompt template and OpenAI client at startup
PROMPT_TEMPLATE = load_prompt_template()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
CLIENT = OpenAI(api_key=api_key)

def generate_investment_projection(monthly_contribution_amount, risk_tolerance, interests):
    """Generate investment projection using OpenAI API"""
    # Replace variables in cached prompt template
    prompt = PROMPT_TEMPLATE.replace("{monthly_contribution_amount}", str(monthly_contribution_amount))
    prompt = prompt.replace("{risk_tolerance}", risk_tolerance)
    prompt = prompt.replace("{interests}", interests)
    
    # Make API call with streaming
    stream = CLIENT.chat.completions.create(
        model="gpt-4o-mini",  # Using faster model
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,  # More deterministic and faster
        stream=True  # Enable streaming
    )
    
    # Accumulate streamed response
    response_text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content
    
    # Parse JSON response
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If response is not valid JSON, return error
        raise ValueError(f"Invalid JSON response from OpenAI: {response_text}")

@app.route('/api/investment-projection', methods=['POST'])
def investment_projection():
    """API endpoint to generate investment projection"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract and validate parameters
        monthly_contribution_amount = data.get('monthly_contribution_amount')
        risk_tolerance = data.get('risk_tolerance')
        interests = data.get('interests')
        
        # Validate required parameters
        if monthly_contribution_amount is None:
            return jsonify({"error": "monthly_contribution_amount is required"}), 400
        if risk_tolerance is None:
            return jsonify({"error": "risk_tolerance is required"}), 400
        if interests is None:
            return jsonify({"error": "interests is required"}), 400
        
        # Validate parameter types and values
        try:
            monthly_contribution_amount = float(monthly_contribution_amount)
            if monthly_contribution_amount <= 0:
                return jsonify({"error": "monthly_contribution_amount must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "monthly_contribution_amount must be a valid number"}), 400
        
        if risk_tolerance not in ["High", "Average", "Minimal"]:
            return jsonify({"error": "risk_tolerance must be one of: High, Average, Minimal"}), 400
        
        if not isinstance(interests, str) or not interests.strip():
            return jsonify({"error": "interests must be a non-empty string"}), 400
        
        # Generate investment projection
        projection = generate_investment_projection(
            monthly_contribution_amount, 
            risk_tolerance, 
            interests
        )
        
        return jsonify(projection)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "investment-projection-api"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)