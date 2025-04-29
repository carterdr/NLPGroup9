# NLPGroup9

# Setup Instructions
### If you want to create the distracted.json dataset
1. Install ollama from https://ollama.com/download
```bash
ollama pull mistral
ollama serve
```
2. Download train.json and test.json from https://huggingface.co/datasets/ChilleD/SVAMP/tree/main and put them into the dataset/ folder
3. Next navigate to the root project folder and run
```bash
python3 edit_dataset.py
```
   - This will combine the two datasets into combined.json
   - Then, using the locally hosted mistral, this will create a new distracted.json file with the new "Distracted" field in each entry containing the new body + distracting information
### Creating the Model Statistical Results
1. In order to obtain the results on the distracted and non-distracted data run
```bash
python3 run.py
```
   - This will call the APIs of mistral-large-latest, llama3-8b-8192 and gemini-2.0-flash models concurrently to save time.
   - Once these three finish running, deepseek-r1-distill-llama-70b will run because it uses the same API Key as llama3-8b-8192, allowing us to avoid rate limiting.
   - For each model, it will loop over all 2000 (1000 distracted, 1000 non-distracted) entries in the distracted.json dataset, save the answer the model gave, whether this is a TP, FN, or FP, and the type of question to a model specific json file.
   - These model specific results are then saved in the results/ folder
   - If the creation of the statistics is interrupted, it will pick up where it left off
3. In order to create the statistics file run
```bash
python3 create_results.py
```


After the mistral-large-latest, llama3-8b-8192 and gemini-2.0-flash models completed, the deepseek model started to run, and I noticed that it was including the long reasoning in its responses. So the prompt was changed to be more strict with only including the number result for DeepSeek only.

f"Answer the following question using the information in the body with one number, and nothing else. No explanation, no quotes, no labels, just a single number.\nBody: {body_to_use}\n\nQuestion: {question}"


NEW PROMPT
prompt = f"Answer the following question using the information in the body with one number, and nothing else. Do not include any explanation, reasoning, quotes, or extra text. Return just a single number.\nBody: {body_to_use}\n\nQuestion: {question}"
