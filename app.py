"""
Affan's Kitchen - Restaurant Order / POS System
------------------------------------------------
A single-file Streamlit app for taking orders (Breakfast / Lunch / Dinner)
and printing a bill/receipt.

Run locally:
    pip install -r requirements.txt
    streamlit run streamlit_app.py

Put your logo file (renamed to "logo.png") in the same folder as this
script if you want it to appear at the top of the page.
"""

import streamlit as st
from datetime import datetime
import os

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Affan's Kitchen - POS", page_icon="🍲", layout="wide")

# ---------------------------------------------------------------------------
# MENU  (spelling corrected — edit the prices to match your real prices)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}  # {item_name: {"qty": int, "price": int}}

if "order_placed" not in st.session_state:
    st.session_state.order_placed = False


def add_to_cart(item, price, qty):
    if qty <= 0:
        return
    if item in st.session_state.cart:
        st.session_state.cart[item]["qty"] += qty
    else:
        st.session_state.cart[item] = {"qty": qty, "price": price}


def remove_from_cart(item):
    if item in st.session_state.cart:
        del st.session_state.cart[item]


def clear_cart():
    st.session_state.cart = {}
    st.session_state.order_placed = False


# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
logo_col, title_col = st.columns([1, 4])
with logo_col:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110)
with title_col:
    st.markdown(f"## {RESTAURANT_NAME}")
    st.caption(RESTAURANT_TAGLINE)

st.divider()

# ---------------------------------------------------------------------------
# MENU + ORDERING UI
# ---------------------------------------------------------------------------
menu_col, cart_col = st.columns([2, 1])

with menu_col:
    st.subheader("📋 Menu")
    tabs = st.tabs(list(MENU.keys()))
    for tab, category in zip(tabs, MENU.keys()):
        with tab:
            for item, price in MENU[category].items():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{item}**")
                c2.write(f"Rs. {price}")
                qty = c3.number_input(
                    "Qty", min_value=0, max_value=50, value=0, step=1,
                    key=f"{category}_{item}", label_visibility="collapsed"
                )
                if qty > 0:
                    st.session_state.setdefault("_pending_qty", {})[f"{category}_{item}"] = (item, price, qty)

            if st.button(f"Add {category} items to order", key=f"add_{category}"):
                pending = st.session_state.get("_pending_qty", {})
                added_any = False
                for k, (item, price, qty) in list(pending.items()):
                    if k.startswith(category):
                        add_to_cart(item, price, qty)
                        added_any = True
                if added_any:
                    st.success(f"{category} items added to order.")
                else:
                    st.info("Set a quantity above 0 before adding.")

# ---------------------------------------------------------------------------
# CART / ORDER SUMMARY
# ---------------------------------------------------------------------------
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

            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"{item} x{qty}")
            c2.write(f"Rs. {line_total}")
            if c3.button("❌", key=f"remove_{item}"):
                remove_from_cart(item)
                st.rerun()

        st.divider()
        tax_rate = st.number_input("Tax / Service %", min_value=0, max_value=30, value=0, step=1)
        tax_amount = round(total * tax_rate / 100)
        grand_total = total + tax_amount

        st.write(f"Subtotal: **Rs. {total}**")
        st.write(f"Tax/Service ({tax_rate}%): **Rs. {tax_amount}**")
        st.markdown(f"### Grand Total: Rs. {grand_total}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Place Order"):
                st.session_state.order_placed = True
        with col_b:
            if st.button("🗑️ Clear Order"):
                clear_cart()
                st.rerun()

# ---------------------------------------------------------------------------
# BILL / RECEIPT
# ---------------------------------------------------------------------------
if st.session_state.order_placed and st.session_state.cart:
    st.divider()
    st.subheader("🖨️ Bill / Receipt")

    order_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    total = sum(d["qty"] * d["price"] for d in st.session_state.cart.values())
    tax_rate = st.session_state.get("tax_rate", 0)
    tax_amount = round(total * tax_rate / 100)
    grand_total = total + tax_amount

    receipt_lines = []
    receipt_lines.append(RESTAURANT_NAME.center(32))
    receipt_lines.append(RESTAURANT_TAGLINE.center(32))
    receipt_lines.append("-" * 32)
    receipt_lines.append(f"Date: {order_time}")
    receipt_lines.append("-" * 32)
    receipt_lines.append(f"{'Item':<18}{'Qty':>4}{'Amt':>10}")
    receipt_lines.append("-" * 32)
    for item, data in st.session_state.cart.items():
        qty = data["qty"]
        price = data["price"]
        line_total = qty * price
        receipt_lines.append(f"{item[:18]:<18}{qty:>4}{line_total:>10}")
    receipt_lines.append("-" * 32)
    receipt_lines.append(f"{'Subtotal':<22}{total:>10}")
    receipt_lines.append(f"{'Tax/Service':<22}{tax_amount:>10}")
    receipt_lines.append(f"{'TOTAL':<22}{grand_total:>10}")
    receipt_lines.append("-" * 32)
    receipt_lines.append("Thank you for your order!".center(32))

    receipt_text = "\n".join(receipt_lines)

    st.code(receipt_text, language=None)

    st.download_button(
        "⬇️ Download Receipt (.txt)",
        data=receipt_text,
        file_name=f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
    )

    # Browser print button — opens the print dialog for this receipt only
    print_html = f"""
    <div id="receipt-print" style="font-family: monospace; white-space: pre; display:none;">{receipt_text}</div>
    <button onclick="printReceipt()" style="padding:8px 16px; font-size:14px; cursor:pointer;">🖨️ Print Receipt</button>
    <script>
    function printReceipt() {{
        var content = document.getElementById('receipt-print').innerText;
        var printWindow = window.open('', '', 'width=400,height=600');
        printWindow.document.write('<pre style="font-family:monospace; font-size:14px;">' + content + '</pre>');
        printWindow.document.close();
        printWindow.print();
    }}
    </script>
    """
    st.components.v1.html(print_html, height=60)

