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
import base64

st.set_page_config(page_title="Affan's Kitchen - POS", page_icon="🍲", layout="wide", initial_sidebar_state="collapsed")

# --- MOBILE-FRIENDLY STYLING ---
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    /* Bigger, thumb-friendly tap targets everywhere */
    .stButton > button {
        min-height: 40px;
        font-size: 16px !important;
        border-radius: 8px;
        padding: 6px 10px;
    }
    /* Prevent iOS auto-zoom on inputs (must be >=16px) */
    input, select, textarea {
        font-size: 16px !important;
    }
    /* Shrink the built-in gaps Streamlit adds around every element/row —
       this is the main cause of a page feeling "tall" on mobile */
    div[data-testid="stVerticalBlock"] { gap: 0.35rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.4rem !important; }
    div[data-testid="stElementContainer"] { margin-bottom: 0 !important; }
    hr { margin: 0.25rem 0 !important; }
    div[data-testid="stMetric"] { padding: 0.3rem !important; }

    /* Tighter padding on small screens so more fits without scrolling sideways */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            padding-top: 0.6rem !important;
            padding-bottom: 2rem !important;
        }
        h1 { font-size: 1.3rem !important; margin-bottom: 0.2rem !important; }
        h2, .stSubheader { font-size: 1.05rem !important; margin: 0.3rem 0 !important; }
        h3 { font-size: 1rem !important; }
        .stCaption { font-size: 0.75rem !important; }
        .stButton > button {
            padding: 6px 4px;
            font-size: 15px !important;
        }
        /* Make tabs compact & scrollable on touch */
        .stTabs [data-baseweb="tab"] {
            font-size: 14px;
            padding: 6px 8px;
        }
        .stTabs { margin-bottom: 0.2rem !important; }
        div[data-testid="stVerticalBlock"] { gap: 0.2rem !important; }
    }
    /* Compact bordered item-row cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.3rem 0.5rem;
        margin-bottom: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)


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

# Pakistan timezone offset (UTC+5)
PAKISTAN_OFFSET = timedelta(hours=5)

@st.cache_resource
def get_conn():
    """Single cached SQLite connection reused across reruns (fast)."""
    conn = sqlite3.connect('orders.db', check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

# --- PASSCODE PROTECTION ---
CORRECT_PASSCODE = "112233"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(f"# 🔐 {RESTAURANT_NAME}")
    st.markdown("### Please enter the passcode to continue")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        passcode = st.text_input("Enter Passcode", type="password", key="passcode_input")

        if st.button("🔓 Unlock", use_container_width=True, type="primary"):
            if passcode == CORRECT_PASSCODE:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect passcode! Please try again.")

    st.stop()

# --- LOGOUT BUTTON IN SIDEBAR ---
with st.sidebar:
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()

def get_pakistan_time():
    """Get current time in Pakistan (UTC+5)"""
    return datetime.utcnow() + PAKISTAN_OFFSET

def generate_receipt_html(order):
    """Generate HTML receipt for printing"""
    items_html = ""
    for item in order["items"]:
        items_html += f"""
        <tr>
            <td style="text-align: left; padding: 5px 10px;">{item['item'][:25]}</td>
            <td style="text-align: center; padding: 5px 10px;">{item['qty']}</td>
            <td style="text-align: right; padding: 5px 10px;">Rs. {item['total']}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @media print {{
                body {{ margin: 0; padding: 10px; }}
                .no-print {{ display: none !important; }}
                .receipt-container {{ max-width: 300px; margin: 0 auto; }}
            }}
            body {{
                font-family: 'Courier New', monospace;
                background: white;
            }}
            .receipt-container {{
                max-width: 300px;
                margin: 20px auto;
                padding: 15px;
                border: 1px dashed #ccc;
                background: #fff;
            }}
            .header {{
                text-align: center;
                border-bottom: 1px dashed #000;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }}
            .header h2 {{
                margin: 5px 0;
                font-size: 18px;
            }}
            .header p {{
                margin: 3px 0;
                font-size: 12px;
                color: #666;
            }}
            .info {{
                font-size: 13px;
                margin: 10px 0;
            }}
            .info p {{
                margin: 3px 0;
            }}
            .items-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            .items-table th {{
                border-bottom: 1px solid #000;
                padding: 5px 10px;
                font-size: 13px;
            }}
            .items-table td {{
                font-size: 13px;
            }}
            .total-section {{
                border-top: 1px dashed #000;
                padding-top: 10px;
                margin-top: 10px;
                font-size: 14px;
            }}
            .total-section .grand-total {{
                font-size: 16px;
                font-weight: bold;
                margin-top: 5px;
                padding-top: 5px;
                border-top: 1px solid #000;
            }}
            .footer {{
                text-align: center;
                margin-top: 15px;
                font-size: 12px;
                color: #666;
                border-top: 1px dashed #ccc;
                padding-top: 10px;
            }}
            .print-btn {{
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 30px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
                margin: 10px 0;
                width: 100%;
            }}
            .print-btn:hover {{
                background: #45a049;
            }}
            .order-id {{
                color: #4CAF50;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="receipt-container">
            <div class="header">
                <h2>{RESTAURANT_NAME}</h2>
                <p>{RESTAURANT_TAGLINE}</p>
            </div>

            <div class="info">
                <p><strong>Date:</strong> {order['date']} {order['time']} (PKT)</p>
                <p><strong>Order #:</strong> <span class="order-id">{order['order_id']}</span></p>
            </div>

            <table class="items-table">
                <thead>
                    <tr>
                        <th style="text-align: left;">Item</th>
                        <th style="text-align: center;">Qty</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <div class="total-section">
                <p><strong>Subtotal:</strong> <span style="float: right;">Rs. {order['subtotal']}</span></p>
                <p><strong>Tax ({order['tax_rate']}%):</strong> <span style="float: right;">Rs. {order['tax_amount']}</span></p>
                <p class="grand-total"><strong>TOTAL:</strong> <span style="float: right;">Rs. {order['grand_total']}</span></p>
            </div>

            <div class="footer">
                <p>Thank you for your order!</p>
                <p>Visit again 🍲</p>
            </div>
        </div>

        <div class="no-print" style="text-align: center;">
            <button class="print-btn" onclick="window.print()">🖨️ Print Receipt</button>
        </div>
    </body>
    </html>
    """
    return html

def generate_receipt_text(order):
    """Generate plain text receipt"""
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

    return "\n".join(receipt_lines)

# Initialize database
def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Orders table
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

    conn.commit()

@st.cache_data(show_spinner=False)
def load_menu_from_db():
    """Load menu from database (cached — cleared automatically after any edit)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT category, item_name, price, active FROM menu ORDER BY category, item_name')
    rows = c.fetchall()

    menu = {}
    for row in rows:
        category, item_name, price, active = row
        if active:
            if category not in menu:
                menu[category] = {}
            menu[category][item_name] = price
    return menu

def add_menu_item(category, item_name, price):
    """Add a new item to menu"""
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO menu (category, item_name, price)
            VALUES (?, ?, ?)
        ''', (category, item_name, price))
        conn.commit()
        load_menu_from_db.clear()
        return True, "Item added successfully!"
    except sqlite3.IntegrityError:
        return False, "Item already exists in this category!"

def update_menu_item(category, item_name, new_price, new_name=None):
    """Update an existing menu item's price or name"""
    conn = get_conn()
    c = conn.cursor()
    try:
        if new_name and new_name != item_name:
            c.execute('''
                UPDATE menu
                SET item_name = ?, price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category = ? AND item_name = ?
            ''', (new_name, new_price, category, item_name))
        else:
            c.execute('''
                UPDATE menu
                SET price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category = ? AND item_name = ?
            ''', (new_price, category, item_name))
        conn.commit()
        load_menu_from_db.clear()
        return True, "Item updated successfully!"
    except Exception as e:
        return False, f"Error updating item: {str(e)}"

def toggle_menu_item(category, item_name, active):
    """Activate or deactivate a menu item"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        UPDATE menu
        SET active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE category = ? AND item_name = ?
    ''', (active, category, item_name))
    conn.commit()
    load_menu_from_db.clear()

def get_all_categories():
    """Get all unique categories"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM menu ORDER BY category')
    categories = [row[0] for row in c.fetchall()]
    return categories

def get_all_menu_items():
    """Get all menu items (including inactive)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT category, item_name, price, active FROM menu ORDER BY category, item_name')
    rows = c.fetchall()
    return rows

def delete_menu_item(category, item_name):
    """Delete a menu item completely"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM menu WHERE category = ? AND item_name = ?', (category, item_name))
    conn.commit()
    load_menu_from_db.clear()

def save_order_to_db(order):
    """Save order to SQLite database"""
    conn = get_conn()
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

def load_orders_from_db():
    """Load all orders from SQLite database"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, order_id, date, time, items, subtotal, tax_rate, tax_amount, grand_total FROM orders ORDER BY id')
    rows = c.fetchall()

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
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM orders WHERE id = ?', (db_id,))
    conn.commit()

def delete_all_orders_from_db():
    """Delete all orders from database"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM orders')
    conn.commit()

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

if "inventory_delete_confirm" not in st.session_state:
    st.session_state.inventory_delete_confirm = None

if "print_order" not in st.session_state:
    st.session_state.print_order = None


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


# App Header — one compact live clock line instead of 3 stacked time displays
st.markdown(f"# 🍲 {RESTAURANT_NAME}")
st.markdown(f"<p style='margin:0 0 0.3rem 0; color:#888; font-size:0.85rem;'>{RESTAURANT_TAGLINE}</p>", unsafe_allow_html=True)

st.components.v1.html(f"""
    <div style="text-align: left; font-size: 13px; color: #888; font-family: sans-serif;">
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
            document.getElementById('live-clock').innerHTML = '🕐 ' + pakistan.toLocaleString('en-GB', options) + ' (PKT)';
        }}
        updateClock();
        setInterval(updateClock, 1000);
    </script>
""", height=22)

# Navigation
page = st.sidebar.selectbox("📌 Navigation", ["📋 Take Order", "📊 Sales Report", "📦 Inventory Management"])

# Fragment support: only the widget the user clicks reruns, not the whole app.
# Falls back to a no-op decorator on older Streamlit versions.
_fragment = getattr(st, "fragment", None) or getattr(st, "experimental_fragment", None) or (lambda f: f)


@_fragment
def render_order_taking():
    """Menu + cart. Wrapped in a fragment so tapping +/- is instant —
    it no longer reruns the header, clock, and sidebar on every click."""
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
                        qty_key = f"qty_{category}_{item}"
                        if qty_key not in st.session_state:
                            st.session_state[qty_key] = 0

                        c1, c2, c3, c4 = st.columns([3, 0.8, 0.7, 0.8], gap="small")
                        c1.markdown(
                            f"<div style='line-height:1.25; padding-top:6px;'>"
                            f"<b>{item}</b><br>"
                            f"<span style='color:#888; font-size:12.5px;'>Rs. {price}</span></div>",
                            unsafe_allow_html=True
                        )

                        if c2.button("➖", key=f"minus_{category}_{item}", use_container_width=True):
                            if st.session_state[qty_key] > 0:
                                st.session_state[qty_key] -= 1
                                if item in st.session_state.cart:
                                    decrease_qty(item)
                                    st.session_state[qty_key] = st.session_state.cart.get(item, {}).get("qty", 0)
                            st.rerun()

                        c3.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:700;'>{st.session_state[qty_key]}</div>", unsafe_allow_html=True)

                        if c4.button("➕", key=f"plus_{category}_{item}", use_container_width=True):
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

                c1, c2, c3, c4 = st.columns([3, 0.8, 0.7, 0.8], gap="small")
                c1.markdown(
                    f"<div style='line-height:1.25; padding-top:6px;'>"
                    f"<b>{item}</b><br>"
                    f"<span style='color:#888; font-size:12.5px;'>Rs. {line_total}</span></div>",
                    unsafe_allow_html=True
                )

                if c2.button("➖", key=f"cart_minus_{item}", use_container_width=True):
                    decrease_qty(item)
                    for category in MENU:
                        if item in MENU[category]:
                            qty_key = f"qty_{category}_{item}"
                            if qty_key in st.session_state:
                                st.session_state[qty_key] = st.session_state.cart.get(item, {}).get("qty", 0)
                    st.rerun()

                c3.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:700;'>{qty}</div>", unsafe_allow_html=True)

                if c4.button("➕", key=f"cart_plus_{item}", use_container_width=True):
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

            st.markdown(
                f"<div style='font-size:14px; line-height:1.6; margin-top:4px;'>"
                f"Subtotal: <b>Rs. {total}</b><br>"
                f"Tax/Service ({tax_rate}%): <b>Rs. {tax_amount}</b></div>"
                f"<div style='font-size:19px; font-weight:800; margin:4px 0 6px 0;'>Grand Total: Rs. {grand_total}</div>",
                unsafe_allow_html=True
            )

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

    # Show bill with print option
    if st.session_state.last_order:
        st.divider()
        st.subheader("🖨️ Bill / Receipt")

        order = st.session_state.last_order
        receipt_text = generate_receipt_text(order)
        st.code(receipt_text, language=None)

        col_bill1, col_bill2, col_bill3 = st.columns(3)
        with col_bill1:
            if st.button("🖨️ Print Receipt", use_container_width=True, type="primary"):
                st.session_state.print_order = order
                st.rerun()
        with col_bill2:
            st.download_button(
                "⬇️ Download (.txt)",
                data=receipt_text,
                file_name=f"receipt_{order['order_id']}_{order['date'].replace('-', '')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_bill3:
            if st.button("📋 New Order", use_container_width=True):
                st.session_state.last_order = None
                st.rerun()


if page == "📋 Take Order":
    # Check if we need to show print view
    if st.session_state.print_order:
        order = st.session_state.print_order
        receipt_html = generate_receipt_html(order)
        st.components.v1.html(receipt_html, height=600, scrolling=True)

        col_back, col_download = st.columns(2)
        with col_back:
            if st.button("⬅️ Back to POS", use_container_width=True):
                st.session_state.print_order = None
                st.rerun()
        with col_download:
            receipt_text = generate_receipt_text(order)
            st.download_button(
                "⬇️ Download Receipt (.txt)",
                data=receipt_text,
                file_name=f"receipt_{order['order_id']}_{order['date'].replace('-', '')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        render_order_taking()

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
            # Check if we need to show print view for an order
            if st.session_state.print_order:
                order = st.session_state.print_order
                receipt_html = generate_receipt_html(order)
                st.components.v1.html(receipt_html, height=600, scrolling=True)

                col_back_print, col_download_print = st.columns(2)
                with col_back_print:
                    if st.button("⬅️ Back to Sales Report", use_container_width=True):
                        st.session_state.print_order = None
                        st.rerun()
                with col_download_print:
                    receipt_text = generate_receipt_text(order)
                    st.download_button(
                        "⬇️ Download Receipt (.txt)",
                        data=receipt_text,
                        file_name=f"receipt_{order['order_id']}_{order['date'].replace('-', '')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                for order in filtered_orders:
                    with st.expander(f"Order #{order['order_id']} - {order['date']} at {order['time']} - Rs. {order['grand_total']}"):
                        col_info, col_actions = st.columns([3, 1])

                        with col_info:
                            st.write(f"**Date:** {order['date']}")
                            st.write(f"**Time:** {order['time']} (PKT)")
                            st.write(f"**Items:**")
                            for item in order["items"]:
                                st.write(f"  • {item['item']} x{item['qty']} = Rs. {item['total']}")
                            st.write(f"**Subtotal:** Rs. {order['subtotal']}")
                            st.write(f"**Tax ({order['tax_rate']}%):** Rs. {order['tax_amount']}")
                            st.write(f"**Grand Total:** Rs. {order['grand_total']}")

                        with col_actions:
                            # Print button for each order
                            if st.button("🖨️ Print", key=f"print_{order['db_id']}", use_container_width=True):
                                st.session_state.print_order = order
                                st.rerun()

                            # Delete button with confirmation
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
            csv_data = df_export.to_csv(index=False)
            st.download_button(
                "📥 Download Sales Report (CSV)",
                data=csv_data,
                file_name=f"sales_report_{selected_date if selected_date != 'All Dates' else 'all'}.csv",
                mime="text/csv",
                use_container_width=True
            )

elif page == "📦 Inventory Management":
    st.subheader("📦 Inventory Management")
    st.caption("Add, edit, deactivate, or delete menu items.")

    # ---- Add new item ----
    with st.expander("➕ Add New Menu Item", expanded=False):
        existing_categories = get_all_categories()
        with st.form("add_item_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cat_choice = st.selectbox(
                    "Category",
                    existing_categories + ["➕ New Category..."] if existing_categories else ["➕ New Category..."]
                )
                if cat_choice == "➕ New Category...":
                    new_category = st.text_input("New Category Name")
                else:
                    new_category = cat_choice
            with col2:
                new_item_name = st.text_input("Item Name")

            new_item_price = st.number_input("Price (Rs.)", min_value=0, step=10)

            submitted = st.form_submit_button("Add Item", use_container_width=True, type="primary")
            if submitted:
                if not new_category or not new_item_name:
                    st.error("Please fill in category and item name.")
                elif new_item_price <= 0:
                    st.error("Price must be greater than 0.")
                else:
                    success, msg = add_menu_item(new_category.strip(), new_item_name.strip(), new_item_price)
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    st.divider()

    # ---- List / edit / delete existing items ----
    all_items = get_all_menu_items()

    if not all_items:
        st.info("No menu items yet. Add one above to get started.")
    else:
        categories = sorted(set(row[0] for row in all_items))
        filter_cat = st.selectbox("Filter by Category", ["All"] + categories)

        display_items = all_items if filter_cat == "All" else [r for r in all_items if r[0] == filter_cat]

        for category, item_name, price, active in display_items:
            item_key = f"{category}::{item_name}"
            is_editing = st.session_state.inventory_editing == item_key
            is_deleting = st.session_state.inventory_delete_confirm == item_key

            with st.container(border=True):
                if is_editing:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        edit_name = st.text_input("Item Name", value=item_name, key=f"edit_name_{item_key}")
                    with col2:
                        edit_price = st.number_input("Price (Rs.)", min_value=0, step=10, value=int(price), key=f"edit_price_{item_key}")
                    with col3:
                        st.write("")
                        st.write("")
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾", key=f"save_{item_key}", use_container_width=True, help="Save"):
                                success, msg = update_menu_item(category, item_name, edit_price, edit_name.strip())
                                if success:
                                    st.session_state.inventory_editing = None
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        with col_cancel:
                            if st.button("❌", key=f"cancel_edit_{item_key}", use_container_width=True, help="Cancel"):
                                st.session_state.inventory_editing = None
                                st.rerun()
                elif is_deleting:
                    st.warning(f"⚠️ Delete **{item_name}** ({category}) permanently?")
                    col_y, col_n = st.columns(2)
                    with col_y:
                        if st.button("✅ Yes, Delete", key=f"inv_confirm_{item_key}", use_container_width=True, type="primary"):
                            delete_menu_item(category, item_name)
                            st.session_state.inventory_delete_confirm = None
                            st.success(f"Deleted {item_name}")
                            st.rerun()
                    with col_n:
                        if st.button("Cancel", key=f"inv_cancel_{item_key}", use_container_width=True):
                            st.session_state.inventory_delete_confirm = None
                            st.rerun()
                else:
                    col1, col2, col3, col4, col5, col6 = st.columns([1.2, 2, 1, 1, 1, 1])
                    col1.write(f"`{category}`")
                    col2.write(f"**{item_name}**" if active else f"~~{item_name}~~")
                    col3.write(f"Rs. {int(price)}")
                    col4.write("🟢 Active" if active else "⚪ Inactive")

                    if col5.button("✏️ Edit", key=f"edit_btn_{item_key}", use_container_width=True):
                        st.session_state.inventory_editing = item_key
                        st.rerun()

                    if active:
                        if col6.button("🚫 Disable", key=f"disable_{item_key}", use_container_width=True):
                            toggle_menu_item(category, item_name, 0)
                            st.rerun()
                    else:
                        if col6.button("✅ Enable", key=f"enable_{item_key}", use_container_width=True):
                            toggle_menu_item(category, item_name, 1)
                            st.rerun()

                    del_col = st.columns([5, 1])[1]
                    if del_col.button("🗑️ Delete Item", key=f"del_btn_{item_key}", use_container_width=True):
                        st.session_state.inventory_delete_confirm = item_key
                        st.rerun()
