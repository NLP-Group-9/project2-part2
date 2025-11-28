# Recipe Chat - Voice-Enabled Recipe Assistant

A web-based recipe parsing and querying system that uses NLP to extract and answer questions about recipes from popular cooking websites.

**Python version:** 3.11.9  
**GitHub:** https://github.com/NLP-Group-9/project2
**Gemini model:** gemini-2.5-flash-lite

## Quick Start

### Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run the Application For GUI (Voice + Text)

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

### Run the Application For text based interaction

```bash
python recipe_chat.py
```

## Usage

1. **Parse a Recipe:** Enter a recipe URL from allrecipes.com or seriouseats.com and click "Parse Recipe"
2. **Ask Questions:** Use the voice button or type your question and click "Ask"

## Supported Queries

### Recipe Display
- `show ingredients` - List all ingredients
- `show recipe` - Display all steps
- `show step 3` - Show a specific step

### Recipe Walkthrough
- `start recipe` - Begin step-by-step walkthrough
- `next` or `n` - Next step
- `back` or `b` - Previous step
- `repeat` - Repeat current step

### Ingredient Questions
- `how much salt do I need?`
- `how many eggs do I need?`
- `how much of that?` (in walkthrough mode)

### Cooking Questions
- `what temperature?`
- `how long to bake?`
- `how long does it take?`

### Substitutions
- `what can I substitute for butter?`
- `I don't have eggs`

### Definitions & How-To
- `what is zesting?` - Get Google search link
- `how do I julienne?` - Get YouTube video search link

## Browser Compatibility

**Speech Recognition:**
- Chrome (recommended)
- Edge
- Safari (limited)
- Firefox (text input only)

## Parsing Logic
All Parsing is handled by Google's Gemini. Model is specified in the header of this README

## Extra Credit Features

1. **Multi-website Support:** Supports allrecipes.com and seriouseats.com recipes
2. **Speech-to-Text:** Voice-enabled query interface using Web Speech API

## Tested Recipes

- `https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/`
- `https://www.allrecipes.com/recipe/228285/teriyaki-salmon/`
- `https://www.seriouseats.com/pecan-pie-cheesecake-recipe-11843450`
