import re
from html_parser import process_url
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"

def create_chat_session(recipe_data):
    """
    Create a new Gemini chat session with recipe context.
    
    Args:
        recipe_data: Dict with 'ingredients' and 'instructions' keys
    
    Returns:
        chat session object
    """
    # Configure Gemini API
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
# Create initial system-like message with recipe context
    initial_prompt = f"""
You are a helpful cooking assistant with conversation memory. You can help users navigate through a recipe step-by-step.

FULL RECIPE DATA:
{json.dumps(recipe_data, indent=2)}

INSTRUCTIONS FOR YOU:
CRITICAL FIRST STEP: Before anything else, you MUST atomize the instructions. Break down each instruction into smaller, atomic steps. Each atomic step should be a single action. For example:
- "Preheat oven to 350°F, then mix flour and eggs" → becomes Step 1: "Preheat oven to 350°F" and Step 2: "Mix flour and eggs"
- Look for conjunctions like "then", "and then", "while", etc. and split on those
- Each step should be one clear action

After atomizing, you will use ONLY these atomized steps for the entire conversation. Renumber them starting from 1.

Then follow these rules:
- Track which step the user is currently on based on our conversation
- If they say "start", "begin", or "start recipe", begin at step 1 of the ATOMIZED steps
- If they say "next" or "n", move to the next atomized step
- If they say "back", "b", or "previous", go to the previous atomized step
- If they say "repeat" or "again", repeat the current atomized step
- If they ask "step X", jump to that step number in the atomized steps
- When presenting a step, format it clearly: "Step X: [instruction text]"
- After showing a step, remind them they can say 'next', 'back', or ask questions
- If they ask contextual questions like "how much of that?", "what temperature?", "how long?", refer to the current step based on our conversation
- If asking about ingredients without context, provide exact quantities from the recipe
- If the answer isn't in the recipe, say so politely and provide general cooking advice if appropriate
- Keep track of where they are in the recipe throughout our conversation

You should maintain context and remember which step the user is on as we talk.

First, atomize the steps internally, then respond with: "Ready! I've loaded and processed the recipe into [NUMBER] steps. You can ask me questions, or say 'start' to begin the step-by-step walkthrough."
"""
    
    # Start chat session
    chat = model.start_chat(history=[])
    
    # Send initial context
    response = chat.send_message(initial_prompt)
    
    return chat


def query_gemini_chat(chat, query):
    """
    Send a user query through the chat session.
    
    Args:
        chat: Active chat session
        query: User's current question
    
    Returns:
        str: Gemini's response
    """
    try:
        response = chat.send_message(query)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"


def process_user_query(chat, query):
    """
    Process a user query and return appropriate response.
    
    Args:
        chat: Active chat session
        query: User query string
    
    Returns:
        bool: True if should continue, False if should exit
    """
    query_lower = query.lower().strip()
    
    # Check for exit
    if query_lower in ['quit', 'exit', 'q']:
        print("\nGoodbye!")
        return False
    
    # Send to Gemini chat
    print("\nThinking...")
    response = query_gemini_chat(chat, query)
    print(f"\n{response}")
    
    return True


def main():
    """Main function to run the conversational interface."""
    print("Welcome to the Recipe Assistant!")
    print("=" * 50)
    
    # Ask for recipe URL
    url = input("\nPlease enter a recipe URL: ").strip()
    
    if not url:
        print("No URL provided. Exiting.")
        return
    
    # Parse the recipe
    print("\nParsing recipe...")
    try:
        recipe_data = process_url(url)
        print(f"Successfully parsed recipe with {len(recipe_data['ingredients'])} ingredients and {len(recipe_data['instructions'])} steps!")
    except Exception as e:
        print(f"Error parsing recipe: {e}")
        return
    
    # Create chat session with recipe context
    print("\nInitializing AI assistant...")
    chat = create_chat_session(recipe_data)
    
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
        
        should_continue = process_user_query(chat, query)
        
        if not should_continue:
            break


if __name__ == "__main__":
    main()