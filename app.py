from flask import Flask, request, render_template, redirect, url_for
import functions

app = Flask(__name__)

# Initialize with dummy data on first run
functions.initialize_dummy_data()


@app.route('/')
def home():
    return render_template('menu.html')


@app.route('/health')
def health_check():
    """Health check endpoint for Kubernetes"""
    try:
        # Check if data file is accessible
        inventory = functions.show_current_inventory()
        return {'status': 'healthy', 'items_count': len(inventory)}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_type = request.form.get('type', '').strip().lower()
        category = request.form.get('category', '').strip().lower()
        cost_price_str = request.form.get('cost_price', '').strip()

        if item_type not in ['ring', 'bracelet', 'necklace']:
            return render_template('add.html', error='Invalid item type. Must be ring, bracelet, or necklace.')
        if category not in ['silver', 'gold']:
            return render_template('add.html', error='Invalid category. Must be silver or gold.')
        try:
            cost_price = float(cost_price_str)
            if cost_price <= 0:
                raise ValueError
        except ValueError:
            return render_template('add.html', error='Invalid cost price. Must be a positive number.')

        functions.add_jewelry_item(item_type, category, cost_price)
        return redirect(url_for('home'))

    return render_template('add.html')


@app.route('/show')
def show_inventory():
    try:
        inventory_list = functions.show_current_inventory()
        return render_template('show.html', items=inventory_list)
    except Exception as e:
        return render_template('show.html', error=f"Error loading inventory: {str(e)}")


@app.route('/sold', methods=['GET', 'POST'])
def mark_sold():
    if request.method == 'POST':
        item_id_str = request.form.get('id', '').strip()
        selling_price_str = request.form.get('selling_price', '').strip()

        try:
            item_id = int(item_id_str)
            selling_price = float(selling_price_str)
            if selling_price <= 0:
                raise ValueError("Selling price must be positive")
            updated_item = functions.mark_item_sold(item_id, selling_price)
            if not updated_item:
                raise ValueError('Item not found or already sold.')
            return redirect(url_for('home'))
        except ValueError as e:
            return render_template('sold.html', error=str(e))
        except Exception as e:
            return render_template('sold.html', error=f"Error marking item as sold: {str(e)}")

    return render_template('sold.html')


@app.route('/update', methods=['GET', 'POST'])
def update_item():
    if request.method == 'POST':
        try:
            item_id_str = request.form.get('id', '').strip()
            item_id = int(item_id_str)

            updated_data = {}
            item_type = request.form.get('type', '').strip().lower()
            if item_type:
                if item_type not in ['ring', 'bracelet', 'necklace']:
                    raise ValueError('Invalid item type.')
                updated_data['type'] = item_type
            category = request.form.get('category', '').strip().lower()
            if category:
                if category not in ['silver', 'gold']:
                    raise ValueError('Invalid category.')
                updated_data['category'] = category
            cost_price_str = request.form.get('cost_price', '').strip()
            if cost_price_str:
                cost_price = float(cost_price_str)
                if cost_price <= 0:
                    raise ValueError('Invalid cost price.')
                updated_data['cost_price'] = round(cost_price, 2)
            selling_price_str = request.form.get('selling_price', '').strip()
            if selling_price_str:
                selling_price = float(selling_price_str)
                if selling_price <= 0:
                    raise ValueError('Invalid selling price.')
                updated_data['selling_price'] = round(selling_price, 2)
            status = request.form.get('status', '').strip().lower()
            if status:
                if status not in ['available', 'sold']:
                    raise ValueError('Invalid status.')
                updated_data['status'] = status

            updated = functions.update_item(item_id, updated_data)
            if not updated:
                raise ValueError('Item not found.')
            return redirect(url_for('home'))
        except ValueError as e:
            return render_template('update.html', error=str(e))
        except Exception as e:
            return render_template('update.html', error=f"Error updating item: {str(e)}")

    return render_template('update.html')


@app.route('/profit')
def profit_summary():
    try:
        summary = functions.calculate_profit_summary()
        return render_template('profit.html', summary=summary)
    except Exception as e:
        return render_template('profit.html', error=f"Error loading profit summary: {str(e)}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
