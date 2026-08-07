import base64
from datetime import datetime
import io
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page Configuration
st.set_page_config(
    page_title="Affan's Kitchen - POS & Management",
    page_icon="🍽️",
    layout="wide",
)

# Initialize Session State for Orders & Analytics
if "orders_history" not in st.session_state:
  st.session_state.orders_history = []


# Base64 Logo Function (Embedded Logo)
def get_base64_logo():
  # Placeholder transparent/clean small base64 logo string
  return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


# Menu Configuration
MENU = {
    "Breakfast": {
        "Omelette & Bread": 250,
        "Halwa Puri Set": 350,
        "Paratha Chai": 180,
        "Pancakes": 400,
    },
    "Lunch": {
        "Chicken Biryani": 550,
        "Beef Karahi (Half)": 950,
        "Daal Chawal": 300,
        "Roti / Naan": 40,
    },
    "Dinner": {
        "Mutton Pulao": 750,
        "Chicken Tikka Pizza": 1100,
        "BBQ Platter": 1400,
        "Mineral Water": 80,
    },
}

# Navigation Tabs
tab_pos, tab_kds, tab_analytics = st.tabs(
    ["🛒 Cashier POS", "👨‍🍳 Kitchen Display (KDS)", "📊 Sales Analytics"]
)

with tab_pos:
  st.title("🍽️ Affan's Kitchen - POS System")

  col_menu, col_bill = st.columns([1.2, 0.8])

  with col_menu:
    st.subheader("Select Category & Items")
    category = st.selectbox("Meal Category", list(MENU.keys()))

    # Cart storage inside session state
    if "cart" not in st.session_state:
      st.session_state.cart = {}

    # Display items as interactive selectors
    selected_items = {}
    for item, price in MENU[category].items():
      col1, col2 = st.columns([2, 1])
      with col1:
        st.write(f"**{item}** (Rs. {price})")
      with col2:
        qty = st.number_input(
            f"Qty {item}",
            min_value=0,
            max_value=20,
            value=st.session_state.cart.get(item, {}).get("qty", 0),
            key=f"qty_{item}",
            label_visibility="collapsed",
        )
        if qty > 0:
          selected_items[item] = {"price": price, "qty": qty}

    # Update Cart Button
    if st.button("Update Cart", type="primary"):
      for item in MENU[category]:
        if item in st.session_state.cart:
          del st.session_state.cart[item]
      st.session_state.cart.update(selected_items)
      st.success("Cart updated successfully!")

  with col_bill:
    st.subheader("Current Bill Summary")

    if not st.session_state.get("cart"):
      st.info("Your cart is empty.")
    else:
      subtotal = 0
      bill_items_list = []

      # Render Logo
      logo_b64 = get_base64_logo()
      st.markdown(
          f"<div style='text-align: center;'><img"
          f" src='data:image/png;base64,{logo_b64}' width='60'></div>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<h3 style='text-align: center; margin-bottom: 0;'>Affan's"
          " Kitchen</h3>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; color: gray;'>Official Receipt</p>",
          unsafe_allow_html=True,
      )
      st.write("--------------------------------------------------")

      for item, data in st.session_state.cart.items():
        total_price = data["price"] * data["qty"]
        subtotal += total_price
        bill_items_list.append({
            "item": item,
            "price": data["price"],
            "qty": data["qty"],
            "total": total_price,
        })
        st.text(f"{item} x{data['qty']} = Rs. {total_price}")

      tax = subtotal * 0.05  # 5% Tax example
      grand_total = subtotal + tax

      st.write("--------------------------------------------------")
      st.write(f"**Subtotal:** Rs. {subtotal:.2f}")
      st.write(f"**Tax (5%):** Rs. {tax:.2f}")
      st.markdown(f"### **Grand Total: Rs. {grand_total:.2f}**")

      # Complete Order Button
      if st.button("Complete Order & Send to Kitchen"):
        new_order = {
            "order_id": len(st.session_state.orders_history) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": bill_items_list,
            "grand_total": grand_total,
            "status": "Pending",
        }
        st.session_state.orders_history.append(new_order)
        st.success(f"Order #{new_order['order_id']} placed successfully!")
        st.session_state.cart = {}
        st.rerun()

      # PDF Generation Function
      def generate_pdf(order_data, sub, tx, grand):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        p.drawString(250, height - 50, "Affan's Kitchen")
        p.drawString(240, height - 65, "Official Receipt")
        p.drawString(
            50, height - 100, f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        p.drawString(50, height - 120, "-" * 55)

        y = height - 140
        for i in order_data:
          p.drawString(
              50, y, f"{i['item']} x{i['qty']} - Rs. {i['total']:.2f}"
          )
          y -= 20

        p.drawString(50, y - 10, "-" * 55)
        p.drawString(50, y - 35, f"Subtotal: Rs. {sub:.2f}")
        p.drawString(50, y - 55, f"Tax (5%): Rs. {tx:.2f}")
        p.drawString(50, y - 75, f"Grand Total: Rs. {grand:.2f}")

        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

      pdf_buffer = generate_pdf(
          bill_items_list, subtotal, tax, grand_total
      )
      st.download_button(
          label="📥 Download PDF Receipt",
          data=pdf_buffer,
          file_name="affans_kitchen_receipt.pdf",
          mime="application/pdf",
      )

with tab_kds:
  st.subheader("👨‍🍳 Kitchen Display System (Active Orders)")

  if not st.session_state.orders_history:
    st.info("No active orders in the queue.")
  else:
    for order in st.session_state.orders_history:
      if order["status"] != "Completed":
        with st.expander(
            f"Order #{order['order_id']} - Time: {order['timestamp']} -"
            f" Status: [{order['status']}]",
            expanded=True,
        ):
          for item_info in order["items"]:
            st.write(
                f"- **{item_info['item']}** (Quantity:"
                f" {item_info['qty']})"
            )

          col_btn1, col_btn2 = st.columns(2)
          with col_btn1:
            if st.button("Mark Preparing", key=f"prep_{order['order_id']}"):
              order["status"] = "Preparing"
              st.rerun()
          with col_btn2:
            if st.button("Mark Completed", key=f"comp_{order['order_id']}"):
              order["status"] = "Completed"
              st.rerun()

with tab_analytics:
  st.subheader("📊 Sales Analytics & Reporting Dashboard")

  if not st.session_state.orders_history:
    st.info("No sales data available yet.")
  else:
    total_sales = sum([o["grand_total"] for o in st.session_state.orders_history])
    total_orders = len(st.session_state.orders_history)

    m1, m2 = st.columns(2)
    m1.metric("Total Revenue", f"Rs. {total_sales:.2f}")
    m2.metric("Total Orders Placed", total_orders)

    st.write("---")
    st.subheader("Recent Order Logs")
    for o in reversed(st.session_state.orders_history):
      st.text(
          f"Order #{o['order_id']} | Total: Rs. {o['grand_total']:.2f} | Status:"
          f" {o['status']} | {o['timestamp']}"
      )
