"""
Flask backend API for recipe chat interface.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from html_parser import process_url
from data_classes import Ingredient, Step
from recipe_state_machine import RecipeStateMachine
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global state to store parsed recipe data
recipe_data = {
    'ingredients': None,
    'steps': None,
    'fsm': None,
    'url': None
}


def format_ingredients(ingredients):
    """Format ingredients list as string."""
    if not ingredients:
        return "No ingredients found."
    
    lines = ["Here are the ingredients:"]
    for ingredient in ingredients:
        parts = []
        if ingredient.quantity:
            parts.append(ingredient.quantity)
        if ingredient.measurement_unit:
            parts.append(ingredient.measurement_unit)
        if ingredient.name:
            parts.append(ingredient.name)
        
        ingredient_str = " ".join(parts) if parts else ingredient.name
        lines.append(f"- {ingredient_str}")
    
    return "\n".join(lines)


def format_steps(steps):
    """Format steps list as string."""
    if not steps:
        return "No steps found."
    
    lines = ["Here are all the steps:"]
    for step in steps:
        lines.append(f"Step {step.step_number}: {step.description}")
    
    return "\n".join(lines)


def format_current_step(step):
    """Format current step as string."""
    return f"Step {step.step_number}: {step.description}"


def is_next_step_query(query):
    """See if user wants to jump 1 step ahead."""
    patterns = [
        r'next step',
        r'next',
        r'\bn\b',
        r'advance',
        r'continue',
        r'what\'s next',
        r'forward',
        r'move ahead',
        r'proceed',
        r'forward one step',
        r'go forward',
        r'resume',
    ]
    query = query.lower().strip()
    for pattern in patterns:
        if re.search(pattern, query):
            return True
    return False


def is_go_back_a_step_query(query):
    """See if user wants to go back a step."""
    patterns = [
        r'last step',
        r'go back a step',
        r'^b$',
        r'go back',
        r'go back one step',
        r'back',
        r'previous',
        r'previous step'
    ]
    query = query.lower().strip()
    for pattern in patterns:
        if re.search(pattern, query):
            return True
    return False


def is_begin_recipe_query(query):
    """See if user wants to start following the recipe step-by-step."""
    patterns = [
        r'\bstart recipe\b',
        r'start cooking',
        r'begin recipe',
        r'start the recipe',
        r'start',
        r'walkthrough',
        r'beginning',
    ]
    query = query.lower().strip()
    for pattern in patterns:
        if re.search(pattern, query):
            return True
    return False


def is_repeat_query(query):
    """Detect if the user wants the current step repeated."""
    patterns = [
        r'\brepeat\b',
        r'\brepeat that\b',
        r'\brepeat step\b',
        r'\bsay that again\b',
        r'\bwhat was that\b',
        r'\bagain\b$',
        r'again',
        r'repeat',
        r'say again',
        r'tell me again',
        r'what did you say',
    ]
    q = query.lower().strip()
    for p in patterns:
        if re.search(p, q):
            return True
    return False


def extract_ingredient_from_how_much(query):
    """Extract ingredient name from "how much X do i need?" queries."""
    pattern = r'how (?:much|many) (?!time\b)(.+?)(?:\s+(?:do (?:i|we)|is|are)\s+(?:need|needed))?[?.]?$'
    match = re.search(pattern, query)
    
    if match:
        ingredient = match.group(1).strip()
        ingredient = re.sub(r'\s+(?:do (?:i|we)|is|are)\s+(?:need|needed)', '', ingredient)
        ingredient = ingredient.rstrip('?.,!')
        return ingredient if ingredient else None
    
    return None


def find_ingredient_by_name(ingredients, search_name):
    """Find an ingredient by name using case-insensitive substring matching."""
    search_name = search_name.lower().strip()
    
    for ingredient in ingredients:
        ingredient_name_lower = ingredient.name.lower()
        if search_name in ingredient_name_lower or ingredient_name_lower in search_name:
            return ingredient
    
    return None


def handle_substitution_query(query):
    """Handle ingredient substitution questions."""
    q = query.lower().strip()
    
    patterns = [
        r'substitute for (.+)',
        r'what can i use instead of (.+)',
        r'what can i substitute for (.+)',
        r'what can i use instead of (.+)',
        r'what can i use as a substitute for (.+)',
        r'in place of (.+)',
        r'alternative to (.+)',
        r'replacement for (.+)',
        r'i dont have (.+)',
        r'i dont have any(.+)',
        r'i do not have (.+)',
        r'i do not have any (.+)',
        r'im out of (.+)',
        r'i am out of (.+)',
    ]
    
    for p in patterns:
        match = re.search(p, q)
        if match:
            ingredient = match.groups()[-1].strip(" ?.!")
            
            if not ingredient:
                return "Ingredient not found, sorry!"
            
            encoded = ingredient.replace(" ", "+")
            url = f"https://www.google.com/search?q={encoded}+cooking+substitute"
            
            return f"Here are some substitution options for '{ingredient}':\n{url}"
    
    return None


def handle_cooking_time_query(query, steps):
    """Handle cooking time questions."""
    q = query.lower().strip()
    
    actions = ["bake", "roast", "broil", "grill", "toast", "sear",
        "boil", "simmer", "poach", "steam", "blanch", "parboil", "cook",
        "fry", "deep-fry", "pan-fry", "saute", "sautee", "stir-fry",
        "braise", "stew", "microwave", "smoke", "char", "caramelize", "reduce"
    ]
    
    time_mentioned = ("how long" in q) or ("time" in q) or ("minutes" in q) or \
    ("hours" in q) or ("hour" in q) or ("minute" in q) or ("cook for" in q) or \
    ("bake for" in q) or ("done" in q) or ("ready" in q)
    
    if not time_mentioned:
        return None
    
    found_action = None
    for action in actions:
        if re.search(rf'\b{action}\b', q):
            found_action = action
            break
    
    something_found = False
    results = []
    
    if found_action:
        for step in steps:
            if found_action in step.description.lower():
                results.append(f"Step {step.step_number}: {step.description}")
                something_found = True
        
        if something_found:
            return "\n".join(results)
    
    # Otherwise, no specific action found, list anything with time mentioned
    for step in steps:
        if re.search(r'(\d+\s*(minutes|minute|hours|hour))', step.description.lower()) \
            or re.search(r'\b(how long|time|ready|done)\b', step.description.lower()):
            results.append(f"Step {step.step_number}: {step.description}")
            something_found = True
    
    if not something_found:
        return "Couldn't find any relevant cooking time information."
    
    return "\n".join(results)


def handle_cooking_temp_query(query, steps):
    """Handle cooking temperature questions."""
    q = query.lower().strip()
    
    temp_mentioned = ("temp" in q) or ("temperature" in q) or ("heat" in q) or \
    ("when is it done" in q) or ("degree" in q)
    temp_keywords = ["degree", "°", "preheat", "oven", "heat to"]
    
    if not temp_mentioned:
        return None
    
    found_temp_keyword = False
    results = []
    
    for step in steps:
        for keyword in temp_keywords:
            if keyword in step.description.lower():
                found_temp_keyword = True
                results.append(f"Step {step.step_number}: {step.description}")
                break
    
    if found_temp_keyword:
        return "\n".join(results)
    
    return "Couldn't find any relevant cooking temperature information."


def handle_how_much_question(ingredients, query, fsm):
    """Handle "how much <ingredient> do i need?" questions."""
    vague_pattern = (
        r'^(how (much|many))'
        r'(?:\s+of\s+(that|this|it|those|these))?'
        r'(?:\s+(do i need|is needed|are needed))?'
        r'\s*\??$'
    )
    
    if re.search(vague_pattern, query.strip()):
        step = fsm.get_current_step()
        if hasattr(step, "ingredients") and step.ingredients:
            responses = []
            for name in step.ingredients:
                ingredient = find_ingredient_by_name(ingredients, name)
                if ingredient:
                    parts = []
                    if ingredient.quantity:
                        parts.append(ingredient.quantity)
                    if ingredient.measurement_unit:
                        parts.append(ingredient.measurement_unit)
                    parts.append(f"of {ingredient.name}")
                    response = " ".join(parts)
                else:
                    response = f"some {name}"
                responses.append(f"You need {response}.")
            return "\n".join(responses)
        return "I couldn't find any ingredients in this recipe step."
    
    # Otherwise, non-vague
    ingredient_name = extract_ingredient_from_how_much(query)
    
    if not ingredient_name:
        return None
    
    ingredient = find_ingredient_by_name(ingredients, ingredient_name)
    
    if ingredient:
        parts = []
        if ingredient.quantity:
            parts.append(ingredient.quantity)
        if ingredient.measurement_unit:
            parts.append(ingredient.measurement_unit)
        if ingredient.name:
            parts.append(f"of {ingredient.name}")
        
        response = " ".join(parts) if parts else f"some {ingredient.name}"
        return f"You need {response}."
    else:
        return "I couldn't find that ingredient in this recipe."


def handle_what_is_question(query, fsm):
    """Handle "what is X?" questions by returning a Google search URL."""
    if re.search(r"what(?:'?s| is) that\??$", query):
        step = fsm.get_current_step()
        if hasattr(step, "ingredients") and step.ingredients:
            urls = []
            for ingredient in step.ingredients:
                name = str(ingredient)
                search_query = name.replace(" ", "+")
                url = f"https://www.google.com/search?q={search_query}"
                urls.append(f"I found a reference for you: {url}")
            return "\n".join(urls)
    
    pattern = r"what(?:'?s| is) (.+?)[?.]?$"
    match = re.search(pattern, query)
    
    if not match:
        return None
    
    search_term = match.group(1).strip()
    search_term = search_term.rstrip('?.,!')
    
    query_encoded = search_term.replace(" ", "+")
    url = f"https://www.google.com/search?q={query_encoded}"
    
    return f"I found a reference for you: {url}"


def handle_how_do_i_question(query, fsm):
    """Handle "how do I X?" questions by returning a YouTube search URL."""
    if re.search(r'^(how\??|how do i do (that|this|it)\??)$', query.strip()):
        step = fsm.get_current_step()
        if hasattr(step, "methods") and step.methods:
            urls = []
            for method in step.methods:
                search_query = f"how to {method}".replace(" ", "+")
                url = f"https://www.youtube.com/results?search_query={search_query}"
                urls.append(f"Here's a video search that might help: {url}")
            return "\n".join(urls)
        return "I couldn't find any methods in this recipe step."
    
    pattern = r'how do (?:i|you) (.+?)[?.]?$'
    match = re.search(pattern, query)
    
    if not match:
        return None
    
    action = match.group(1).strip()
    action = action.rstrip('?.,!')
    
    search_query = f"how to {action}".replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={search_query}"
    
    return f"Here's a video search that might help: {url}"


def extract_step_number(query):
    """Extract step number from queries like "show step 3" or "step 2"."""
    pattern = r'step\s+(\d+)'
    match = re.search(pattern, query)
    
    if match:
        return int(match.group(1))
    
    return None


def is_ingredients_query(query):
    """Check if query is asking to show ingredients."""
    patterns = [
        r'show\s+ingredients',
        r'list\s+ingredients',
        r'show\s+me\s+the\s+ingredients',
        r'ingredients',
    ]
    
    for pattern in patterns:
        if re.search(pattern, query):
            return True
    
    return False


def is_recipe_query(query):
    """Check if query is asking to show the full recipe."""
    patterns = [
        r'show\s+recipe',
        r'show\s+all\s+steps',
        r'display\s+the\s+recipe',
        r'full\s+recipe',
        r'show\s+me\s+the\s+recipe',
        r'display\s+all\s+steps',
        r'display\s+recipe',
        r'display\s+the\s+recipe',
        r'whole recipe',
        r'entire recipe',
        r'complete recipe',
    ]
    
    for pattern in patterns:
        if re.search(pattern, query):
            return True
    
    return False


def process_user_query(ingredients, steps, fsm, query):
    """Process a user query and return response string."""
    query_lower = query.lower().strip()
    
    # Check for ingredients list
    if is_ingredients_query(query_lower):
        return format_ingredients(ingredients)
    
    # Check for full recipe
    if is_recipe_query(query_lower):
        return format_steps(steps)
    
    if is_begin_recipe_query(query_lower):
        fsm.jump_to_step(1)
        step = fsm.get_current_step()
        return f"{format_current_step(step)}\n\nType 'next' or 'n' for the next step, or ask a question."
    
    if is_next_step_query(query_lower):
        fsm.move_steps_forward(1)
        step = fsm.get_current_step()
        return f"{format_current_step(step)}\n\nType 'next' or 'n' for the next step, or ask a question."
    
    if is_go_back_a_step_query(query_lower):
        fsm.move_steps_forward(-1)
        step = fsm.get_current_step()
        return f"{format_current_step(step)}\n\nType 'next' or 'n' for the next step, or ask a question."
    
    # Check for specific step number
    step_num = extract_step_number(query_lower)
    if step_num:
        fsm.jump_to_step(step_num)
        step = fsm.get_current_step()
        return format_current_step(step)
    
    if is_repeat_query(query_lower):
        step = fsm.get_current_step()
        return format_current_step(step)
    
    # Check for "how much" questions
    if query_lower.startswith("how much") or query_lower.startswith("how many"):
        result = handle_how_much_question(ingredients, query_lower, fsm)
        if result:
            return result
    
    # Check for "what is" questions
    if query_lower.startswith("what is") or query_lower.startswith("what's") or query_lower.startswith("whats"):
        result = handle_what_is_question(query_lower, fsm)
        if result:
            return result
    
    # Check for "how" questions (that are not "how much")
    if query_lower.startswith("how"):
        result = handle_how_do_i_question(query_lower, fsm)
        if result:
            return result
    
    # Check cooking temperature
    result = handle_cooking_temp_query(query, steps)
    if result:
        return result
    
    # Check cooking time
    result = handle_cooking_time_query(query, steps)
    if result:
        return result
    
    # Check substitution
    result = handle_substitution_query(query_lower)
    if result:
        return result
    
    # Fallback: help message
    return ("Sorry, I didn't understand that.\n\n"
            "I can:\n"
            "- show ingredients\n"
            "- show the full recipe\n"
            "- start recipe walkthrough (start)\n"
            "- show step <number>\n"
            "- answer \"how much <ingredient> do I need?\"\n"
            "- answer \"what is X?\" and \"how do I X?\" with helpful links.")


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
        ingredients, steps = process_url(url)
        fsm = RecipeStateMachine(steps)
        
        recipe_data['ingredients'] = ingredients
        recipe_data['steps'] = steps
        recipe_data['fsm'] = fsm
        recipe_data['url'] = url
        
        return jsonify({
            'success': True,
            'message': f'Successfully parsed recipe with {len(ingredients)} ingredients and {len(steps)} steps!',
            'ingredients_count': len(ingredients),
            'steps_count': len(steps)
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
    global recipe_data
    
    if not recipe_data['ingredients'] or not recipe_data['steps'] or not recipe_data['fsm']:
        return jsonify({'error': 'No recipe loaded. Please parse a recipe first.'}), 400
    
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        response = process_user_query(
            recipe_data['ingredients'],
            recipe_data['steps'],
            recipe_data['fsm'],
            query
        )
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status of the recipe."""
    global recipe_data
    
    if recipe_data['ingredients'] and recipe_data['steps']:
        return jsonify({
            'has_recipe': True,
            'url': recipe_data['url'],
            'ingredients_count': len(recipe_data['ingredients']),
            'steps_count': len(recipe_data['steps'])
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

