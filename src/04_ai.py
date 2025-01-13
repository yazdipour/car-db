import json
import os
import time
import ollama

def translate_text(text, client, model='qwen2.5'):
    if not text:
        return ""
    prompt = f"""Translate this German text to English. 
Please respond only in plain English without any Chinese characters or other languages.
Only return the final translated text:
{text}"""
    try:
        response = client.generate(model=model, prompt=prompt)
        # Add small delay to avoid overwhelming the model
        # time.sleep(0.5)
        return response['response'].strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def classify_category(model_name, client, model='qwen2.5'):
    if not model_name:
        return ""
    
    prompt = """Based on this car model name, classify it into ONE of these categories:
    Sedan, Hatchback, SUV, Crossover, Minivan, Truck, Convertible, Coupe, or Roadster.
    Please respond only in plain English without any Chinese characters.
    Only return the category name, nothing else.
    Car model: """ + model_name
    
    try:
        response = client.generate(model=model, prompt=prompt)
        # time.sleep(0.5)
        return response['response'].strip()
    except Exception as e:
        print(f"Category classification error: {e}")
        return ""

def classify_insurance(model_name, client, model='qwen2.5'):
    if not model_name:
        return ""
    
    prompt = """Based on this car model name, classify its expected insurance cost in Germany into:
    High (expensive luxury/sports cars)
    Medium (mid-range cars)
    Low (economy cars)
    Please respond only in plain English without any Chinese characters.
    Only return High, Medium, or Low, nothing else.
    Car model: """ + model_name
    
    try:
        response = client.generate(model=model, prompt=prompt)
        # time.sleep(0.5)
        return response['response'].strip()
    except Exception as e:
        print(f"Insurance classification error: {e}")
        return ""

def main():
    # Create Ollama client
    client = ollama

    # Load JSON data
    parrent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    with open(f'{parrent_dir}/data/models_raw2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each entry
    for item in data:
        item['strengths'] = translate_text(item['strengths'], client)
        print(f"-> {item['strengths']}")
        item['weaknesses'] = translate_text(item['weaknesses'], client)
        print(f"-> {item['weaknesses']}")
        item['category'] = classify_category(item.get('name', ''), client)
        print(f"-> Category: {item['category']}")
        # Add insurance classification
        item['insurance'] = classify_insurance(item.get('name', ''), client)
        print(f"-> Insurance: {item['insurance']}")

    # Save translated and categorized data
    with open('data/models_final.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
