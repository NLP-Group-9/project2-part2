# Recipe Chat - Voice-Enabled Recipe Assistant

A web-based recipe parsing and querying system that uses NLP to extract and answer questions about recipes from popular cooking websites.

**Python version:** 3.11.9  
**GitHub:** https://github.com/NLP-Group-9/project2

## Features

- 🍳 Parse recipes from AllRecipes and Serious Eats
- 🎤 Voice-enabled query interface (speech-to-text)
- 💬 Natural language recipe queries
- 📝 Step-by-step recipe walkthrough
- 🔍 Ingredient substitution suggestions
- 📚 Cooking method and definition lookups

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Open in Browser

Navigate to:
```
http://localhost:5000
```

## Usage

### Step 1: Parse a Recipe

1. Enter a recipe URL from:
   - **allrecipes.com** (e.g., `https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/`)
   - **seriouseats.com** (e.g., `https://www.seriouseats.com/pecan-pie-cheesecake-recipe-11843450`)
2. Click **"Parse Recipe"**
3. Wait for the confirmation message

### Step 2: Ask Questions

You can ask questions in two ways:

#### Voice Input (Recommended)
- Click the **🎤 Voice** button
- Speak your question clearly
- The system automatically converts speech to text and sends the query

#### Text Input
- Type your question in the text field
- Press **Enter** or click **"Ask"**
- You can also use voice input and edit the text before sending

## Example Questions

### Viewing Recipe Information
- `show ingredients` - List all ingredients
- `show recipe` - Display all steps
- `show step 3` - Show a specific step

### Recipe Walkthrough
- `start recipe` - Begin step-by-step walkthrough
- `next` or `n` - Go to next step
- `back` or `b` - Go back one step
- `repeat` - Repeat current step

### Ingredient Questions
- `how much salt do I need?`
- `how many eggs do I need?`
- `how much of that?` (when in walkthrough mode)

### Cooking Questions
- `what temperature?`
- `how long to bake?`
- `how long does it take?`

### Substitutions
- `what can I substitute for butter?`
- `I don't have eggs`
- `I'm out of milk`

### Definitions & How-To
- `what is zesting?` - Get a Google search link
- `how do I julienne?` - Get a YouTube video search link
- `what is that?` - Look up ingredients from current step

## Browser Compatibility

**Speech Recognition:**
- ✅ Chrome (recommended)
- ✅ Edge
- ✅ Safari (limited support)
- ❌ Firefox (not supported - text input still works)

## Troubleshooting

**"Error connecting to server":**
- Make sure the Flask server is running (`python app.py`)
- Check that you're accessing `http://localhost:5000`
- The page will show a connection status message when it loads

**"No recipe loaded" error:**
- Make sure you've parsed a recipe URL first
- Check that the URL is from a supported website

**Speech recognition not working:**
- Use Chrome or Edge browser
- Allow microphone permissions when prompted
- Check your browser's microphone settings

**Recipe parsing returns 0 ingredients/steps:**
- Make sure the URL is from allrecipes.com or seriouseats.com
- Check that the URL is complete and accessible
- Some recipes may have different HTML structures

## Technical Details

### Parsing Logic

1. **Ingredient and Instruction Extraction**
   - Uses BeautifulSoup to parse HTML
   - Identifies structured data tags for ingredients and instructions
   - Extracts quantity, unit, and name for each ingredient

2. **Ingredient Parsing**
   - Leverages website's structured HTML data
   - Cleans ingredient names (removes descriptors, prep instructions)
   - Handles compound ingredients (e.g., "salt and pepper")

3. **Instruction Atomization**
   - Splits instructions by conjunctions and punctuation
   - Uses spaCy NLP to identify sentence boundaries
   - Breaks complex steps into atomic actions

4. **Instruction Parsing**
   - Identifies ingredients mentioned in each step
   - Extracts cooking tools from hardcoded list
   - Detects cooking methods using spaCy verb tagging
   - Extracts time durations and temperatures using regex patterns


This project is part of CS337 coursework.
