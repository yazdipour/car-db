import json
import os
import glob

def process_brand_files():
    all_models = []
    parrent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_files = glob.glob(os.path.join(parrent_dir, 'data', 'processed', '**.json'))
    
    for file_path in json_files:
        brand_name = os.path.splitext(os.path.basename(file_path))[0]
        
        with open(file_path, 'r') as f:
            brand_data = json.load(f)
            for model in brand_data:
                model['brand'] = brand_name
                all_models.append(model)
    
    # Save merged data
    with open(parrent_dir + '/data/models_raw.json', 'w') as f:
        json.dump(all_models, f, indent=2)

def main():
    process_brand_files()

if __name__ == "__main__":
    main()
