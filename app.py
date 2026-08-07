"""
Affan's Kitchen - Restaurant Order / POS System
------------------------------------------------
A single-file Streamlit app for taking orders (Breakfast / Lunch / Dinner),
printing bills/receipts, tracking daily sales, and managing inventory.
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import json

st.set_page_config(page_title="Affan's Kitchen - POS", page_icon="🍲", layout="wide")

MENU = {
    "Breakfast": {
        "Aloo Paratha": 150,
        "Chana": 120,
        "Omelette": 80,
        "Fried Egg": 70,
        "Egg Masala": 130,
        "Tea": 50,
    },
    "Lunch": {
        "Daal Chawal": 200,
        "Anda Tikki": 90,
        "Naan": 40,
        "Raita": 60,
        "Salad": 50,
        "Achaar": 30,
    },
    "Dinner": {
        "Chicken Kabab": 250,
        "Mutton Kabab": 350,
        "Leg Piece": 300,
        "Chest Piece": 280,
        "Tikka Boti": 320,
        "Malai Boti": 330,
    },
}

RESTAURANT_NAME = "Affan's Kitchen"
RESTAURANT_TAGLINE = "Tradition in Every Bite"

# Pakistan timezone offset (UTC+5)
PAKISTAN_OFFSET = timedelta(hours=5)

def get_pakistan_time():
    """Get current time in Pakistan (UTC+5)"""
    return datetime.utcnow() + PAKISTAN_OFFSET

# Initialize databases
def init_db():
    # Orders database
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            date TEXT,
            time TEXT,
            items TEXT,
            subtotal REAL,
            tax_rate REAL,
            tax_amount REAL,
            grand_total REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    
    # Inventory database
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            category TEXT,
            quantity REAL,
            unit TEXT,
            min_stock REAL,
            cost_per_unit REAL,
            last_updated TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_order_to_db(order):
    """Save order to SQLite database"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO orders (order_id, date, time, items, subtotal, tax_rate, tax_amount, grand_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order["order_id"],
        order["date"],
        order["time"],
        json.dumps(order["items"]),
        order["subtotal"],
        order["tax_rate"],
        order["tax_amount"],
        order["grand_total"]
    ))
    conn.commit()
    conn.close()

def load_orders_from_db():
    """Load all orders from SQLite database"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT id, order_id, date, time, items, subtotal, tax_rate, tax_amount, grand_total FROM orders ORDER BY id')
    rows = c.fetchall()
    conn.close()
    
    orders = []
    for row in rows:
        orders.append({
            "db_id": row[0],
            "order_id": row[1],
            "date": row[2],
            "time": row[3],
            "items": json.loads(row[4]),
            "subtotal": row[5],
            "tax_rate": row[6],
            "tax_amount": row[7],
            "grand_total": row[8]
        })
    return orders

def delete_order_from_db(db_id):
    """Delete a specific order from database by its ID"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('DELETE FROM orders WHERE id = ?', (db_id,))
    conn.commit()
    conn.close()

