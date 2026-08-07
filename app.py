
import streamlit as st
from datetime import datetime
import pandas as pd
import os
import json
import uuid
import base64

st.set_page_config(
    page_title="Affan's Kitchen POS",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------
# LOGIN
# -----------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "staff_name" not in st.session_state:
    st.session_state.staff_name = ""

if not st.session_state.logged_in:

    st.markdown(
    """
    <style>
    .login-box{
        width:420px;
        margin:auto;
        margin-top:60px;
        padding:30px;
        border-radius:20px;
        background:white;
        box-shadow:0 10px 30px rgba(0,0,0,.25);
    }

    .title{
        text-align:center;
        font-size:42px;
        font-weight:bold;
        color:#d62828;
    }

    .subtitle{
        text-align:center;
        color:gray;
        margin-bottom:20px;
    }

    div.stButton>button{
        width:100%;
        height:60px;
        border-radius:12px;
        font-size:22px;
        font-weight:bold;
        background:#ff6b00;
        color:white;
        border:none;
    }

    div.stButton>button:hover{
        background:#e85d04;
    }

    </style>
    """,
    unsafe_allow_html=True
    )

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown('<div class="title">🍔 Affan\'s Kitchen</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="subtitle">Restaurant POS System</div>',
        unsafe_allow_html=True
    )

    staff = st.text_input("Staff Name")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("LOGIN"):

        if password == "112233":

            st.session_state.logged_in = True
            st.session_state.staff_name = staff
            st.rerun()

        else:
            st.error("Wrong password")

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
    # ===========================================
# SESSION STATE
# ===========================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "order_number" not in st.session_state:
    st.session_state.order_number = 1001

MENU = {
    "Breakfast": {
        "Paratha": 180,
        "Omelette": 250,
        "Halwa Puri": 320,
        "Tea": 120,
        "Coffee": 180,
    },

    "Lunch": {
        "Chicken Biryani": 450,
        "Beef Biryani": 520,
        "Chicken Karahi": 1450,
        "Chicken Handi": 1650,
        "Daal": 280,
        "Naan": 40,
    },

    "Dinner": {
        "BBQ Platter": 1800,
        "Chicken Tikka": 420,
        "Seekh Kebab": 390,
        "Zinger Burger": 520,
        "Fries": 250,
        "Cold Drink": 120,
    }
}

# ===========================================
# MODERN CSS
# ===========================================

st.markdown("""
<style>

.main{
    background:#f6f6f6;
}

.block-container{
    padding-top:1rem;
}

.bigtitle{
    font-size:38px;
    font-weight:bold;
    color:#D62828;
}

.staff{
    font-size:18px;
    color:#555;
}

.totalbox{
    background:#ffffff;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,.12);
    text-align:center;
    margin-top:15px;
}

.totalprice{
    font-size:42px;
    color:#D62828;
    font-weight:bold;
}

.section{
    background:white;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 2px 10px rgba(0,0,0,.10);
    margin-bottom:15px;
}

div.stButton > button{
    width:100%;
    height:70px;
    font-size:22px;
    font-weight:bold;
    border-radius:14px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
f"""
<div class="bigtitle">
🍔 Affan's Kitchen POS
</div>

<div class="staff">
Logged in as <b>{st.session_state.staff_name}</b>
</div>
""",
unsafe_allow_html=True
)

left,right=st.columns([2,1])

# ===========================================
# MENU
# ===========================================

with left:

    tabs=st.tabs(["🍳 Breakfast","🍛 Lunch","🍔 Dinner"])

    categories=list(MENU.keys())

    for tab,category in zip(tabs,categories):

        with tab:

            items=MENU[category]

            cols=st.columns(2)

            index=0

            for name,price in items.items():

                with cols[index%2]:

                    if st.button(
                        f"{name}\nRs {price}",
                        key=name,
                        use_container_width=True
                    ):

                        st.session_state.cart.append({
                            "item":name,
                            "price":price,
                            "qty":1,
                            "time":datetime.now().strftime("%I:%M:%S %p")
                        })

                        st.rerun()

                index+=1
                # ===========================================
# CART
# ===========================================

with right:

    st.markdown("## 🛒 Current Order")

    if len(st.session_state.cart) == 0:

        st.info("Cart is empty")

    else:

        grand_total = 0

        remove_index = None

        for i, item in enumerate(st.session_state.cart):

            subtotal = item["price"] * item["qty"]
            grand_total += subtotal

            with st.container(border=True):

                c1, c2 = st.columns([3,1])

                with c1:

                    st.markdown(f"### {item['item']}")

                    st.write(f"🕒 Added : {item['time']}")

                    st.write(f"Rs {item['price']} x {item['qty']}")

                with c2:

                    if st.button("➕", key=f"plus{i}"):

                        st.session_state.cart[i]["qty"] += 1
                        st.rerun()

                    if st.button("➖", key=f"minus{i}"):

                        if st.session_state.cart[i]["qty"] > 1:
                            st.session_state.cart[i]["qty"] -= 1
                        else:
                            remove_index = i

                        st.rerun()

                    if st.button("❌", key=f"remove{i}"):

                        remove_index = i
                        st.rerun()

                st.markdown(
                    f"### Subtotal : Rs {subtotal}"
                )

        if remove_index is not None:

            st.session_state.cart.pop(remove_index)
            st.rerun()

        st.markdown("---")

        st.markdown(
            f"""
            <div class="totalbox">
                <div>Total Amount</div>
                <div class="totalprice">
                    Rs {grand_total}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🧹 Clear Cart",
                use_container_width=True
            ):

                st.session_state.cart = []
                st.rerun()

        with col2:

            if st.button(
                "✅ Checkout",
                use_container_width=True
            ):

                st.session_state.order_number += 1

                st.success(
                    f"Order #{st.session_state.order_number} created successfully!"
                )

                st.balloons()
                # ===========================================
# RECEIPT PREVIEW
# ===========================================

st.divider()

st.subheader("🧾 Receipt Preview")

if len(st.session_state.cart) > 0:

    receipt_total = sum(
        item["price"] * item["qty"]
        for item in st.session_state.cart
    )

    order_time = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    st.markdown(
        """
        <style>

        .receipt{

            background:white;
            padding:25px;
            border-radius:15px;
            border:2px dashed #444;

        }

        .receipt-header{

            display:flex;
            justify-content:space-between;
            align-items:center;

        }

        .logo{

            width:90px;
            height:90px;
            border-radius:50%;
            background:#eeeeee;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:42px;

        }

        .restaurant{

            text-align:right;

        }

        .restaurant h2{

            color:#D62828;
            margin:0;

        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="receipt">', unsafe_allow_html=True)

    col1, col2 = st.columns([1,3])

    with col1:

        # Replace this with st.image("assets/logo.png", width=90)
        st.markdown(
            """
            <div class="logo">
            🍔
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="restaurant">
            <h2>Affan's Kitchen</h2>
            <b>Restaurant & Fast Food</b><br>
            Thank you for visiting
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    left_info, right_info = st.columns(2)

    with left_info:

        st.write(
            f"**Order #:** {st.session_state.order_number}"
        )

        st.write(
            f"**Staff:** {st.session_state.staff_name}"
        )

    with right_info:

        st.write(
            f"**Date:** {order_time}"
        )

    st.markdown("---")

    item_table = []

    for item in st.session_state.cart:

        item_table.append(
            {
                "Item": item["item"],
                "Qty": item["qty"],
                "Price": item["price"],
                "Total": item["qty"] * item["price"],
            }
        )

    df = pd.DataFrame(item_table)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### -------------------------")

    st.markdown(
        f"# Total : Rs {receipt_total}"
    )

    st.success("Ready to Print")

    st.markdown("</div>", unsafe_allow_html=True)

else:

    st.info("Add menu items to generate a receipt preview.")
    
