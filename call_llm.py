import os
import requests
import time
from dotenv import load_dotenv
load_dotenv()

GROQ_MODELS = {
    "llama3": "llama3-8b-8192",
    "deepseek": "deepseek-r1-distill-llama-70b"
}
API_KEYS = {
    "groq": os.environ.get("GROQ_API_KEY", ""),
    "gemini": os.environ.get("GEMINI_API_KEY", ""),
    "mistral": os.environ.get("MISTRAL_API_KEY", ""),
}

def call_groq_api(prompt: str, temperature: float, model: str = "llama3") -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEYS['groq']}",
    }
    model_name = GROQ_MODELS.get(model, GROQ_MODELS["llama3"])

    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature #want no creativity if not creating distraction
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def call_gemini_api(prompt: str, temperature: float) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEYS['gemini']}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature}
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def call_mistral_api(prompt: str, temperature: float) -> str:
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEYS['mistral']}"
    }
    data = {
        "model": "mistral-large-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature #want no creativity if not creating distraction
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Used to create distaction column in the dataset and only works locally
def call_ollama_local(prompt: str, temperature: float) -> str:
    data = {
        "model": "mistral",
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/generate", json=data)
    response.raise_for_status()
    return response.json()["response"].strip()



# Call specific model and handle exceptions with retries
def call_model(prompt: str, create_distraction: bool, model: str = "ollama", retries : int = 0) -> str:
    temperature = 0.7 if create_distraction else 0.0
    try: 
        if model == "ollama":
            return call_ollama_local(prompt, temperature)
        elif model == "gemini":
            return call_gemini_api(prompt, temperature)
        elif model == "mistral":
            return call_mistral_api(prompt, temperature)
        elif model == "llama3" or model == "deepseek":
            return call_groq_api(prompt, temperature, model)
        else:
            raise ValueError(f"Unsupported model: {model}")
    except requests.exceptions.HTTPError as e:
        # use an increasing backoff time to avoid rate limiting
        if e.response.status_code == 429:
            wait_time = 10 * (retries + 1)
            print(f"Rate limit exceeded for {model}. Retrying in {wait_time} seconds.")
            time.sleep(wait_time)
            return call_model(prompt, create_distraction, model, retries + 1)
        else:
            print(e)
            return ""
    except Exception as e:
        print(e)
        return ""
    