def delete_all_orders_from_db():
    """Delete all orders from database"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('DELETE FROM orders')
    conn.commit()
    conn.close()

# Inventory database functions
def add_inventory_item(item_name, category, quantity, unit, min_stock, cost_per_unit, notes=""):
    """Add a new item to inventory"""
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    last_updated = get_pakistan_time().strftime("%d-%m-%Y %I:%M %p")
    try:
        c.execute('''
            INSERT INTO inventory (item_name, category, quantity, unit, min_stock, cost_per_unit, last_updated, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_name, category, quantity, unit, min_stock, cost_per_unit, last_updated, notes))
        conn.commit()
        conn.close()
        return True, "Item added successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Item already exists!"

def update_inventory_quantity(item_id, new_quantity):
    """Update quantity of an inventory item"""
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    last_updated = get_pakistan_time().strftime("%d-%m-%Y %I:%M %p")
    c.execute('UPDATE inventory SET quantity = ?, last_updated = ? WHERE id = ?', (new_quantity, last_updated, item_id))
    conn.commit()
    conn.close()

def update_inventory_item(item_id, item_name, category, quantity, unit, min_stock, cost_per_unit, notes):
    """Update all fields of an inventory item"""
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    last_updated = get_pakistan_time().strftime("%d-%m-%Y %I:%M %p")
    c.execute('''
        UPDATE inventory 
        SET item_name = ?, category = ?, quantity = ?, unit = ?, min_stock = ?, cost_per_unit = ?, last_updated = ?, notes = ?
        WHERE id = ?
    ''', (item_name, category, quantity, unit, min_stock, cost_per_unit, last_updated, notes, item_id))
    conn.commit()
    conn.close()

def delete_inventory_item(item_id):
    """Delete an inventory item"""
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def load_inventory():
    """Load all inventory items"""
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM inventory ORDER BY category, item_name')
    rows = c.fetchall()
    conn.close()
    
    inventory = []
    for row in rows:
        inventory.append({
            "id": row[0],
            "item_name": row[1],
            "category": row[2],
            "quantity": row[3],
            "unit": row[4],
            "min_stock": row[5],
            "cost_per_unit": row[6],
            "last_updated": row[7],
            "notes": row[8]
        })
    return inventory

# Initialize databases
init_db()

# Initialize session state
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "order_placed" not in st.session_state:
    st.session_state.order_placed = False

if "last_order" not in st.session_state:
    st.session_state.last_order = None

if "daily_orders" not in st.session_state:
    st.session_state.daily_orders = load_orders_from_db()

if "menu_qty" not in st.session_state:
    st.session_state.menu_qty = {}

if "items_added" not in st.session_state:
    st.session_state.items_added = set()

if "delete_confirm" not in st.session_state:
    st.session_state.delete_confirm = None

if "delete_all_confirm" not in st.session_state:
    st.session_state.delete_all_confirm = False

# Inventory session states
if "inv_delete_confirm" not in st.session_state:
    st.session_state.inv_delete_confirm = None

if "editing_item" not in st.session_state:
    st.session_state.editing_item = None

if "inventory" not in st.session_state:
    st.session_state.inventory = load_inventory()


def add_to_cart(item, price, qty=1):
    """Add item to cart with specified quantity"""
    if item in st.session_state.cart:
        st.session_state.cart[item]["qty"] += qty
    else:
        st.session_state.cart[item] = {"qty": qty, "price": price}


def remove_from_cart(item):
    """Remove item completely from cart"""
    if item in st.session_state.cart:
        del st.session_state.cart[item]


def increase_qty(item, price):
    """Increase quantity of item in cart"""
    if item in st.session_state.cart:
        st.session_state.cart[item]["qty"] += 1
    else:
        st.session_state.cart[item] = {"qty": 1, "price": price}


def decrease_qty(item):
    """Decrease quantity of item in cart"""
    if item in st.session_state.cart:
        if st.session_state.cart[item]["qty"] > 1:
            st.session_state.cart[item]["qty"] -= 1
        else:
            del st.session_state.cart[item]


def clear_cart():
    """Clear the entire cart"""
    st.session_state.cart = {}
    st.session_state.order_placed = False
    st.session_state.items_added = set()


def save_order_to_history():
    """Save current order to history and database"""
    if not st.session_state.cart:
        return
    
    order_time = get_pakistan_time()
    order_date = order_time.strftime("%Y-%m-%d")
    
    items = []
    subtotal = 0
    for item, data in st.session_state.cart.items():
        qty = data["qty"]
        price = data["price"]
        line_total = qty * price
        subtotal += line_total
        items.append({
            "item": item,
            "qty": qty,
            "price": price,
            "total": line_total
        })
    
    tax_rate = st.session_state.get("tax_rate", 0)
    tax_amount = round(subtotal * tax_rate / 100)
    grand_total = subtotal + tax_amount
    
    existing_orders = load_orders_from_db()
    next_order_id = 1 if not existing_orders else max(o["order_id"] for o in existing_orders) + 1
    
    order = {
        "order_id": next_order_id,
        "date": order_date,
        "time": order_time.strftime("%I:%M %p"),
        "items": items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "grand_total": grand_total
    }
    
    st.session_state.daily_orders = load_orders_from_db()
    save_order_to_db(order)
    st.session_state.last_order = order


# App Header
current_time = get_pakistan_time()
st.markdown(f"# 🍲 {RESTAURANT_NAME}")
st.caption(RESTAURANT_TAGLINE)
st.caption(f"🕐 Pakistan Time: {current_time.strftime('%d-%m-%Y %I:%M %p')}")

st.components.v1.html(f"""
    <div style="text-align: right; font-size: 16px; color: #666; padding: 5px;">
        <span id="live-clock"></span>
    </div>
    <script>
        function updateClock() {{
            const now = new Date();
            const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
            const pakistan = new Date(utc + (5 * 3600000));
            const options = {{ 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                hour12: true 
            }};
            document.getElementById('live-clock').innerHTML = '🕐 ' + pakistan.toLocaleString('en-GB', options);
        }}
        updateClock();
        setInterval(updateClock, 1000);
    </script>
