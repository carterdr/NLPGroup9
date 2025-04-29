import json
from call_llm import call_model

# Combine datasets from test.json and train.json into combined.json
def combine_data():
    with open("dataset/test.json", "r") as f:
        data1 = json.load(f)
    with open("dataset/train.json", "r") as f:
        data2 = json.load(f)
    combined_data = data1 + data2
    with open("dataset/combined.json", "w") as f:
        json.dump(combined_data, f, indent=2)
# Use local ollama llm to add distracting field to the dataset
def add_distractions_column():
    with open("dataset/combined.json", "r") as f:
        data = json.load(f)
    index = 0
    for item in data:
        print(f"Processing item {index} of {len(data)}")
        body = item["Body"]
        question = item["Question"]
        distraction_prompt = f"""Your task is to add 1-2 distracting but contextually appropriate sentences to the following math problem:
BODY: {body}
QUESTION: {question}
IMPORTANT RULES:
1. DO NOT solve the problem or include any calculations. 
2. DO NOT mention the answer or any method to find the answer.
3. Attempt to add numbers that are not relevant to the problem.
4. ONLY return the distracting sentences without any other text.
5. Make distractions that are thematically related but irrelevant to solving the problem.
6. DO NOT FORMAT YOUR RESPONSE IN BULLET POINTS OR ANY OTHER FORMAT, JUST SCENTENCES.
7. Keep your response short - maximum 2 sentences."""
        distraction_text = call_model(distraction_prompt, create_distraction=True)
        item["Distracted"] = body + " " + distraction_text 
        index += 1
    with open("dataset/distracted.json", "w") as f:
        json.dump(data, f, indent=2)
        
if __name__ == "__main__":
    combine_data()
    add_distractions_column()