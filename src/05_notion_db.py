import json
import os
from notion_client import Client
from typing import Dict, Any
from tqdm import tqdm

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PARRENT_PAGE_ID = os.getenv("PARRENT_PAGE_ID")
notion = Client(auth=NOTION_TOKEN)

def create_car_database(parent_page_id: str) -> str:
    """Create a new database in Notion with car-specific properties"""
    
    properties = {
        "Model": {"title": {}},  # Title field
        "Brand": {
            "select": {
                "options": [
                    {"name": "audi", "color": "blue"},
                    {"name": "bmw", "color": "blue"}, 
                    {"name": "benz", "color": "blue"},
                    {"name": "citroen", "color": "red"},
                    {"name": "fiat", "color": "green"},
                    {"name": "ford", "color": "gray"},
                    {"name": "honda", "color": "red"},
                    {"name": "hyundai", "color": "red"},
                    {"name": "kia", "color": "red"},
                    {"name": "lexus", "color": "red"},
                    {"name": "mazda", "color": "red"},
                    {"name": "mitsubishi", "color": "red"},
                    {"name": "nissan", "color": "red"},
                    {"name": "toyota", "color": "red"},
                    {"name": "vw", "color": "blue"},
                ]
            }
        },
        "Category": {"rich_text": {}},  # Changed to rich_text
        "Insurance": {"rich_text": {}},  # Changed to rich_text
        "Image": {"url": {}},
        "Link": {"url": {}},
        "New Price": {"rich_text": {}},
        "Strengths": {"rich_text": {}},
        "Weaknesses": {"rich_text": {}},
        # Technical Data properties
        "Tech - 0 to 100": {"rich_text": {}},
        "Tech - Top Speed": {"rich_text": {}},
        "Tech - CO2 Emissions": {"rich_text": {}},
        "Tech - Consumption": {"rich_text": {}},
        "Tech - Emissions Std": {"rich_text": {}},
        "Tech - Dimensions": {"rich_text": {}},
        "Tech - Doors": {"rich_text": {}},
        "Tech - Trunk": {"rich_text": {}},
        "Tech - Tow Capacity": {"rich_text": {}},
        # ADAC Score properties
        "ADAC - Final": {"rich_text": {}},
        "ADAC - Families": {"rich_text": {}},
        "ADAC - Seniors": {"rich_text": {}},
        "ADAC - Transport": {"rich_text": {}},
        "ADAC - Value for money": {"rich_text": {}},
        "ADAC - City traffic": {"rich_text": {}},
        "ADAC - Long distance": {"rich_text": {}},
        "ADAC - Driving pleasure": {"rich_text": {}}
    }
    
    new_database = notion.databases.create(
        parent={"page_id": parent_page_id},
        title=[{"text": {"content": "Car DB"}}],
        properties=properties
    )
    
    return new_database["id"]

def prepare_car_entry(car: Dict[str, Any]) -> Dict[str, Any]:
    """Transform car data into Notion database entry format"""
    
    tech_data = car.get("tech_data", {})
    adac_scores = car.get("adac_scores", {})
    
    entry = {
        "Model": {"title": [{"text": {"content": car.get("name", "")}}]},
        "Brand": {"select": {"name": car.get("brand", "")}},
        "Category": {"rich_text": [{"text": {"content": str(car.get("category", ""))}}]},
        "Insurance": {"rich_text": [{"text": {"content": str(car.get("insurance", ""))}}]},
        "Link": {"url": car.get("link", "")},
        "New Price": {"rich_text": [{"text": {"content": str(car.get("new_price", ""))}}]},
        "Strengths": {"rich_text": [{"text": {"content": str(car.get("strengths", ""))}}]},
        "Weaknesses": {"rich_text": [{"text": {"content": str(car.get("weaknesses", ""))}}]},
        # Technical Data fields
        "Tech - 0 to 100": {"rich_text": [{"text": {"content": str(tech_data.get("0to100", ""))}}]},
        "Tech - Top Speed": {"rich_text": [{"text": {"content": str(tech_data.get("Top Speed", ""))}}]},
        "Tech - CO2 Emissions": {"rich_text": [{"text": {"content": str(tech_data.get("CO2 emissions", ""))}}]},
        "Tech - Consumption": {"rich_text": [{"text": {"content": str(tech_data.get("Consumption", ""))}}]},
        "Tech - Emissions Std": {"rich_text": [{"text": {"content": str(tech_data.get("Emissions Std", ""))}}]},
        "Tech - Dimensions": {"rich_text": [{"text": {"content": str(tech_data.get("Dimensions(L/W/H)", ""))}}]},
        "Tech - Doors": {"rich_text": [{"text": {"content": str(tech_data.get("Doors", ""))}}]},
        "Tech - Trunk": {"rich_text": [{"text": {"content": str(tech_data.get("Trunk", ""))}}]},
        "Tech - Tow Capacity": {"rich_text": [{"text": {"content": str(tech_data.get("Tow Capacity", ""))}}]},
        # ADAC Score fields
        "ADAC - Final": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - Final", ""))}}]},
        "ADAC - Families": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - Families", ""))}}]},
        "ADAC - Seniors": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - Seniors", ""))}}]},
        "ADAC - Transport": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - Transport", ""))}}]},
        "ADAC - Value for money": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - Value for money", ""))}}]},
        "ADAC - City traffic": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - City traffic", ""))}}]},
        "ADAC - Long distance": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - Long distance", ""))}}]},
        "ADAC - Driving pleasure": {"rich_text": [{"text": {"content": str(adac_scores.get("Score - Driving pleasure", ""))}}]}
    }
    return entry

def populate_database(database_id: str, cars: list):
    """Add car entries to the Notion database"""
    
    for car in tqdm(cars, desc="Adding cars to Notion database"):
        properties = prepare_car_entry(car)
        try:
            notion.pages.create(
                parent={"database_id": database_id},
                properties=properties,
                cover = {"type": "external", "external": {"url": car.get("img")}}
            )
        except Exception as e:
            print(f"Error adding car {car.get('name')}: {str(e)}")

def main():
    parrent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(parrent_dir, "data", "models_final.json"), "r") as f:
        cars = json.load(f)
    
    # Parent page ID is where you want to create the database
    # Create the database
    database_id = create_car_database(PARRENT_PAGE_ID)
    
    # Populate the database with car entries
    populate_database(database_id, cars)

if __name__ == "__main__":
    main()
