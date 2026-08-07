import base64
from datetime import datetime
import streamlit as st

# Page configuration for mobile and desktop responsiveness
st.set_page_config(
    page_title="Affans Kitchen - POS", page_icon="🍔", layout="wide"
)

# --- LOGIN CONFIGURATION ---
POS_PASSCODE = "112233"


def check_password():
  """Returns True if the user entered the correct password."""

  def password_entered():
    if st.session_state["password"] == POS_PASSCODE:
      st.session_state["password_correct"] = True
      del st.session_state["password"]
    else:
      st.session_state["password_correct"] = False

  if "password_correct" not in st.session_state:
    st.markdown("## 🔐 Affans Kitchen - Secure POS Login")
    st.text_input(
        "Enter Staff Passcode",
        type="password",
        on_change=password_entered,
        key="password",
    )
    return False
  elif not st.session_state["password_correct"]:
    st.markdown("## 🔐 Affans Kitchen - Secure POS Login")
    st.text_input(
        "Enter Staff Passcode",
        type="password",
        on_change=password_entered,
        key="password",
    )
    st.error("😕 Passcode incorrect. Please try again.")
    return False
  else:
    return True


if not check_password():
  st.stop()

# --- STYLING FOR FAST-FOOD TOUCH BUTTONS ---
st.markdown(
    """
    <style>
    /* Make buttons look like large, chunky fast-food POS buttons */
    div.stButton > button {
        background-color: #f8f9fa;
        color: #212529;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 20px 10px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        width: 100%;
        margin-bottom: 10px;
    }
    div.stButton > button:hover {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- MENU & DATA CONFIGURATION ---
MENU = {
    "Cheeseburger": 8.50,
    "Chicken Burger": 7.50,
    "French Fries": 3.00,
    "Onion Rings": 3.50,
    "Soft Drink": 2.00,
    "Bottled Water": 1.50,
    "Pepperoni Pizza": 12.00,
    "Margherita Pizza": 10.00,
    "Chocolate Brownie": 4.00,
    "Ice Cream Scoop": 2.50,
}

TAX_RATE = 0.08  # 8% Tax

# Initialize session states
if "cart" not in st.session_state:
  st.session_state.cart = {}
if "daily_sales" not in st.session_state:
  st.session_state.daily_sales = []

# Top bar with title and logout button
title_col, logout_col = st.columns([3, 1])
with title_col:
  st.title("🍔 Affans Kitchen - POS System")
with logout_col:
  if st.button("🔒 Logout", use_container_width=True):
    st.session_state["password_correct"] = False
    st.rerun()

st.markdown("---")

# Layout: Menu on left, Cart & Sales Tracker on right
tab_pos, tab_sales = st.tabs(["🛒 Take Orders", "📊 Daily Sales Tracker"])

with tab_pos:
  col1, col2 = st.columns([1.5, 1])

  with col1:
    st.subheader("Menu Items")
    menu_items = list(MENU.items())

    for i in range(0, len(menu_items), 2):
      c1, c2 = st.columns(2)
      with c1:
        item1, price1 = menu_items[i]
        if st.button(f"{item1}\n${price1:.2f}", key=f"btn_{item1}"):
          add_time = datetime.now().strftime("%H:%M:%S")
          if item1 in st.session_state.cart:
            st.session_state.cart[item1]["qty"] += 1
          else:
            st.session_state.cart[item1] = {
                "price": price1,
                "qty": 1,
                "time": add_time,
            }
          st.rerun()

      if i + 1 < len(menu_items):
        with c2:
          item2, price2 = menu_items[i + 1]
          if st.button(f"{item2}\n${price2:.2f}", key=f"btn_{item2}"):
            add_time = datetime.now().strftime("%H:%M:%S")
            if item2 in st.session_state.cart:
              st.session_state.cart[item2]["qty"] += 1
            else:
              st.session_state.cart[item2] = {
                  "price": price2,
                  "qty": 1,
                  "time": add_time,
              }
            st.rerun()

  with col2:
    st.subheader("Current Order & Receipt")

    if not st.session_state.cart:
      st.info("Your cart is empty. Tap menu items to add.")
    else:
      # Bill Header: Logo Left, Affans Kitchen Right
      bill_col1, bill_col2 = st.columns([1, 2])
      with bill_col1:
        st.markdown("🍲 **[Logo]**")
      with bill_col2:
        st.markdown("### Affans Kitchen")

      st.markdown(
          f"<small>Order Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>",
          unsafe_allow_html=True,
      )
      st.markdown("---")

      subtotal = 0.0

      for item, data in list(st.session_state.cart.items()):
        price = data["price"]
        qty = data["qty"]
        time_added = data["time"]
        item_total = price * qty
        subtotal += item_total

        sc1, sc2, sc3 = st.columns([2, 1, 1])
        with sc1:
          st.text(f"{item}\n${price:.2f} x {qty} (Added: {time_added})")
        with sc2:
          st.text(f"${item_total:.2f}")
        with sc3:
          if st.button("❌", key=f"rem_{item}"):
            del st.session_state.cart[item]
            st.rerun()

      st.markdown("---")
      tax = subtotal * TAX_RATE
      grand_total = subtotal + tax

      st.write(f"**Subtotal:** ${subtotal:.2f}")
      st.write(f"**Tax (8%):** ${tax:.2f}")
      st.markdown(f"### Total: ${grand_total:.2f}")

      btn_col1, btn_col2 = st.columns(2)
      with btn_col1:
        if st.button(
            "✅ Complete Order", type="primary", use_container_width=True
        ):
          # Save order to daily sales history
          order_record = {
              "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "items": dict(st.session_state.cart),
              "total": grand_total,
          }
          st.session_state.daily_sales.append(order_record)
          st.success("Order Placed Successfully!")
          st.session_state.cart = {}
          st.rerun()
      with btn_col2:
        if st.button("🗑️ Clear", use_container_width=True):
          st.session_state.cart = {}
          st.rerun()

with tab_sales:
  st.subheader("📊 Daily Sales Tracking")
  if not st.session_state.daily_sales:
    st.info("No completed orders yet today.")
  else:
    total_revenue = sum(order["total"] for order in st.session_state.daily_sales)
    st.metric(
        label="Total Revenue Today", value=f"${total_revenue:.2f}", delta=None
    )
    st.markdown("---")

    for idx, sale in enumerate(reversed(st.session_state.daily_sales), 1):
      with st.expander(
          f"Order #{idx} - {sale['timestamp']} - Total: ${sale['total']:.2f}"
      ):
        for item, info in sale["items"].items():
          st.text(
              f"• {item} (Qty: {info['qty']}) @ ${info['price']:.2f} each"
              f" [Added at {info['time']}]"
          )
