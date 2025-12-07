"""
Jewelry Shop Inventory Management 
Functions File
"""
import json
import os
from threading import Lock

# Data file path - will be mounted on NFS in Kubernetes
data_dir = os.getenv('DATA_DIR', '/var/www/flask_app/data')
data_file = os.path.join(data_dir, 'inventory.json')
file_lock = Lock()

# Ensure data directory exists
os.makedirs(data_dir, exist_ok=True)


def load_data():
    """Load inventory data from JSON file"""
    with file_lock:
        if not os.path.exists(data_file):
            return {'inventory': [], 'next_id': 1}
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {'inventory': [], 'next_id': 1}


def save_data(data):
    """Save inventory data to JSON file"""
    with file_lock:
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)


def initialize_dummy_data():
    """Initialize with dummy data if file is empty"""
    data = load_data()
    if not data['inventory']:
        dummy_items = [
            {"id": 1, "type": "ring", "category": "gold", "cost_price": 250.00, "selling_price": None, "status": "available"},
            {"id": 2, "type": "necklace", "category": "silver", "cost_price": 150.00, "selling_price": None, "status": "available"},
            {"id": 3, "type": "bracelet", "category": "gold", "cost_price": 180.00, "selling_price": 220.00, "status": "sold"},
            {"id": 4, "type": "ring", "category": "silver", "cost_price": 80.00, "selling_price": None, "status": "available"},
            {"id": 5, "type": "necklace", "category": "gold", "cost_price": 320.00, "selling_price": 400.00, "status": "sold"},
            {"id": 6, "type": "bracelet", "category": "silver", "cost_price": 95.00, "selling_price": None, "status": "available"},
            {"id": 7, "type": "ring", "category": "gold", "cost_price": 280.00, "selling_price": 350.00, "status": "sold"},
            {"id": 8, "type": "necklace", "category": "silver", "cost_price": 120.00, "selling_price": None, "status": "available"}
        ]
        data = {'inventory': dummy_items, 'next_id': 9}
        save_data(data)
    return data


def main_menu_handler():  # Menu Handler function
    print("\n   Main Menu")
    print("1️⃣  Add New Item")
    print("2️⃣  Show current inventory")
    print("3️⃣  Mark Item as Sold")
    print("4️⃣  Update item")
    print("5️⃣  Calculate profit summary")
    print("6️⃣  Get inventory summary")
    print("7️⃣  Quit")


def add_jewelry_item(item_type, category, cost_price):
    data = load_data()
    new_item = {
        "id": data['next_id'],
        "type": item_type,
        "category": category,
        "cost_price": round(cost_price, 2),
        "selling_price": None,
        "status": "available"
    }
    data['inventory'].append(new_item)
    data['next_id'] += 1
    save_data(data)
    return new_item


def mark_item_sold(item_id, selling_price):
    data = load_data()
    for item in data['inventory']:
        if item['id'] == item_id and item['status'] == 'available':
            item['status'] = 'sold'
            item['selling_price'] = round(float(selling_price), 2)
            save_data(data)
            return item
    return None


def calculate_profit_summary():
    data = load_data()
    inventory = data['inventory']
    total_cost_all = sum(item['cost_price'] for item in inventory)
    total_cost_available = sum(
        item['cost_price'] for item in inventory if item['status'] == 'available')
    total_cost_sold = sum(item['cost_price']
                          for item in inventory if item['status'] == 'sold')
    total_revenue = sum(item['selling_price'] for item in inventory if item['status']
                        == 'sold' and item.get('selling_price') is not None)
    total_profit = total_revenue - total_cost_sold

    profit_per_item = [
        {
            'id': item['id'],
            'type': item['type'],
            'profit': round(item['selling_price'] - item['cost_price'], 2)
        }
        for item in inventory
        if item['status'] == 'sold' and item.get('selling_price') is not None
    ]

    return {
        'total_cost_all': round(total_cost_all, 2),
        'total_cost_available': round(total_cost_available, 2),
        'total_cost_sold': round(total_cost_sold, 2),
        'total_revenue': round(total_revenue, 2),
        'total_profit': round(total_profit, 2),
        'profit_per_item': profit_per_item
    }


def update_item(item_id, updated_data):
    data = load_data()
    for item in data['inventory']:
        if item['id'] == item_id:
            for key, value in updated_data.items():
                item[key] = value
            save_data(data)
            return item
    return None


def show_current_inventory():
    data = load_data()
    return data['inventory']
