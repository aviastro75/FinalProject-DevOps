"""
Jewelry Shop Inventory Management 
Functions File
"""


def main_menu_handler():  # Menu Handler function
    print("\n   Main Menu")
    print("1️⃣  Add New Item")
    print("2️⃣  Show current inventory")
    print("3️⃣  Mark Item as Sold")
    print("4️⃣  Update item")
    print("5️⃣  Calculate profit summary")
    print("6️⃣  Quit")


def generate_next_id(inventory):
    if not inventory:
        return 1
    return max(item['id'] for item in inventory) + 1


def add_jewelry_item(inventory, item_type, category, cost_price):
    new_item = {
        "id": generate_next_id(inventory),
        "type": item_type.strip(),
        "category": category.strip(),
        "cost_price": round(cost_price, 2),
        "selling_price": None,
        "status": "available"
    }
    inventory.append(new_item)
    return inventory, new_item


def mark_item_sold(inventory, item_id, selling_price):
    if not str(item_id).isdigit():
        return inventory, None

    item_id = int(item_id)
    for item in inventory:
        if item['id'] == item_id and item['status'] == "available":
            item['status'] = "sold"
            item['selling_price'] = round(float(selling_price), 2)
            return inventory, item
    return inventory, None


def calculate_profit_summary(inventory):
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


def update_item(inventory, item_id, updated_data):
    for item in inventory:
        if item['id'] == item_id:
            item.update(updated_data)
            return item
    return None


def show_current_inventory(inventory):
    return [
        {
            'id': item['id'],
            'type': item['type'],
            'category': item['category'],
            'cost_price': item['cost_price'],
            'selling_price': item['selling_price'],
            'status': item['status']
        }
        for item in inventory
    ]
