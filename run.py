import json

def combine_data():
    with open('test.json', 'r') as f:
        data1 = json.load(f)
    with open('train.json', 'r') as f:
        data2 = json.load(f)
    combined_data = data1 + data2
    with open('combined.json', 'w') as f:
        json.dump(combined_data, f, indent=2)
combine_data()