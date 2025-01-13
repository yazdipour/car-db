import json
from bs4 import BeautifulSoup
import os
from typing import List, Dict
import requests
import time

tech_keys = {
    "von 0 auf 100 km/h": "0to100",
    "Höchstgeschwindigkeit": "Top Speed",
    "CO2-Ausstoß (komb.)": "CO2 emissions",
    "Verbrauch (komb.)": "Consumption",
    "Abgasnorm": "Emissions Std",
    "Maße (L/B/H) ab": "Dimensions(L/W/H)",
    "Türen": "Doors",
    "Kofferraum": "Trunk",
    "Anhängelast": "Tow Capacity"
}

adac_keys = {
    "Autotest": "Score - Final",
    "Familien": "Score - Families",
    "Senioren": "Score - Seniors", 
    "Transport": "Score - Transport",
    "Preis/Leistung": "Score - Value for money",
    "Stadtverkehr": "Score - City traffic",
    "Langstrecke": "Score - Long distance", 
    "Fahrspaß": "Score - Driving pleasure"
}

def extract_pros_cons(soup: BeautifulSoup, class_name: str) -> str:
    """Extract and merge list items under a specific section"""
    try:
        section = soup.find('div', {'class': class_name})
        if not section:
            return ""
        items = section.find_all('li')
        return " - ".join([item.text.strip() for item in items]) if items else ""
    except:
        return ""

def extract_price(soup: BeautifulSoup, price_type: str) -> str:
    """Extract price information"""
    try:
        rows = soup.find_all('div', {'class': 'OverviewTabs_row___xHUM'})
        for row in rows:
            label = row.find('span', {'class': 'OverviewTabs_label__JJrDq'})
            if label and price_type in label.text:
                price = row.find('button')
                if price:
                    return price.text.strip()
        return ""
    except:
        return ""

def extract_tech_data(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract technical data from the overview tab"""
    tech_data = {}
    try:
        tech_rows = soup.find_all('div', {'class': 'OverviewTabs_row___xHUM'})
        for row in tech_rows:
            label = row.find('span', {'class': 'OverviewTabs_label__JJrDq'})
            value = row.find_all('span')[-1]  # Last span contains the value
            if label and value and label != value:
                key = label.text.strip().replace(':', '')
                # Use English key if available, otherwise use German key
                eng_key = tech_keys.get(key, key)
                tech_data[eng_key] = value.text.strip()
    except:
        pass
    return tech_data

def extract_adac_scores(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract ADAC test scores for both primary (Autotest) and secondary scores"""
    scores = {}
    try:
        # Extract primary score (Autotest)
        primary_score = soup.find('div', {'class': 'ADACScoreRow_primary__6AQLF'})
        if primary_score:
            label = primary_score.find('p', {'data-testid': 'adac-score-text'})
            rating = primary_score.find('p', {'data-testid': 'adac-score-rating'})
            if label and rating:
                key = label.text.strip()
                eng_key = adac_keys.get(key, key)
                scores[eng_key] = rating.text.strip()

        # Extract secondary scores
        score_rows = soup.find_all('div', {'class': 'ADACScoreRow_secondary__S_xH0'})
        for row in score_rows:
            label = row.find('p', {'data-testid': 'adac-score-text'})
            rating = row.find('p', {'data-testid': 'adac-score-rating'})
            if label and rating:
                key = label.text.strip()
                eng_key = adac_keys.get(key, key)
                scores[eng_key] = rating.text.strip()
    except:
        pass
    return scores

def crawl_model_page(url: str) -> Dict:
    """Crawl a single model page and extract information"""
    try:
        # Add delay to avoid overwhelming the server
        time.sleep(1)
        
        # If URL doesn't start with http, add the domain
        if not url.startswith('http'):
            url = 'https://www.autoscout24.de' + url
            
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'strengths': extract_pros_cons(soup, 'ProsAndCons_content__ZSyz2'),
            'weaknesses': extract_pros_cons(soup, 'ProsAndCons_content__ZSyz2'),  # Gets second instance
            'new_price': extract_price(soup, 'Neu ab'),
            'tech_data': extract_tech_data(soup),
            'adac_scores': extract_adac_scores(soup)
        }
        
        return data
    
    except Exception as e:
        print(f"Error crawling {url}: {str(e)}")
        return {}

def main():
    # Read the models_raw.json file
    parrent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    try:
        with open(parrent_dir + '/data/models_raw.json', 'r', encoding='utf-8') as f:
            models = json.load(f)
    except Exception as e:
        print(f"Error reading models_raw.json: {str(e)}")
        return

    # Process each model
    for model in models:
        print(f"Processing {model['name']}...")
        
        # Get additional data from the model page
        additional_data = crawl_model_page(model['link'])
        
        # Update the model object with new data
        model.update(additional_data)

    # Save the updated data back to models_raw.json
    try:
        with open(parrent_dir + '/data/models_raw2.json', 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=2)
        print("Successfully updated models_raw.json")
    except Exception as e:
        print(f"Error saving models_raw.json: {str(e)}")

if __name__ == "__main__":
    main()
