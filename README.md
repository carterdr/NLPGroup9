# NLPGroup9

# Setup Instructions
### Install Dependences
```bash
pip install -r requirements.txt
```
### If you want to create the distracted.json dataset
1. Install ollama from https://ollama.com/download
```bash
ollama pull mistral
ollama serve
```
2. Download train.json and test.json from https://huggingface.co/datasets/ChilleD/SVAMP/tree/main and put them into the dataset/ folder
3. Set up .env variables with your GROQ_API_KEY, GEMINI_API_KEY, and MISTRAL_API_KEY
4. Next navigate to the root project folder and run
```bash
python3 edit_dataset.py
```
   - This will combine the two datasets into combined.json
   - Then, using the locally hosted mistral, this will create a new distracted.json file with the new "Distracted" field in each entry containing the new body + distracting information
### Creating the Model Statistical Results
1. In order to obtain the results on the distracted and non-distracted data run
```bash
python3 create_results.py
```
   - This will call the APIs of mistral-large-latest, llama3-8b-8192 and gemini-2.0-flash models concurrently to save time.
   - Once these three finish running, deepseek-r1-distill-llama-70b will run because it uses the same API Key as llama3-8b-8192, allowing us to avoid rate limiting.
   - For each model, it will loop over all 2000 (1000 distracted, 1000 non-distracted) entries in the distracted.json dataset, save the answer the model gave, whether this is a TP, FN, or FP, and the type of question to a model specific json file.
   - These model specific results are then saved in the results/ folder
   - If the creation of the statistics is interrupted, it will pick up where it left off
3. In order to create the statistics file run
```bash
python3 stats.py
```
   - This will loop through the four results json files and put all results into one list then turn the list into a pandas dataframe
   - We group the stats by model, by is_distracted, question_type and include a special version of is_distrated that only has the tp, fn and fp counts
   - We calculate the accuracy, precision, recall and f1 scores for each of these groups.
   - Finally each pandas frame is saved to a seperate sheet in the excel file.
# Model APIs
1. **mistral-large-latest** and **deepseek-r1-distill-llama-70b** were run using https://api.groq.com/openai/v1/chat/completions
2. **llama3-8b-8192** was run with https://api.mistral.ai/v1/chat/completions
3. **gemini-2.0-flash** was run with https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash
4. call_llm.py handles calling all the LLM APIs
# Problems encountered
1. We all originally created the code on google colab and then realized later that we were supposed to have a GitHub so Carter decided to move it himself.
2. After the mistral-large-latest, llama3-8b-8192 and gemini-2.0-flash models completed, the deepseek model started to run, and we noticed that it was including its long reasoning in its responses. So the prompt was changed to be more strict with only including the number result for DeepSeek only. This didn't work very well so we decided to take the value after the last "\n" in the deepseek response and treat it as the response. If we didn't do this the response would always be a fn even though the model had the right answer. 

### Orignal Prompt:
   ```python
   f"Answer the following question using the information in the body with one number, and nothing else. No explanation, no quotes, no labels, just a single number.\nBody: {body_to_use}\n\nQuestion: {question}"
   ```
### New Prompt:
   ```python
   f"Answer the following question using the information in the body with one number, and nothing else. Do not include any explanation, reasoning, quotes, or extra text. Return just a single number.\nBody: {body_to_use}\n\nQuestion: {question}"
   ```
