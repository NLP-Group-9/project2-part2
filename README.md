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

## User Inputs
[INSERT ALL AVAILABLE USER INPUTS HERE FOR TA TO READ FROM]

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
