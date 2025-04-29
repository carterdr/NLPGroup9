import json
import time
from call_llm import call_model
from multiprocessing import Process
import os

def evaluate_model(model_name: str):
    visited_set = set() # using line number wasn't really working
    results_path = f"results/results_{model_name}.json"
    
    # find where left off if it was stopped early
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            for line in f:
                entry = json.loads(line)
                visited_set.add((entry["question_id"], entry["is_distracted"]))
    with open("dataset/distracted.json", "r") as f:
        data = json.load(f)
    with open(results_path, "a") as f_output:
        index = 0
        for item in data:
            # get info from the entry
            body = item["Body"]
            distracted_body = item["Distracted"]
            question = item["Question"]
            question_id = item["ID"]
            question_type = item["Type"]
            answer = item["Answer"]
            for is_distracted in [True, False]:
                # if we have already used this datapoint, skip it
                if (question_id, is_distracted) in visited_set:
                    continue
                # send prompt
                body_to_use = distracted_body if is_distracted else body
                prompt = f"Answer the following question using the information in the body with one number, and nothing else. Do not include any explanation, reasoning, quotes, or extra text. Return just a single number. For example if your answer is 100, return only 100. \nBody: {body_to_use}\n\nQuestion: {question}"
                model_response = call_model(prompt, create_distraction=False, model=model_name)
                
                try:
                    # deepseek always includes thinking in the question so we need to check if the final text is a number in order to have more meaningful statistics
                    if model_name == "deepseek":
                        model_response_as_num = float(model_response.split("\n")[-1])
                    else:
                        model_response_as_num = float(model_response.strip())
                    if model_response_as_num == answer:
                        # if the response number is correct its a true positive
                        result_type = "tp"
                    else:
                        # if the response number is wrong its a false positive
                        result_type = "fp"
                except Exception as e:
                    # if the response isnt a number its a false negative
                    result_type = "fn"
                    
                result = {
                    "model" : model_name,
                    "question_id" : question_id, # question id from the dataset
                    "question_type": question_type, # multiple choice or subtraction etc,
                    "is_distracted": is_distracted, # true or false
                    "result_type": result_type, #tp, fp, or fn, 
                    "model_response": model_response, # the model's response
                    "true_answer": answer, # the correct answer
                }
                f_output.write(json.dumps(result) + "\n")
                f_output.flush()
                # used to avoid rate limiting if possible
                time.sleep(1)
                index += 1
                if index % 100 == 0:
                    print(f"Processed {index} items for model {model_name}.")

if __name__ == "__main__":
    models = ["llama3", "mistral", "gemini"]
    processes = []
    for model in models:
        p = Process(target=evaluate_model, args=(model, ))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    # run after all the others since it uses the same api_key as llama3
    evaluate_model("deepseek")