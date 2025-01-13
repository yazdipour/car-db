import json
from bs4 import BeautifulSoup
from typing import List, Dict
import os

class CarExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_html(self) -> str:
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def extract_cars(self) -> List[Dict[str, str]]:
        html_content = self.read_html()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        cars = []
        car_containers = soup.find_all('div', class_='TopModels_model__zd0sT')
        
        for container in car_containers:
            img = container.find('img')
            link = container.find('a', class_='TopModels_title__lnpU6')
            
            # Clean up the name by removing extra spaces and newlines
            name = ' '.join(link.text.strip().split())
            
            car_info = {
                'img': img['src'],
                'link': link['href'],
                'name': name
            }
            cars.append(car_info)
            
        return cars

# Example usage
def extract_and_save_cars(__file__, CarExtractor, brand_name):
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = parent_dir + "/data/raw/" + brand_name + ".html"
    extractor = CarExtractor(file_path)
    cars = extractor.extract_cars()
    # save it in json file
    output_file = parent_dir + "/data/processed/" + brand_name + ".json"
    with open(output_file, 'w') as file:
        json.dump(cars, file, indent=4)

def process_all_brands(__file__, CarExtractor):
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(parent_dir, "data/raw")
    
    # Get all HTML files and extract brand names
    brand_names = [
        os.path.splitext(f)[0] 
        for f in os.listdir(raw_dir) 
        if f.endswith('.html')
    ]
    
    # Process each brand
    for brand_name in brand_names:
        print(f"Processing {brand_name}...")
        extract_and_save_cars(__file__, CarExtractor, brand_name)
        print(f"Completed {brand_name}")

if __name__ == "__main__":
    process_all_brands(__file__, CarExtractor)
