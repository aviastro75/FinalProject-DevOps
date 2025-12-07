import functions


def main():
    inventory = []

    while True:
        functions.main_menu_handler()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            while True:
                item_type = input(
                    "Enter item type (ring, bracelet, necklace): ").strip().lower()
                if item_type in ["ring", "bracelet", "necklace"]:
                    break
                print(
                    "Invalid item type. Please enter 'ring', 'bracelet', or 'necklace'.")

            while True:
                category = input(
                    "Enter category (silver, gold): ").strip().lower()
                if category in ["silver", "gold"]:
                    break
                print("Invalid category. Please enter 'silver' or 'gold'.")

            while True:
                try:
                    cost_price = float(
                        input("Enter cost price (positive number): "))
                    if cost_price > 0:
                        break
                    print("Cost price must be a positive number.")
                except ValueError:
                    print("Invalid input. Please enter a valid positive number.")

            inventory, new_item = functions.add_jewelry_item(
                inventory, item_type, category, cost_price
            )
            print(f"Item added successfully: {new_item}")

        elif choice == "2":
            inventory_list = functions.show_current_inventory(inventory)
            if inventory_list:
                print("\nCurrent Inventory:")
                for item in inventory_list:
                    print(f"ID: {item['id']}, Type: {item['type']}, Category: {item['category']}, Cost Price: ${item['cost_price']}, Selling Price: ${item['selling_price'] or 'N/A'}, Status: {item['status']}")
            else:
                print("Inventory is empty.")

        elif choice == "3":
            item_id = input("Enter item ID to mark as sold: ").strip()
            try:
                selling_price = float(input("Enter selling price: "))
                inventory, updated_item = functions.mark_item_sold(
                    inventory, item_id, selling_price)
                if updated_item:
                    print(f"Item marked as sold successfully: {updated_item}")
                else:
                    print("Item not found or invalid ID.")
            except ValueError:
                print("Invalid input. Please enter valid values.")

        elif choice == "4":
            try:
                item_id = int(input("Enter item ID to update: ").strip())
                print("Enter new values (press Enter to keep unchanged):")
                item_type = input("New item type: ").strip() or None
                category = input("New category: ").strip() or None
                cost_price = input("New cost price: ").strip()
                selling_price = input("New selling price: ").strip()
                status = input("New status (available/sold): ").strip() or None

                updated_data = {}
                if item_type:
                    updated_data['type'] = item_type
                if category:
                    updated_data['category'] = category
                if cost_price:
                    updated_data['cost_price'] = round(float(cost_price), 2)
                if selling_price:
                    updated_data['selling_price'] = round(
                        float(selling_price), 2)
                if status:
                    updated_data['status'] = status.lower()

                updated_item = functions.update_item(
                    inventory, item_id, updated_data)
                if updated_item:
                    print(f"Item updated successfully: {updated_item}")
                else:
                    print("Item not found.")
            except ValueError:
                print("Invalid input. Please enter valid values.")

        elif choice == "5":
            profit_summary = functions.calculate_profit_summary(inventory)
            print("\nProfit Summary:")
            print(
                f"Total Cost (All Items): ${profit_summary['total_cost_all']}")
            print(
                f"Total Cost (Available): ${profit_summary['total_cost_available']}")
            print(f"Total Cost (Sold): ${profit_summary['total_cost_sold']}")
            print(f"Total Revenue: ${profit_summary['total_revenue']}")
            print(f"Total Profit: ${profit_summary['total_profit']}")
            print("Profit per sold item:")
            for item in profit_summary['profit_per_item']:
                print(
                    f"ID: {item['id']}, Type: {item['type']}, Profit: ${item['profit']}")

        elif choice == "6":
            print("Exiting program...")
            break

        else:
            print("Invalid choice. Please select 1-7.")


if __name__ == "__main__":
    main()
