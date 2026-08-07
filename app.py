"""
Affan's Kitchen - Professional POS System
----------------------------------------
Advanced restaurant POS with daily sales tracking, inventory management,
and professional receipt generation.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import json
import pandas as pd
import plotly.express as px
import os
from pathlib import Path

st.set_page_config(
    page_title="Affan's Kitchen - POS", 
    page_icon="🍲", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
RESTAURANT_NAME = "Affan's Kitchen"
RESTAURANT_TAGLINE = "Tradition in Every Bite"
TAX_RATE = 5  # Default tax rate

# Menu Configuration
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

# Data persistence functions
def get_data_dir():
    """Create and return data directory path"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir

def load_json(filename):
    """Load data from JSON file"""
    data_dir = get_data_dir()
    file_path = data_dir / filename
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(filename, data):
    """Save data to JSON file"""
    data_dir = get_data_dir()
    file_path = data_dir / filename
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize session state with persistence
def init_session_state():
    defaults = {
        "cart": {},
        "order_placed": False,
        "order_history": load_json("orders.json"),
        "daily_sales": load_json("daily_sales.json"),
        "inventory": load_json("inventory.json"),
        "current_order_number": 1,
        "tax_rate": TAX_RATE,
        "discount": 0,
        "customer_name": "",
        "customer_phone": "",
        "order_type": "Dine In",
        "data_loaded": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize inventory if empty
    if not st.session_state.inventory:
        for category, items in MENU.items():
            for item in items:
                st.session_state.inventory[item] = {
                    "stock": 100,
                    "low_stock_threshold": 10,
                    "cost_price": 0,
                }
        save_json("inventory.json", st.session_state.inventory)
    
    # Set current order number from history
    if st.session_state.order_history:
        max_order = 0
        for order in st.session_state.order_history:
            try:
                num = int(order['order_number'].split('-')[-1])
                if num > max_order:
                    max_order = num
            except:
                pass
        st.session_state.current_order_number = max_order + 1
    
    st.session_state.data_loaded = True

init_session_state()

# Core Functions
def add_to_cart(item, price, qty=1):
    if qty <= 0:
        return False
    # Check inventory
    if st.session_state.inventory[item]["stock"] < qty:
        st.error(f"Insufficient stock for {item}. Available: {st.session_state.inventory[item]['stock']}")
        return False
    
    if item in st.session_state.cart:
        st.session_state.cart[item]["qty"] += qty
    else:
        st.session_state.cart[item] = {"qty": qty, "price": price}
    
    # Update inventory
    st.session_state.inventory[item]["stock"] -= qty
    save_json("inventory.json", st.session_state.inventory)
    st.session_state.order_placed = False
    return True

def remove_from_cart(item):
    if item in st.session_state.cart:
        # Return to inventory
        qty = st.session_state.cart[item]["qty"]
        st.session_state.inventory[item]["stock"] += qty
        save_json("inventory.json", st.session_state.inventory)
        del st.session_state.cart[item]
    st.session_state.order_placed = False

def clear_cart():
    # Return all items to inventory
    for item, data in st.session_state.cart.items():
        st.session_state.inventory[item]["stock"] += data["qty"]
    save_json("inventory.json", st.session_state.inventory)
    st.session_state.cart = {}
    st.session_state.order_placed = False
    # Clear quantity inputs
    for key in list(st.session_state.keys()):
        if key.startswith("qty_"):
            del st.session_state[key]

def generate_receipt():
    order_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    order_number = f"ORD-{datetime.now().strftime('%y%m%d')}-{st.session_state.current_order_number:04d}"
    
    total = sum(d["qty"] * d["price"] for d in st.session_state.cart.values())
    tax_rate = st.session_state.tax_rate
    tax_amount = round(total * tax_rate / 100)
    discount = st.session_state.discount
    grand_total = total + tax_amount - discount
    
    receipt_lines = []
    receipt_lines.append("=" * 40)
    receipt_lines.append(RESTAURANT_NAME.center(40))
    receipt_lines.append(RESTAURANT_TAGLINE.center(40))
    receipt_lines.append("=" * 40)
    receipt_lines.append(f"Order #: {order_number}")
    receipt_lines.append(f"Date: {order_time}")
    receipt_lines.append(f"Customer: {st.session_state.customer_name or 'Walk-in'}")
    receipt_lines.append(f"Type: {st.session_state.order_type}")
    receipt_lines.append("=" * 40)
    receipt_lines.append(f"{'Item':<20}{'Qty':>6}{'Price':>10}{'Total':>10}")
    receipt_lines.append("-" * 40)
    
    for item, data in st.session_state.cart.items():
        qty = data["qty"]
        price = data["price"]
        line_total = qty * price
        receipt_lines.append(f"{item[:20]:<20}{qty:>6}{price:>10}{line_total:>10}")
    
    receipt_lines.append("=" * 40)
    receipt_lines.append(f"{'Subtotal':<36}{total:>10}")
    receipt_lines.append(f"{'Tax/Service (' + str(tax_rate) + '%)':<36}{tax_amount:>10}")
    if discount > 0:
        receipt_lines.append(f"{'Discount':<36}{'-' + str(discount):>10}")
    receipt_lines.append(f"{'TOTAL':<36}{grand_total:>10}")
    receipt_lines.append("=" * 40)
    receipt_lines.append("Thank you for dining with us!".center(40))
    receipt_lines.append("Please visit again!".center(40))
    receipt_lines.append("=" * 40)
    
    return "\n".join(receipt_lines), order_number, order_time, grand_total

def save_order_to_history(receipt_text, order_number, order_time, grand_total):
    order_data = {
        "order_number": order_number,
        "date": order_time,
        "customer": st.session_state.customer_name or "Walk-in",
        "order_type": st.session_state.order_type,
        "items": st.session_state.cart.copy(),
        "total": grand_total,
        "receipt": receipt_text,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.order_history.append(order_data)
    save_json("orders.json", st.session_state.order_history)
    st.session_state.current_order_number += 1
    
    # Update daily sales
    today = date.today().isoformat()
    if today not in st.session_state.daily_sales:
        st.session_state.daily_sales[today] = {
            "orders": [],
            "total_sales": 0,
            "total_items": 0,
            "categories": {}
        }
    
    daily = st.session_state.daily_sales[today]
    daily["orders"].append(order_number)
    daily["total_sales"] += grand_total
    daily["total_items"] += sum(d["qty"] for d in st.session_state.cart.values())
    
    # Update category sales
    for item, data in st.session_state.cart.items():
        category = next((cat for cat, items in MENU.items() if item in items), "Other")
        if category not in daily["categories"]:
            daily["categories"][category] = {"count": 0, "revenue": 0}
        daily["categories"][category]["count"] += data["qty"]
        daily["categories"][category]["revenue"] += data["qty"] * data["price"]
    
    save_json("daily_sales.json", st.session_state.daily_sales)

# UI Layout
# Header
st.title(f"🍲 {RESTAURANT_NAME}")
st.caption(RESTAURANT_TAGLINE)

# Quick stats
col1, col2, col3 = st.columns(3)
today = date.today().isoformat()
if today in st.session_state.daily_sales:
    daily_total = st.session_state.daily_sales[today]["total_sales"]
    daily_items = st.session_state.daily_sales[today]["total_items"]
    orders_today = len(st.session_state.daily_sales[today]["orders"])
    
    with col1:
        st.metric("Today's Sales", f"Rs. {daily_total:,}", f"{daily_items} items")
    with col2:
        st.metric("Orders Today", orders_today)
    with col3:
        avg_order = daily_total / orders_today if orders_today > 0 else 0
        st.metric("Avg. Order Value", f"Rs. {avg_order:,.0f}")

st.divider()

# Main Layout
menu_col, cart_col, analytics_col = st.tabs(["📋 Menu & Order", "🧾 Cart & Checkout", "📊 Analytics"])

with menu_col:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Menu")
        
        # Customer Info
        with st.expander("👤 Customer Details", expanded=False):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.session_state.customer_name = st.text_input("Customer Name", value=st.session_state.customer_name)
            with col_b:
                st.session_state.customer_phone = st.text_input("Phone", value=st.session_state.customer_phone)
            with col_c:
                st.session_state.order_type = st.selectbox("Order Type", ["Dine In", "Takeaway", "Delivery"])
        
        # Menu Tabs - SIMPLIFIED VERSION WITHOUT CALLBACK ISSUES
        tabs = st.tabs(list(MENU.keys()))
        for tab, category in zip(tabs, MENU.keys()):
            with tab:
                for item, price in MENU[category].items():
                    col_item, col_price, col_qty = st.columns([3, 1, 2])
                    
                    with col_item:
                        # Show stock status
                        stock = st.session_state.inventory[item]["stock"]
                        stock_emoji = "🟢" if stock > 10 else "🟡" if stock > 5 else "🔴"
                        st.write(f"**{item}** {stock_emoji}")
                    
                    with col_price:
                        st.write(f"Rs. {price}")
                    
                    with col_qty:
                        qty_key = f"qty_{category}_{item}"
                        
                        # Initialize qty_key if it doesn't exist
                        if qty_key not in st.session_state:
                            st.session_state[qty_key] = 0
                        
                        # Use a container for the quantity controls
                        qty_container = st.container()
                        with qty_container:
                            # Three columns for - | number | +
                            c1, c2, c3 = st.columns([1, 2, 1])
                            
                            # Minus button
                            if c1.button("−", key=f"minus_{qty_key}", 
                                       disabled=st.session_state[qty_key] == 0,
                                       use_container_width=True):
                                if st.session_state[qty_key] > 0:
                                    st.session_state[qty_key] -= 1
                                    if st.session_state[qty_key] == 0:
                                        remove_from_cart(item)
                                    else:
                                        if item in st.session_state.cart:
                                            st.session_state.cart[item]["qty"] = st.session_state[qty_key]
                                    st.rerun()
                            
                            # Number input
                            c2.number_input("", key=qty_key, 
                                          min_value=0, 
                                          max_value=st.session_state.inventory[item]["stock"], 
                                          step=1, 
                                          label_visibility="collapsed")
                            
                            # Plus button
                            if c3.button("+", key=f"plus_{qty_key}", 
                                       disabled=st.session_state[qty_key] >= st.session_state.inventory[item]["stock"],
                                       use_container_width=True):
                                if st.session_state[qty_key] < st.session_state.inventory[item]["stock"]:
                                    st.session_state[qty_key] += 1
                                    add_to_cart(item, price, 1)
                                    st.rerun()

with cart_col:
    st.subheader("🧾 Current Order")
    
    if not st.session_state.cart:
        st.info("No items in cart. Add items from the menu.")
    else:
        # Cart Items
        total = 0
        total_items = 0
        for item, data in list(st.session_state.cart.items()):
            qty = data["qty"]
            price = data["price"]
            line_total = qty * price
            total += line_total
            total_items += qty
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(f"{item}")
            col2.write(f"x{qty}")
            col3.write(f"Rs. {line_total}")
            if col4.button("❌", key=f"remove_{item}"):
                remove_from_cart(item)
                st.rerun()
        
        st.divider()
        
        # Order Summary
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.tax_rate = st.number_input("Tax %", min_value=0, max_value=30, 
                                                       value=st.session_state.tax_rate, step=1)
        with col2:
            st.session_state.discount = st.number_input("Discount Rs.", min_value=0, 
                                                       value=st.session_state.discount, step=10)
        
        tax_amount = round(total * st.session_state.tax_rate / 100)
        grand_total = total + tax_amount - st.session_state.discount
        
        st.write(f"Items: **{total_items}**")
        st.write(f"Subtotal: **Rs. {total:,}**")
        st.write(f"Tax ({st.session_state.tax_rate}%): **Rs. {tax_amount:,}**")
        if st.session_state.discount > 0:
            st.write(f"Discount: **-Rs. {st.session_state.discount:,}**")
        st.markdown(f"### Grand Total: Rs. {grand_total:,}")
        
        # Action Buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Place Order", use_container_width=True):
                if st.session_state.cart:
                    st.session_state.order_placed = True
                    receipt_text, order_number, order_time, grand_total = generate_receipt()
                    save_order_to_history(receipt_text, order_number, order_time, grand_total)
                    st.success(f"Order {order_number} placed successfully!")
                    st.balloons()
                    # Clear cart after order
                    st.session_state.cart = {}
                    for key in list(st.session_state.keys()):
                        if key.startswith("qty_"):
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.warning("Cart is empty!")
        
        with col2:
            if st.button("🗑️ Clear Cart", use_container_width=True):
                clear_cart()
                st.rerun()
        
        with col3:
            if st.button("📝 Quick Order", use_container_width=True):
                sample_items = list(st.session_state.cart.keys())
                if not sample_items:
                    for category, items in MENU.items():
                        for item, price in list(items.items())[:2]:
                            add_to_cart(item, price, 1)
                    st.rerun()
    
    # Order History Preview
    with st.expander("📜 Recent Orders", expanded=False):
        if st.session_state.order_history:
            recent = st.session_state.order_history[-5:]
            for order in reversed(recent):
                st.caption(f"**{order['order_number']}** - {order['date']} - Rs. {order['total']:,}")
        else:
            st.info("No orders yet")

with analytics_col:
    st.subheader("📊 Daily Analytics")
    
    # Date selector
    col1, col2 = st.columns(2)
    with col1:
        view_date = st.date_input("Select Date", date.today())
    with col2:
        if st.button("Refresh Data"):
            st.rerun()
    
    date_str = view_date.isoformat()
    
    if date_str in st.session_state.daily_sales:
        daily = st.session_state.daily_sales[date_str]
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", f"Rs. {daily['total_sales']:,}")
        with col2:
            st.metric("Total Items", daily['total_items'])
        with col3:
            st.metric("Orders", len(daily['orders']))
        with col4:
            avg_order = daily['total_sales'] / len(daily['orders']) if daily['orders'] else 0
            st.metric("Avg. Order", f"Rs. {avg_order:,.0f}")
        
        st.divider()
        
        # Category Breakdown
        if daily['categories']:
            st.subheader("Category Performance")
            cat_data = []
            for cat, data in daily['categories'].items():
                cat_data.append({
                    "Category": cat,
                    "Items Sold": data['count'],
                    "Revenue": data['revenue']
                })
            
            df = pd.DataFrame(cat_data)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df, x='Category', y='Items Sold', title='Items by Category')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.pie(df, values='Revenue', names='Category', title='Revenue by Category')
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent Orders
        with st.expander("📋 Daily Orders Detail", expanded=False):
            for order_num in daily['orders']:
                for order in st.session_state.order_history:
                    if order['order_number'] == order_num:
                        st.caption(f"**{order['order_number']}** | {order['date']} | Rs. {order['total']:,}")
                        break
    else:
        st.info(f"No sales data available for {view_date.strftime('%B %d, %Y')}")
    
    # Overall Statistics
    with st.expander("📈 Overall Statistics", expanded=False):
        if st.session_state.order_history:
            total_sales = sum(order['total'] for order in st.session_state.order_history)
            total_orders = len(st.session_state.order_history)
            total_items = sum(sum(item['qty'] for item in order['items'].values()) for order in st.session_state.order_history)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Orders", total_orders)
            with col2:
                st.metric("Total Revenue", f"Rs. {total_sales:,}")
            with col3:
                st.metric("Total Items Sold", total_items)
            
            # Export options
            if st.button("📥 Export Data (CSV)"):
                data = []
                for order in st.session_state.order_history:
                    data.append({
                        "Order #": order['order_number'],
                        "Date": order['date'],
                        "Customer": order['customer'],
                        "Type": order['order_type'],
                        "Total": order['total'],
                    })
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

# Footer
st.divider()
st.caption(f"© 2024 {RESTAURANT_NAME} - Professional POS System")
st.caption(f"Version 2.0 | Orders Today: {len(st.session_state.daily_sales.get(date.today().isoformat(), {}).get('orders', []))}")
