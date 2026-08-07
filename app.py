"""
Affan's Kitchen - Restaurant Order / POS System
------------------------------------------------
A single-file Streamlit app for taking orders (Breakfast / Lunch / Dinner),
printing bills/receipts, and tracking daily sales.
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

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

# Initialize session state
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "order_placed" not in st.session_state:
    st.session_state.order_placed = False

if "daily_orders" not in st.session_state:
    st.session_state.daily_orders = []

if "menu_qty" not in st.session_state:
    st.session_state.menu_qty = {}


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


def save_order_to_history():
    """Save current order to daily orders history"""
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
    
    order = {
        "order_id": len(st.session_state.daily_orders) + 1,
        "date": order_date,
        "time": order_time.strftime("%I:%M %p"),
        "items": items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "grand_total": grand_total
    }
    
    st.session_state.daily_orders.append(order)


# App Header
st.markdown(f"# 🍲 {RESTAURANT_NAME}")
st.caption(RESTAURANT_TAGLINE)

# Pakistan time display
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
            document.getElementById('live-clock').innerHTML = '🕐 PKT: ' + pakistan.toLocaleString('en-GB', options);
        }}
        updateClock();
        setInterval(updateClock, 1000);
    </script>
""", height=35)

st.divider()

# Navigation
page = st.sidebar.selectbox("📌 Navigation", ["📋 Take Order", "📊 Sales Report"])

