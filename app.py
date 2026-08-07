import streamlit as st

# Page configuration for mobile and desktop responsiveness
st.set_page_config(
    page_title="Affans Kitchen - POS", page_icon="🍔", layout="wide"
)

# Menu items and prices
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

# Initialize cart in session state
if "cart" not in st.session_state:
  st.session_state.cart = {}

# Restaurant Title
st.title("🍽️ Affans Kitchen - POS System")
st.markdown("---")

# Layout: Two columns for menu and cart
col1, col2 = st.columns([1.5, 1])

with col1:
  st.subheader("Menu Items")

  # Display menu buttons in a grid
  menu_items = list(MENU.items())
  for i in range(0, len(menu_items), 2):
    c1, c2 = st.columns(2)
    with c1:
      item1, price1 = menu_items[i]
      if st.button(
          f"{item1}\n${price1:.2f}",
          key=f"btn_{item1}",
          use_container_width=True,
      ):
        if item1 in st.session_state.cart:
          st.session_state.cart[item1] += 1
        else:
          st.session_state.cart[item1] = 1
        st.rerun()

    if i + 1 < len(menu_items):
      with c2:
        item2, price2 = menu_items[i + 1]
        if st.button(
            f"{item2}\n${price2:.2f}",
            key=f"btn_{item2}",
            use_container_width=True,
        ):
          if item2 in st.session_state.cart:
            st.session_state.cart[item2] += 1
          else:
            st.session_state.cart[item2] = 1
          st.rerun()

with col2:
  st.subheader("Current Order")

  if not st.session_state.cart:
    st.info("Your cart is empty. Tap menu items to add.")
  else:
    subtotal = 0.0

    # Display cart items
    for item, qty in list(st.session_state.cart.items()):
      price = MENU[item]
      item_total = price * qty
      subtotal += item_total

      sc1, sc2, sc3 = st.columns([2, 1, 1])
      with sc1:
        st.text(f"{item}\n${price:.2f}x{qty}")
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
      if st.button("Complete Order", type="primary", use_container_width=True):
        st.success("Order Placed Successfully!")
        st.session_state.cart = {}
        st.rerun()
    with btn_col2:
      if st.button("Clear Cart", use_container_width=True):
        st.session_state.cart = {}
        st.rerun()