""", height=40)

st.divider()

# Navigation
page = st.sidebar.selectbox("📌 Navigation", ["📋 Take Order", "📊 Sales Report", "📦 Inventory"])

if page == "📋 Take Order":
    menu_col, cart_col = st.columns([2, 1])

    with menu_col:
        st.subheader("📋 Menu")
        tabs = st.tabs(list(MENU.keys()))
        for tab, category in zip(tabs, MENU.keys()):
            with tab:
                for item, price in MENU[category].items():
                    c1, c2, c3, c4, c5 = st.columns([2, 1, 0.5, 0.5, 0.5])
                    c1.write(f"**{item}**")
                    c2.write(f"Rs. {price}")
                    
                    qty_key = f"qty_{category}_{item}"
                    if qty_key not in st.session_state:
                        st.session_state[qty_key] = 0
                    
                    if c3.button("➖", key=f"minus_{category}_{item}"):
                        if st.session_state[qty_key] > 0:
                            st.session_state[qty_key] -= 1
                            if item in st.session_state.cart:
                                decrease_qty(item)
                                st.session_state[qty_key] = st.session_state.cart.get(item, {}).get("qty", 0)
                        st.rerun()
                    
                    c4.markdown(f"<div style='text-align: center; padding: 5px; font-weight: bold;'>{st.session_state[qty_key]}</div>", unsafe_allow_html=True)
                    
                    if c5.button("➕", key=f"plus_{category}_{item}"):
                        st.session_state[qty_key] += 1
                        add_to_cart(item, price, 1)
                        st.rerun()

    with cart_col:
        st.subheader("🧾 Current Order")

        if not st.session_state.cart:
            st.info("No items added yet.")
        else:
            total = 0
            for item, data in list(st.session_state.cart.items()):
                qty = data["qty"]
                price = data["price"]
                line_total = qty * price
                total += line_total

                c1, c2, c3, c4, c5 = st.columns([2, 1, 0.4, 0.4, 0.4])
                c1.write(f"**{item}**")
                c2.write(f"Rs. {line_total}")
                
                if c3.button("➖", key=f"cart_minus_{item}"):
                    decrease_qty(item)
                    for category in MENU:
                        if item in MENU[category]:
                            qty_key = f"qty_{category}_{item}"
                            if qty_key in st.session_state:
                                st.session_state[qty_key] = st.session_state.cart.get(item, {}).get("qty", 0)
                    st.rerun()
                
                c4.markdown(f"<div style='text-align: center; font-size: 14px;'>{qty}</div>", unsafe_allow_html=True)
                
                if c5.button("➕", key=f"cart_plus_{item}"):
                    increase_qty(item, price)
                    for category in MENU:
                        if item in MENU[category]:
                            qty_key = f"qty_{category}_{item}"
                            if qty_key in st.session_state:
                                st.session_state[qty_key] = st.session_state.cart.get(item, {}).get("qty", 0)
                    st.rerun()

            st.divider()
            
            tax_rate = st.number_input("Tax / Service %", min_value=0, max_value=30, value=0, step=1)
            st.session_state["tax_rate"] = tax_rate
            tax_amount = round(total * tax_rate / 100)
            grand_total = total + tax_amount

            st.write(f"Subtotal: **Rs. {total}**")
            st.write(f"Tax/Service ({tax_rate}%): **Rs. {tax_amount}**")
            st.markdown(f"### Grand Total: Rs. {grand_total}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Place Order", use_container_width=True):
                    save_order_to_history()
                    st.session_state.order_placed = True
                    st.success(f"✅ Order placed successfully! Grand Total: Rs. {grand_total}")
                    clear_cart()
                    for key in list(st.session_state.keys()):
                        if key.startswith("qty_"):
                            st.session_state[key] = 0
                    st.rerun()
            with col_b:
                if st.button("🗑️ Clear Order", use_container_width=True):
                    clear_cart()
                    for key in list(st.session_state.keys()):
                        if key.startswith("qty_"):
                            st.session_state[key] = 0
                    st.rerun()

    if st.session_state.last_order:
        st.divider()
        st.subheader("🖨️ Bill / Receipt")
        
        order = st.session_state.last_order
        order_time_str = f"{order['date']} {order['time']}"
        
        receipt_lines = []
        receipt_lines.append("=" * 40)
        receipt_lines.append(RESTAURANT_NAME.center(40))
        receipt_lines.append(RESTAURANT_TAGLINE.center(40))
        receipt_lines.append("=" * 40)
        receipt_lines.append(f"Date: {order_time_str} (PKT)")
        receipt_lines.append(f"Order #: {order['order_id']}")
        receipt_lines.append("-" * 40)
        receipt_lines.append(f"{'Item':<20}{'Qty':>6}{'Amt':>14}")
        receipt_lines.append("-" * 40)
        for item in order["items"]:
            name = item["item"]
            qty = item["qty"]
            line_total = item["total"]
            receipt_lines.append(f"{name[:20]:<20}{qty:>6}{line_total:>14}")
        receipt_lines.append("-" * 40)
        receipt_lines.append(f"{'Subtotal':<26}{order['subtotal']:>14}")
        receipt_lines.append(f"{'Tax/Service':<26}{order['tax_amount']:>14}")
        receipt_lines.append("-" * 40)
        receipt_lines.append(f"{'TOTAL':<26}{order['grand_total']:>14}")
        receipt_lines.append("=" * 40)
        receipt_lines.append("Thank you for your order!".center(40))
        receipt_lines.append("=" * 40)

        receipt_text = "\n".join(receipt_lines)
        st.code(receipt_text, language=None)

        col_bill1, col_bill2 = st.columns(2)
        with col_bill1:
            st.download_button(
                "⬇️ Download Receipt (.txt)",
                data=receipt_text,
                file_name=f"receipt_{order['order_id']}_{order['date'].replace('-', '')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_bill2:
            if st.button("📋 New Order", use_container_width=True):
                st.session_state.last_order = None
                st.rerun()

elif page == "📊 Sales Report":
    st.subheader("📊 Daily Sales Report")
    
    st.session_state.daily_orders = load_orders_from_db()
    
    if not st.session_state.daily_orders:
        st.info("No orders have been placed yet. Start taking orders to see sales data!")
    else:
        dates = list(set(order["date"] for order in st.session_state.daily_orders))
        dates.sort(reverse=True)
        
        col_date, col_delete = st.columns([3, 1])
        with col_date:
            selected_date = st.selectbox("Select Date", ["All Dates"] + dates)
        with col_delete:
            if not st.session_state.delete_all_confirm:
                if st.button("🗑️ Delete All Orders", use_container_width=True, type="secondary"):
                    st.session_state.delete_all_confirm = True
                    st.rerun()
            else:
                st.warning("⚠️ Are you sure? This cannot be undone!")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, Delete All", use_container_width=True, type="primary"):
                        delete_all_orders_from_db()
                        st.session_state.daily_orders = []
                        st.session_state.delete_all_confirm = False
                        st.success("All orders deleted successfully!")
                        st.rerun()
                with col_no:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.delete_all_confirm = False
                        st.rerun()
        
        if selected_date == "All Dates":
            filtered_orders = st.session_state.daily_orders
        else:
            filtered_orders = [order for order in st.session_state.daily_orders if order["date"] == selected_date]
        
        total_orders = len(filtered_orders)
        total_sales = sum(order["grand_total"] for order in filtered_orders)
        total_tax = sum(order["tax_amount"] for order in filtered_orders)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Orders", total_orders)
        col2.metric("Total Sales (Rs.)", f"{total_sales:,.2f}")
        col3.metric("Total Tax (Rs.)", f"{total_tax:,.2f}")
        
        st.divider()
        
        st.subheader("📦 Product-wise Breakdown")
        
        product_sales = {}
        for order in filtered_orders:
            for item in order["items"]:
                product_name = item["item"]
                if product_name not in product_sales:
                    product_sales[product_name] = {"qty": 0, "total": 0}
                product_sales[product_name]["qty"] += item["qty"]
                product_sales[product_name]["total"] += item["total"]
        
        if product_sales:
            sales_data = []
            for product, data in product_sales.items():
                sales_data.append({
                    "Product": product,
                    "Quantity Sold": data["qty"],
                    "Total Revenue (Rs.)": data["total"]
                })
            
            df_products = pd.DataFrame(sales_data)
            df_products = df_products.sort_values("Total Revenue (Rs.)", ascending=False)
            st.dataframe(df_products, use_container_width=True, hide_index=True)
            
            st.subheader("📊 Sales by Product")
            chart_data = pd.DataFrame({
                "Product": [d["Product"] for d in sales_data],
                "Revenue (Rs.)": [d["Total Revenue (Rs.)"] for d in sales_data]
            })
            st.bar_chart(chart_data.set_index("Product"))
        else:
            st.info("No product sales data available for selected date.")
        
        st.divider()
        
        st.subheader("📝 Order History")
        
        if not filtered_orders:
            st.info("No orders found for the selected date.")
        else:
            for order in filtered_orders:
                with st.expander(f"Order #{order['order_id']} - {order['date']} at {order['time']} - Rs. {order['grand_total']}"):
                    col_info, col_del = st.columns([4, 1])
                    
                    with col_info:
                        st.write(f"**Date:** {order['date']}")
                        st.write(f"**Time:** {order['time']} (PKT)")
                        st.write(f"**Items:**")
                        for item in order["items"]:
                            st.write(f"  • {item['item']} x{item['qty']} = Rs. {item['total']}")
                        st.write(f"**Subtotal:** Rs. {order['subtotal']}")
                        st.write(f"**Tax ({order['tax_rate']}%):** Rs. {order['tax_amount']}")
                        st.write(f"**Grand Total:** Rs. {order['grand_total']}")
                    
                    with col_del:
                        if st.session_state.delete_confirm != order['db_id']:
                            if st.button("🗑️ Delete", key=f"delete_{order['db_id']}", use_container_width=True):
                                st.session_state.delete_confirm = order['db_id']
                                st.rerun()
                        else:
                            st.warning("⚠️ Confirm delete?")
                            col_y, col_n = st.columns(2)
                            with col_y:
                                if st.button("✅", key=f"confirm_{order['db_id']}", use_container_width=True):
                                    delete_order_from_db(order['db_id'])
                                    st.session_state.daily_orders = load_orders_from_db()
                                    st.session_state.delete_confirm = None
                                    st.success(f"Order #{order['order_id']} deleted!")
                                    st.rerun()
                            with col_n:
                                if st.button("❌", key=f"cancel_{order['db_id']}", use_container_width=True):
                                    st.session_state.delete_confirm = None
                                    st.rerun()
        
        st.divider()
        if filtered_orders:
            if st.button("📥 Download Sales Report (CSV)", use_container_width=True):
                all_orders_data = []
                for order in filtered_orders:
                    for item in order["items"]:
                        all_orders_data.append({
                            "Order ID": order["order_id"],
                            "Date": order["date"],
                            "Time (PKT)": order["time"],
                            "Product": item["item"],
                            "Quantity": item["qty"],
                            "Price (Rs.)": item["price"],
                            "Line Total (Rs.)": item["total"],
                            "Tax Rate (%)": order["tax_rate"],
                            "Tax Amount (Rs.)": order["tax_amount"],
                            "Grand Total (Rs.)": order["grand_total"]
                        })
                
                df_export = pd.DataFrame(all_orders_data)
                csv = df_export.to_csv(index=False)
                
                st.download_button(
                    "Click to Download CSV",
                    csv,
                    f"sales_report_{selected_date.replace('-', '')}.csv",
                    "text/csv",
                    key="download_csv",
                    use_container_width=True
                )

elif page == "📦 Inventory":
    st.subheader("📦 Inventory Management")
    
    # Refresh inventory data
    st.session_state.inventory = load_inventory()
    
    # Tabs for viewing and adding inventory
    inv_tab1, inv_tab2 = st.tabs(["📋 View Inventory", "➕ Add Item"])
    
    with inv_tab1:
        if not st.session_state.inventory:
            st.info("No items in inventory. Add some items to get started!")
        else:
            # Category filter
            categories = list(set(item["category"] for item in st.session_state.inventory))
            categories.sort()
            selected_category = st.selectbox("Filter by Category", ["All Categories"] + categories)
            
            if selected_category == "All Categories":
                filtered_inventory = st.session_state.inventory
            else:
                filtered_inventory = [item for item in st.session_state.inventory if item["category"] == selected_category]
            
            # Low stock alert
            low_stock_items = [item for item in filtered_inventory if item["quantity"] <= item["min_stock"]]
            if low_stock_items:
                st.warning(f"⚠️ {len(low_stock_items)} item(s) are low on stock and need reordering!")
            
            # Display inventory as cards
            for item in filtered_inventory:
                stock_status = "🔴" if item["quantity"] <= item["min_stock"] else "🟢"
                
                with st.expander(f"{stock_status} {item['item_name']} - {item['quantity']} {item['unit']} ({item['category']})"):
                    if st.session_state.editing_item == item['id']:
                        # Edit mode
                        st.markdown("**Edit Item**")
                        edit_name = st.text_input("Item Name", value=item['item_name'], key=f"edit_name_{item['id']}")
                        edit_category = st.text_input("Category", value=item['category'], key=f"edit_cat_{item['id']}")
                        
                        col_qty, col_unit = st.columns(2)
                        with col_qty:
                            edit_quantity = st.number_input("Quantity", value=float(item['quantity']), step=0.1, key=f"edit_qty_{item['id']}")
                        with col_unit:
                            edit_unit = st.text_input("Unit", value=item['unit'], key=f"edit_unit_{item['id']}")
                        
                        col_min, col_cost = st.columns(2)
                        with col_min:
                            edit_min_stock = st.number_input("Min Stock Level", value=float(item['min_stock']), step=0.1, key=f"edit_min_{item['id']}")
                        with col_cost:
                            edit_cost = st.number_input("Cost per Unit (Rs.)", value=float(item['cost_per_unit']), step=0.01, key=f"edit_cost_{item['id']}")
                        
                        edit_notes = st.text_area("Notes", value=item['notes'], key=f"edit_notes_{item['id']}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 Save", key=f"save_{item['id']}", use_container_width=True):
                                update_inventory_item(item['id'], edit_name, edit_category, edit_quantity, edit_unit, edit_min_stock, edit_cost, edit_notes)
                                st.session_state.inventory = load_inventory()
                                st.session_state.editing_item = None
                                st.success("Item updated!")
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_edit_{item['id']}", use_container_width=True):
                                st.session_state.editing_item = None
                                st.rerun()
                    else:
                        # View mode
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            st.write(f"**Category:** {item['category']}")
                            st.write(f"**Quantity:** {item['quantity']} {item['unit']}")
                            st.write(f"**Min Stock Level:** {item['min_stock']} {item['unit']}")
                            st.write(f"**Cost per Unit:** Rs. {item['cost_per_unit']:.2f}")
                            st.write(f"**Total Value:** Rs. {item['quantity'] * item['cost_per_unit']:.2f}")
                            st.write(f"**Last Updated:** {item['last_updated']}")
                            if item['notes']:
                                st.write(f"**Notes:** {item['notes']}")
                        
                        with col_actions:
                            # Quick stock adjustment
                            st.write("**Quick Adjust:**")
                            col_add, col_sub = st.columns(2)
                            with col_add:
                                if st.button("➕", key=f"qadd_{item['id']}"):
                                    new_qty = item['quantity'] + 1
                                    update_inventory_quantity(item['id'], new_qty)
                                    st.session_state.inventory = load_inventory()
                                    st.rerun()
                            with col_sub:
                                if st.button("➖", key=f"qsub_{item['id']}"):
                                    new_qty = max(0, item['quantity'] - 1)
                                    update_inventory_quantity(item['id'], new_qty)
                                    st.session_state.inventory = load_inventory()
                                    st.rerun()
                            
                            st.divider()
                            
                            if st.button("✏️ Edit", key=f"edit_{item['id']}", use_container_width=True):
                                st.session_state.editing_item = item['id']
                                st.rerun()
                            
                            if st.session_state.inv_delete_confirm != item['id']:
                                if st.button("🗑️ Delete", key=f"inv_del_{item['id']}", use_container_width=True):
                                    st.session_state.inv_delete_confirm = item['id']
                                    st.rerun()
                            else:
                                st.warning("Confirm?")
                                col_y, col_n = st.columns(2)
                                with col_y:
                                    if st.button("✅", key=f"inv_confirm_{item['id']}", use_container_width=True):
                                        delete_inventory_item(item['id'])
                                        st.session_state.inventory = load_inventory()
                                        st.session_state.inv_delete_confirm = None
                                        st.success("Item deleted!")
                                        st.rerun()
                                with col_n:
                                    if st.button("❌", key=f"inv_cancel_{item['id']}", use_container_width=True):
                                        st.session_state.inv_delete_confirm = None
                                        st.rerun()
            
            # Inventory summary
            st.divider()
            st.subheader("📊 Inventory Summary")
            
            total_items = len(filtered_inventory)
            total_value = sum(item['quantity'] * item['cost_per_unit'] for item in filtered_inventory)
            low_stock_count = len([item for item in filtered_inventory if item['quantity'] <= item['min_stock']])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Items", total_items)
            col2.metric("Total Inventory Value", f"Rs. {total_value:,.2f}")
            col3.metric("Low Stock Items", low_stock_count, delta=f"{low_stock_count}" if low_stock_count > 0 else "0")
            
            # Export inventory
            if st.button("📥 Download Inventory (CSV)", use_container_width=True):
                inv_data = []
                for item in filtered_inventory:
                    inv_data.append({
                        "Item Name": item['item_name'],
                        "Category": item['category'],
                        "Quantity": item['quantity'],
                        "Unit": item['unit'],
                        "Min Stock": item['min_stock'],
                        "Cost per Unit": item['cost_per_unit'],
                        "Total Value": item['quantity'] * item['cost_per_unit'],
                        "Status": "Low Stock" if item['quantity'] <= item['min_stock'] else "In Stock",
                        "Last Updated": item['last_updated'],
                        "Notes": item['notes']
                    })
                
                df_inv = pd.DataFrame(inv_data)
                csv_inv = df_inv.to_csv(index=False)
                
                st.download_button(
                    "Click to Download",
                    csv_inv,
                    f"inventory_{get_pakistan_time().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    key="download_inv_csv",
                    use_container_width=True
                )
    
    with inv_tab2:
        st.subheader("Add New Inventory Item")
        
        with st.form("add_inventory_form"):
            new_name = st.text_input("Item Name*", placeholder="e.g., Chicken Breast")
            new_category = st.text_input("Category*", placeholder="e.g., Meat, Vegetables, Spices")
            
            col_q, col_u = st.columns(2)
            with col_q:
                new_quantity = st.number_input("Initial Quantity*", min_value=0.0, step=0.1)
            with col_u:
                new_unit = st.selectbox("Unit*", ["kg", "g", "litre", "ml", "pieces", "packets", "dozen", "bottles", "cans"])
            
            col_m, col_c = st.columns(2)
            with col_m:
                new_min_stock = st.number_input("Minimum Stock Level", min_value=0.0, step=0.1, value=1.0)
            with col_c:
                new_cost = st.number_input("Cost per Unit (Rs.)", min_value=0.0, step=0.
