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

# Default menu structure
DEFAULT_MENU = {
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
BILLING_PASSWORD = "112233"  # Password for billing authorization

# Pakistan timezone offset (UTC+5)
PAKISTAN_OFFSET = timedelta(hours=5)

def get_pakistan_time():
    """Get current time in Pakistan (UTC+5)"""
    return datetime.utcnow() + PAKISTAN_OFFSET

# Initialize database
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    
    # Orders table - Added customer_name field
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            date TEXT,
            time TEXT,
            customer_name TEXT,
            items TEXT,
            subtotal REAL,
            tax_rate REAL,
            tax_amount REAL,
            grand_total REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Menu/Inventory table
    c.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, item_name)
        )
    ''')
    
    # Initialize default menu if empty
    c.execute('SELECT COUNT(*) FROM menu')
    if c.fetchone()[0] == 0:
        for category, items in DEFAULT_MENU.items():
            for item_name, price in items.items():
                c.execute('''
                    INSERT INTO menu (category, item_name, price)
                    VALUES (?, ?, ?)
                ''', (category, item_name, price))
    
    # Add customer_name column if it doesn't exist (for database upgrades)
    try:
        c.execute('ALTER TABLE orders ADD COLUMN customer_name TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

def load_menu_from_db():
    """Load menu from database"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT category, item_name, price, active FROM menu ORDER BY category, item_name')
    rows = c.fetchall()
    conn.close()
    
    menu = {}
    for row in rows:
        category, item_name, price, active = row
        if active:  # Only load active items
            if category not in menu:
                menu[category] = {}
            menu[category][item_name] = price
    return menu

def add_menu_item(category, item_name, price):
    """Add a new item to menu"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO menu (category, item_name, price)
            VALUES (?, ?, ?)
        ''', (category, item_name, price))
        conn.commit()
        return True, "Item added successfully!"
    except sqlite3.IntegrityError:
        return False, "Item already exists in this category!"
    finally:
        conn.close()

