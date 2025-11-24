#Project 1
python ver. 3.11.9
Github link: https://github.com/NLP-Group-9/project2

## Dependencies
This project requires the following Python packages:

- requests
- beautifulsoup4
- spacy

Install them with:
pip install -r requirements.txt

Also install the following spacy model:
python -m spacy download en_core_web_sm

## Steps to run
1) Run recipe_chat with:
>python3 recipe_chat.py

## User Inputs (examples/available inputs)
Note: this is not all of the possible ways to ask questions and recieve relevant
output using our bot, but it is comprehensive and these queries cover everything 
that our bot is designed to do.

**Recipe Retrieval and Display:**
Requests to show a recipe or its components.

“Show me the ingredients list.”
"What are the ingredients?"
"Ingredints Please"
“Display the recipe.”
"Show me the full recipe"

**Navigation Commands**
Moving between, repeating, or revisiting recipe steps.

"Start the recipe walkthrough"
"Start cooking"
"Start"
“Go back a step.”
"Go back"
"Next"
“Go to the next step.”
“Repeat please.”
“Take me to step 3.”
“What’s next?”
“What was that again?”
"Resume recipe walkthrough"
"Resume"

**Step Parameter Queries**
Asking about quantities, times, temperatures, or substitutes within the current step.

“How much salt do I need?”
“What temperature should the oven be?”
“How long do I bake it?” (Only works if "bake" is included as a step in the recipe),
otherwise try with relevant verb(s)
“When is it done?”
“What can I use instead of butter?”
"What can I substitute for butter?"

**Clarification Questions**
Asking for definitions or explanations of terms or tools.

“What is a whisk?” or "what's x"
"How do i sautee?" or "how do i x?"


**Procedure Questions**
Asking how to perform an action or technique.

“How do I knead the dough?”
“How do I do that?” — referring to the current step’s action.
"What is that?" referring to the current step’s action.
Note: for questions relevant to only one step, make sure to say "start" or start the recipe walkthrough 
before asking such questions


**Quantity Questions**
Asking about ingredient amounts.

Specific: “How much flour do I need?”
Vague (step-dependent): “How much of that do I need?” — referring to an ingredient mentioned in the current step. 
Again, make sure to start the recipe walkthrough before asking questions of this nature.


## Parsing Logic
1) Ingredient and Instruction extraction from websites.
   We use BeautifulSoup to read the url and then identify hard coded html tags to identify and extract ingredients and instructions text from the url.

2) Ingredient Parsing.
   The websites that work (allrecipes and seriouseats) have the html tags already differentiate the name, quantity, and measurements of the ingredients which made it incredibly easy to parse. We use this information because it was already expertly prepared by the writer.

3) Atomize Instructions.
   We first atomize the steps by splitting the instructions by common conjunctions and punctuation.

4) Instruction Parsing.
   The main purpose of this step is to identify the ingredients, tools, methods, times, and temps available in a specified instruction step.
   - Ingredients were identified from the ingredients obtained from Step 2). We used substring search for the ingredients since some of the ingredients appear with shorter names in the ingredients.
   - Tools were identified from using a hardcoded list of tools.
   - Methods were extracted from a hardcoded list plus the use of spaCy tagging for VERBS
   - Time was extracted by finding common temp terms (medium heat, low heat, etc) and the detection of numbers from units (Fahrenheit, Celsius, etc)
   - Temp was extracted by finding common numbers including units (seconds, minutes, hours, etc).

## Extra Credit Features
1) Supports allrecipes.com AND seriouseats.com recipes. We tried to also get functionality for the listed websites on the project page: epicurious, bonappetit, delish, and foodnetwork but all of them had issues that were out of our control.
Mainly, epicurious, bonappetit, delish required a paid subscription to access recipes. Foodnetwork did not allow for out html reader to access the website.

2) (IN PROGRESS) Speech to text functionality.
