"""
Flask backend API for recipe chat interface.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from html_parser import process_url
import google.generativeai as genai
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

GEMINI_API_KEY = "AIzaSyBdbrADPwUJq2hB4AfVBAIQhtGLKTXeRnY"
GEMINI_MODEL = "gemini-2.5-flash-lite"

# Global state to store parsed recipe data and conversation history
recipe_data = {
    'recipe': None,
    'url': None
}

# Store conversation histories per session (simplified - in production use sessions)
conversation_histories = {}

def query_gemini(recipe_data, conversation_history, query):
    """
    Send a user query to Gemini along with recipe context and full conversation history.
    
    Args:
        recipe_data: Dict with 'ingredients' and 'instructions' keys
        conversation_history: List of dicts with 'user' and 'assistant' messages
        query: User's current question
    
    Returns:
        str: Gemini's response
    """
    # Configure Gemini API
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    # Build conversation history string
    history_text = ""
    if conversation_history:
        history_text = "CONVERSATION HISTORY:\n"
        for i, exchange in enumerate(conversation_history, 1):
            history_text += f"\nUser: {exchange['user']}\n"
            history_text += f"Assistant: {exchange['assistant']}\n"
        history_text += "\n"
    
    # Create context-aware prompt
    prompt = f"""
You are a helpful cooking assistant with conversation memory. You can help users navigate through a recipe step-by-step.

FULL RECIPE DATA:
{json.dumps(recipe_data, indent=2)}

{history_text}

CURRENT USER QUESTION: {query}

INSTRUCTIONS:
- Track which step the user is currently on based on the conversation history
- If they say "start", "begin", or "start recipe", begin at step 1
- If they say "next" or "n", move to the next step
- If they say "back", "b", or "previous", go to the previous step
- If they say "repeat" or "again", repeat the current step
- If they ask "step X", jump to that step number
- When presenting a step, format it clearly: "Step X: [instruction text]"
- After showing a step, remind them they can say 'next', 'back', or ask questions
- If they ask contextual questions like "how much of that?", "what temperature?", "how long?", refer to the current step based on conversation history
- If asking about ingredients without context, provide exact quantities from the recipe
- If the answer isn't in the recipe, say so politely and provide general cooking advice if appropriate
- Keep track of where they are in the recipe across the entire conversation

Provide a helpful, concise answer to the current question.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"


@app.route('/api/parse', methods=['POST'])
def parse_recipe():
    """Parse a recipe URL and store the results."""
    global recipe_data
    
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        parsed_recipe = process_url(url)
        
        recipe_data['recipe'] = parsed_recipe
        recipe_data['url'] = url
        
        return jsonify({
            'success': True,
            'message': f'Successfully parsed recipe with {len(parsed_recipe["ingredients"])} ingredients and {len(parsed_recipe["instructions"])} steps!',
            'ingredients_count': len(parsed_recipe['ingredients']),
            'steps_count': len(parsed_recipe['instructions'])
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG: Error parsing recipe: {str(e)}")
        print(f"DEBUG: Traceback: {error_trace}")
        return jsonify({'error': f'Error parsing recipe: {str(e)}'}), 500


@app.route('/api/query', methods=['POST'])
def query_recipe():
    """Process a query about the recipe."""
    global recipe_data, conversation_histories
    
    if not recipe_data['recipe']:
        return jsonify({'error': 'No recipe loaded. Please parse a recipe first.'}), 400
    
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    query = data.get('query')
    session_id = data.get('session_id', 'default')  # Use session_id to track different users
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Get or create conversation history for this session
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    
    try:
        response = query_gemini(
            recipe_data['recipe'],
            conversation_histories[session_id],
            query
        )
        
        # Add to conversation history
        conversation_histories[session_id].append({
            'user': query,
            'assistant': response
        })
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500


@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history."""
    global conversation_histories
    
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    if session_id in conversation_histories:
        conversation_histories[session_id] = []
    
    return jsonify({
        'success': True,
        'message': 'Conversation history reset'
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status of the recipe."""
    global recipe_data
    
    if recipe_data['recipe']:
        return jsonify({
            'has_recipe': True,
            'url': recipe_data['url'],
            'ingredients_count': len(recipe_data['recipe']['ingredients']),
            'steps_count': len(recipe_data['recipe']['instructions'])
        })
    else:
        return jsonify({
            'has_recipe': False
        })


@app.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Server is running'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)