def update_menu_item(category, item_name, new_price, new_name=None):
    """Update an existing menu item's price or name"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    try:
        if new_name and new_name != item_name:
            # Update both name and price
            c.execute('''
                UPDATE menu 
                SET item_name = ?, price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category = ? AND item_name = ?
            ''', (new_name, new_price, category, item_name))
        else:
            # Update only price
            c.execute('''
                UPDATE menu 
                SET price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category = ? AND item_name = ?
            ''', (new_price, category, item_name))
        conn.commit()
        return True, "Item updated successfully!"
    except Exception as e:
        return False, f"Error updating item: {str(e)}"
    finally:
        conn.close()

def toggle_menu_item(category, item_name, active):
    """Activate or deactivate a menu item"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''
        UPDATE menu 
        SET active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE category = ? AND item_name = ?
    ''', (active, category, item_name))
    conn.commit()
    conn.close()

def get_all_categories():
    """Get all unique categories"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM menu ORDER BY category')
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories

def get_all_menu_items():
    """Get all menu items (including inactive)"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT category, item_name, price, active FROM menu ORDER BY category, item_name')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_menu_item(category, item_name):
    """Delete a menu item completely"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('DELETE FROM menu WHERE category = ? AND item_name = ?', (category, item_name))
    conn.commit()
    conn.close()

def save_order_to_db(order):
    """Save order to SQLite database"""
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO orders (order_id, date, time, customer_name, items, subtotal, tax_rate, tax_amount, grand_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order["order_id"],
        order["date"],
        order["time"],
        order["customer_name"],
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
    c.execute('SELECT id, order_id, date, time, customer_name, items, subtotal, tax_rate, tax_amount, grand_total FROM orders ORDER BY id')
    rows = c.fetchall()
    conn.close()
    
    orders = []
    for row in rows:
        orders.append({
            "db_id": row[0],
            "order_id": row[1],
            "date": row[2],
            "time": row[3],
            "customer_name": row[4] if row[4] else "",
            "items": json.loads(row[5]),
            "subtotal": row[6],
            "tax_rate": row[7],
            "tax_amount": row[8],
            "grand_total": row[9]
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

# Initialize database
init_db()

# Load current menu
MENU = load_menu_from_db()

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

if "inventory_editing" not in st.session_state:
    st.session_state.inventory_editing = None

if "billing_authorized" not in st.session_state:
    st.session_state.billing_authorized = False

if "customer_name" not in st.session_state:
    st.session_state.customer_name = ""

if "show_billing_dialog" not in st.session_state:
    st.session_state.show_billing_dialog = False


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
    st.session_state.billing_authorized = False
    st.session_state.customer_name = ""
    st.session_state.show_billing_dialog = False


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
        "customer_name": st.session_state.customer_name,
        "items": items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "grand_total": grand_total
    }
    
    st.session_state.daily_orders = load_orders_from_db()
    save_order_to_db(order)
    st.session_state.last_order = order
    st.session_state.billing_authorized = False
    st.session_state.show_billing_dialog = False


# App Header
current_time = get_pakistan_time()
st.markdown(f"# 🍲 {RESTAURANT_NAME}")
st.caption(RESTAURANT_TAGLINE)
st.caption(f"🕐 Pakistan Time: {current_time.strftime('%d-%m-%Y %I:%M %p')}")

# Show live clock
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
page = st.sidebar.selectbox("📌 Navigation", ["📋 Take Order", "📊 Sales Report", "📦 Inventory Management"])

if page == "📋 Take Order":
    # Reload menu to get latest changes
    MENU = load_menu_from_db()
    
    menu_col, cart_col = st.columns([2, 1])

    with menu_col:
        st.subheader("📋 Menu")
        
        if not MENU:
            st.warning("No menu items available. Please add items in Inventory Management.")
        else:
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
            
            # Customer Name Input
            st.session_state.customer_name = st.text_input(
                "👤 Customer Name",
                value=st.session_state.customer_name,
                placeholder="Enter customer name before billing..."
            )
            
            tax_rate = st.number_input("Tax / Service %", min_value=0, max_value=30, value=0, step=1)
            st.session_state["tax_rate"] = tax_rate
            tax_amount = round(total * tax_rate / 100)
            grand_total = total + tax_amount

            st.write(f"Subtotal: **Rs. {total}**")
            st.write(f"Tax/Service ({tax_rate}%): **Rs. {tax_amount}**")
            st.markdown(f"### Grand Total: Rs. {grand_total}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔐 Process Billing", use_container_width=True, type="primary"):
                    # Check if customer name is provided
                    if not st.session_state.customer_name.strip():
                        st.error("⚠️ Please enter customer name before billing!")
                    else:
                        st.session_state.show_billing_dialog = True
                        st.rerun()
            
            with col_b:
                if st.button("🗑️ Clear Order", use_container_width=True):
                    clear_cart()
                    for key in list(st.session_state.keys()):
                        if key.startswith("qty_"):
                            st.session_state[key] = 0
                    st.rerun()
            
            # Billing Authorization Dialog
            if st.session_state.show_billing_dialog:
                st.divider()
                st.warning("🔐 **Billing Authorization Required**")
                st.info(f"👤 Customer: **{st.session_state.customer_name}**")
                st.write(f"Total Amount: **Rs. {grand_total}**")
                
                password = st.text_input(
                    "Enter Billing Password",
                    type="password",
                    placeholder="Enter password to authorize billing...",
                    key="billing_password"
                )
                
                col_pwd1, col_pwd2 = st.columns(2)
                with col_pwd1:
                    if st.button("✅ Authorize & Place Order", use_container_width=True, type="primary"):
                        if password == BILLING_PASSWORD:
                            save_order_to_history()
                            st.session_state.order_placed = True
                            st.success(f"✅ Order placed successfully for {st.session_state.customer_name}! Grand Total: Rs. {grand_total}")
                            customer_name = st.session_state.customer_name
                            clear_cart()
                            for key in list(st.session_state.keys()):
                                if key.startswith("qty_"):
                                    st.session_state[key] = 0
                            st.rerun()
                        else:
                            st.error("❌ Invalid password! Please try again.")
                
                with col_pwd2:
                    if st.button("❌ Cancel Billing", use_container_width=True):
                        st.session_state.show_billing_dialog = False
                        st.rerun()

    # Show bill
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
        receipt_lines.append(f"Customer: {order['customer_name']}")
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
                customer_display = f" - {order.get('customer_name', '')}" if order.get('customer_name') else ""
                with st.expander(f"Order #{order['order_id']} - {order['date']} at {order['time']}{customer_display} - Rs. {order['grand_total']}"):
                    col_info, col_del = st.columns([4, 1])
                    
                    with col_info:
                        st.write(f"**Date:** {order['date']}")
                        st.write(f"**Time:** {order['time']} (PKT)")
                        if order.get('customer_name'):
                            st.write(f"**Customer:** {order['customer_name']}")
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
                            "Customer": order.get("customer_name", ""),
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

elif page == "📦 Inventory Management":
    st.subheader("📦 Inventory & Menu Management")
    
    # Tabs for different inventory operations
    inv_tab1, inv_tab2, inv_tab3 = st.tabs(["📋 Current Menu", "➕ Add New Product", "✏️ Edit Products"])
    
    with inv_tab1:
        st.write("### Current Menu Items")
        
        all_items = get_all_menu_items()
        
        if not all_items:
            st.info("No items in menu. Add some products!")
        else:
            # Group by category
            categories = {}
            for item in all_items:
                category, item_name, price, active = item
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    "name": item_name,
                    "price": price,
                    "active": active
                })
            
            for category, items in categories.items():
                with st.expander(f"📁 {category} ({len(items)} items)", expanded=True):
                    # Create table
                    data = []
                    for item in items:
                        status = "✅ Active" if item["active"] else "❌ Inactive"
                        data.append({
                            "Item": item["name"],
                            "Price (Rs.)": item["price"],
                            "Status": status
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
    
    with inv_tab2:
        st.write("### ➕ Add New Product")
        
        # Get existing categories
        existing_categories = get_all_categories()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Option to select existing category or create new
            category_option = st.radio(
                "Category",
                ["Select Existing", "Create New"],
                horizontal=True
            )
            
            if category_option == "Select Existing":
                if existing_categories:
                    category = st.selectbox("Choose Category", existing_categories)
                else:
                    st.warning("No categories exist. Please create a new one.")
                    category = st.text_input("New Category Name")
            else:
                category = st.text_input("New Category Name", placeholder="e.g., Beverages, Desserts")
        
        with col2:
            item_name = st.text_input("Product Name", placeholder="e.g., Chicken Biryani")
            price = st.number_input("Price (Rs.)", min_value=0, step=10, value=100)
        
        if st.button("➕ Add Product", use_container_width=True, type="primary"):
            if not category or not item_name:
                st.error("Please fill in all fields!")
            elif price <= 0:
                st.error("Price must be greater than 0!")
            else:
                success, message = add_menu_item(category, item_name, price)
                if success:
                    st.success(message)
                    # Reload menu
                    MENU = load_menu_from_db()
                else:
                    st.error(message)
    
    with inv_tab3:
        st.write("### ✏️ Edit or Delete Products")
        
        all_items = get_all_menu_items()
        
        if not all_items:
            st.info("No items to edit.")
        else:
            # Select item to edit
            item_options = {}
            for item in all_items:
                category, item_name, price, active = item
                key = f"{category} > {item_name}"
                item_options[key] = {
                    "category": category,
                    "name": item_name,
                    "price": price,
                    "active": active
                }
            
            selected_item_key = st.selectbox(
                "Select Product to Edit",
                list(item_options.keys())
            )
            
            if selected_item_key:
                selected = item_options[selected_item_key]
                
                st.divider()
                st.write(f"**Current Details:**")
                st.write(f"- Category: **{selected['category']}**")
                st.write(f"- Name: **{selected['name']}**")
                st.write(f"- Price: **Rs. {selected['price']}**")
                st.write(f"- Status: **{'Active' if selected['active'] else 'Inactive'}**")
                
                st.divider()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("New Name", value=selected['name'])
                    new_price = st.number_input("New Price (Rs.)", 
                                               min_value=0, 
                                               step=10, 
                                               value=int(selected['price']))
                
                with col2:
                    st.write("")  # Spacing
                    st.write("")
                    # Toggle active status
                    new_status = st.checkbox("Active (visible in menu)", value=bool(selected['active']))
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                
                with col_btn1:
                    if st.button("💾 Update Product", use_container_width=True, type="primary"):
                        if new_price <= 0:
                            st.error("Price must be greater than 0!")
                        else:
                            success, message = update_menu_item(
                                selected['category'],
                                selected['name'],
                                new_price,
                                new_name if new_name != selected['name'] else None
                            )
                            if success:
                                # Update active status if changed
                                if new_status != selected['active']:
                                    toggle_menu_item(selected['category'], new_name, 1 if new_status else 0)
                                st.success(message)
                                MENU = load_menu_from_db()
                                st.rerun()
                            else:
                                st.error(message)
                
                with col_btn2:
                    if new_status != selected['active']:
                        action = "Activate
