"""
Conversational interface for recipe parsing and querying.
This is a stateless, rule-based interface that answers questions about recipes.
"""

import re
from html_parser import process_url
import google.generativeai as genai
import json

GEMINI_API_KEY = "AIzaSyBdbrADPwUJq2hB4AfVBAIQhtGLKTXeRnY"
GEMINI_MODEL = "gemini-2.5-flash-lite"

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


def process_user_query(recipe_data, conversation_history, query):
    """
    Process a user query and return appropriate response.
    
    Args:
        recipe_data: Dict with 'ingredients' and 'instructions' keys
        conversation_history: List of conversation exchanges
        query: User query string
    
    Returns:
        tuple: (should_continue: bool, assistant_response: str)
    """
    query_lower = query.lower().strip()
    
    # Check for exit
    if query_lower in ['quit', 'exit', 'q']:
        print("\nGoodbye!")
        return False, None
    
    # Send to Gemini for processing
    print("\nThinking...")
    response = query_gemini(recipe_data, conversation_history, query)
    print(f"\n{response}")
    
    return True, response


def main():
    """Main function to run the conversational interface."""
    print("Welcome to the Recipe Assistant!")
    print("=" * 50)
    
    # Ask for recipe URL
    url = input("\nPlease enter a recipe URL: ").strip()
    
    if not url:
        print("No URL provided. Exiting.")
        return
    
    # Parse the recipe with Gemini
    print("\nParsing recipe with AI...")
    try:
        recipe_data = process_url(url)
        print(f"Successfully parsed recipe with {len(recipe_data['ingredients'])} ingredients and {len(recipe_data['instructions'])} steps!")
    except Exception as e:
        print(f"Error parsing recipe: {e}")
        return
    
    # Initialize conversation history
    conversation_history = []
    
    # Enter conversation loop
    print("\n" + "=" * 50)
    print("You can now ask questions about the recipe.")
    print("Try: 'start' to begin walkthrough, 'next', 'back', 'repeat', or ask any question!")
    print("Type 'quit', 'exit', or 'q' to exit.")
    print("=" * 50)
    
    while True:
        query = input("\nYour question: ").strip()
        
        if not query:
            continue
        
        should_continue, assistant_response = process_user_query(recipe_data, conversation_history, query)
        
        if not should_continue:
            break
        
        # Add this exchange to conversation history
        if assistant_response:
            conversation_history.append({
                'user': query,
                'assistant': assistant_response
            })


if __name__ == "__main__":
    main()