if page == "📋 Take Order":
    menu_col, cart_col = st.columns([2, 1])

    with menu_col:
        st.subheader("📋 Menu")
        tabs = st.tabs(list(MENU.keys()))
        
        for tab, category in zip(tabs, MENU.keys()):
            with tab:
                # Use a form-like container for better performance
                for item, price in MENU[category].items():
                    qty_key = f"qty_{category}_{item}"
                    if qty_key not in st.session_state.menu_qty:
                        st.session_state.menu_qty[qty_key] = 0
                    
                    c1, c2, c3, c4, c5 = st.columns([2, 1, 0.6, 0.6, 0.6])
                    c1.write(f"**{item}**")
                    c2.write(f"Rs. {price}")
                    
                    # Use callback for faster response
                    if c3.button("➖", key=f"minus_{category}_{item}", use_container_width=True):
                        if st.session_state.menu_qty[qty_key] > 0:
                            st.session_state.menu_qty[qty_key] -= 1
                    
                    c4.markdown(f"<div style='text-align: center; padding: 5px; font-weight: bold; font-size: 18px;'>{st.session_state.menu_qty[qty_key]}</div>", unsafe_allow_html=True)
                    
                    if c5.button("➕", key=f"plus_{category}_{item}", use_container_width=True):
                        st.session_state.menu_qty[qty_key] += 1

                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button(f"🛒 Add to Cart", key=f"add_{category}", use_container_width=True, type="primary"):
                    added_any = False
                    for item in MENU[category].keys():
                        qty_key = f"qty_{category}_{item}"
                        qty = st.session_state.menu_qty[qty_key]
                        if qty > 0:
                            add_to_cart(item, MENU[category][item], qty)
                            added_any = True
                            st.session_state.menu_qty[qty_key] = 0
                    
                    if added_any:
                        st.toast(f"✅ {category} items added!", icon="🛒")
                    else:
                        st.toast("⚠️ Select items first!", icon="⚠️")

    with cart_col:
        st.subheader("🧾 Current Order")

        if not st.session_state.cart:
            st.info("No items added yet.")
        else:
            # Use a compact table for cart items
            total = 0
            cart_items = list(st.session_state.cart.items())
            
            for item, data in cart_items:
                qty = data["qty"]
                price = data["price"]
                line_total = qty * price
                total += line_total

                c1, c2, c3, c4, c5 = st.columns([2, 1, 0.5, 0.5, 0.5])
                c1.write(f"**{item}**")
                c2.write(f"Rs.{line_total}")
                
                if c3.button("➖", key=f"cart_minus_{item}", use_container_width=True):
                    decrease_qty(item)
                
                c4.markdown(f"<div style='text-align: center; font-size: 16px; font-weight: bold;'>{qty}</div>", unsafe_allow_html=True)
                
                if c5.button("➕", key=f"cart_plus_{item}", use_container_width=True):
                    increase_qty(item, price)

            st.divider()
            
            tax_rate = st.number_input("Tax / Service %", min_value=0, max_value=30, value=0, step=1, key="tax_rate_input")
            st.session_state["tax_rate"] = tax_rate
            tax_amount = round(total * tax_rate / 100)
            grand_total = total + tax_amount

            st.write(f"Subtotal: **Rs. {total:,}**")
            st.write(f"Tax/Service ({tax_rate}%): **Rs. {tax_amount:,}**")
            st.markdown(f"### 💰 Grand Total: Rs. {grand_total:,}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Place Order", use_container_width=True, type="primary"):
                    save_order_to_history()
                    st.session_state.order_placed = True
                    st.success(f"✅ Order placed! Total: Rs. {grand_total:,}")
                    st.balloons()
            with col_b:
                if st.button("🗑️ Clear", use_container_width=True):
                    clear_cart()

    if st.session_state.order_placed and st.session_state.cart:
        st.divider()
        st.subheader("🖨️ Bill / Receipt")

        order_time = get_pakistan_time().strftime("%d-%m-%Y %I:%M %p")
        total = sum(d["qty"] * d["price"] for d in st.session_state.cart.values())
        tax_rate = st.session_state.get("tax_rate", 0)
        tax_amount = round(total * tax_rate / 100)
        grand_total = total + tax_amount

        receipt_lines = []
        receipt_lines.append("=" * 40)
        receipt_lines.append(RESTAURANT_NAME.center(40))
        receipt_lines.append(RESTAURANT_TAGLINE.center(40))
        receipt_lines.append("=" * 40)
        receipt_lines.append(f"Date: {order_time} (PKT)")
        receipt_lines.append("-" * 40)
        receipt_lines.append(f"{'Item':<20}{'Qty':>6}{'Amt':>14}")
        receipt_lines.append("-" * 40)
        for item, data in st.session_state.cart.items():
            qty = data["qty"]
            price = data["price"]
            line_total = qty * price
            receipt_lines.append(f"{item[:20]:<20}{qty:>6}{line_total:>14}")
        receipt_lines.append("-" * 40)
        receipt_lines.append(f"{'Subtotal':<26}{total:>14}")
        receipt_lines.append(f"{'Tax/Service':<26}{tax_amount:>14}")
        receipt_lines.append("-" * 40)
        receipt_lines.append(f"{'TOTAL':<26}{grand_total:>14}")
        receipt_lines.append("=" * 40)
        receipt_lines.append("Thank you for your order!".center(40))
        receipt_lines.append("=" * 40)

        receipt_text = "\n".join(receipt_lines)

        st.code(receipt_text, language=None)

        st.download_button(
            "⬇️ Download Receipt (.txt)",
            data=receipt_text,
            file_name=f"receipt_{get_pakistan_time().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

elif page == "📊 Sales Report":
    st.subheader("📊 Daily Sales Report")
    
    if not st.session_state.daily_orders:
        st.info("No orders have been placed yet. Start taking orders to see sales data!")
    else:
        dates = list(set(order["date"] for order in st.session_state.daily_orders))
        dates.sort(reverse=True)
        
        selected_date = st.selectbox("Select Date", ["All Dates"] + dates)
        
        if selected_date == "All Dates":
            filtered_orders = st.session_state.daily_orders
        else:
            filtered_orders = [order for order in st.session_state.daily_orders if order["date"] == selected_date]
        
        total_orders = len(filtered_orders)
        total_sales = sum(order["grand_total"] for order in filtered_orders)
        total_tax = sum(order["tax_amount"] for order in filtered_orders)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Orders", total_orders)
        col2.metric("Total Sales (Rs.)", f"{total_sales:,}")
        col3.metric("Total Tax (Rs.)", f"{total_tax:,}")
        
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
        
        st.divider()
        
        st.subheader("📝 Order History")
        
        for order in filtered_orders:
            with st.expander(f"Order #{order['order_id']} - {order['date']} at {order['time']} - Rs. {order['grand_total']}"):
                st.write(f"**Date:** {order['date']}")
                st.write(f"**Time:** {order['time']} (PKT)")
                for item in order["items"]:
                    st.write(f"  • {item['item']} x{item['qty']} = Rs. {item['total']}")
                st.write(f"**Subtotal:** Rs. {order['subtotal']}")
                st.write(f"**Tax ({order['tax_rate']}%):** Rs. {order['tax_amount']}")
                st.write(f"**Grand Total:** Rs. {order['grand_total']}")
        
        st.divider()
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
