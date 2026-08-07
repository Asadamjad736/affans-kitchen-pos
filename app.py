import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Affan's Kitchen POS",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# CUSTOM CSS
# ==============================

st.markdown("""
<style>

body{
    background:#f5f5f5;
}

.main .block-container{
    padding-top:15px;
}

div.stButton>button{
    width:100%;
    height:70px;
    border-radius:15px;
    font-size:22px;
    font-weight:bold;
}

.header{
    background:#d62828;
    color:white;
    padding:15px;
    border-radius:15px;
    text-align:center;
    font-size:36px;
    font-weight:bold;
}

.subheader{
    text-align:center;
    color:gray;
    margin-bottom:20px;
}

.loginbox{
    background:white;
    padding:35px;
    border-radius:20px;
    box-shadow:0px 5px 20px rgba(0,0,0,.15);
    max-width:500px;
    margin:auto;
    margin-top:60px;
}

.card{
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,.08);
}

.totalbox{
    background:#fff8dc;
    padding:20px;
    border-radius:15px;
    text-align:center;
    font-size:32px;
    font-weight:bold;
    color:#d62828;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# DATA FOLDER
# ==============================

if not os.path.exists("data"):
    os.makedirs("data")

ORDERS_FILE = "data/orders.csv"

if not os.path.exists(ORDERS_FILE):

    with open(ORDERS_FILE,"w",newline="",encoding="utf-8") as f:

        writer=csv.writer(f)

        writer.writerow([
            "OrderNo",
            "Date",
            "Time",
            "Staff",
            "Items",
            "Total"
        ])

# ==============================
# SESSION
# ==============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "staff" not in st.session_state:
    st.session_state.staff=""

if "cart" not in st.session_state:
    st.session_state.cart=[]

if "order_no" not in st.session_state:
    st.session_state.order_no=1001

# ==============================
# LOGIN
# ==============================

if not st.session_state.logged_in:

    st.markdown('<div class="loginbox">',unsafe_allow_html=True)

    st.markdown(
        '<div class="header">🍔 Affan\'s Kitchen</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subheader">Restaurant POS System</div>',
        unsafe_allow_html=True
    )

    staff=st.text_input(
        "Staff Name"
    )

    password=st.text_input(
        "Password",
        type="password"
    )

    if st.button("LOGIN"):

        if password=="112233":

            st.session_state.logged_in=True
            st.session_state.staff=staff
            st.rerun()

        else:

            st.error("Wrong Password")

    st.markdown("</div>",unsafe_allow_html=True)

    st.stop()

# ==============================
# HEADER
# ==============================

st.markdown(
f"""
<div class="header">
🍔 AFFAN'S KITCHEN POS
</div>
""",
unsafe_allow_html=True
)

left,right=st.columns([2,1])

with right:

    st.success(f"👨 Staff : {st.session_state.staff}")

    st.info(datetime.now().strftime("%d-%b-%Y %I:%M %p"))
# ==============================
# MENU DATA
# ==============================

MENU = {
    "🍳 Breakfast": {
        "Paratha": 180,
        "Omelette": 250,
        "Halwa Puri": 320,
        "Tea": 120,
        "Coffee": 180,
    },
    "🍛 Lunch": {
        "Chicken Biryani": 450,
        "Beef Biryani": 520,
        "Chicken Karahi": 1450,
        "Chicken Handi": 1650,
        "Daal": 280,
        "Naan": 40,
    },
    "🍔 Fast Food": {
        "Zinger Burger": 520,
        "Beef Burger": 650,
        "Chicken Shawarma": 350,
        "Fries": 250,
        "Pizza Slice": 300,
        "Club Sandwich": 420,
    },
    "🥤 Drinks": {
        "Cold Drink": 120,
        "Mineral Water": 80,
        "Fresh Lime": 180,
        "Mint Margarita": 220,
    }
}

# ==============================
# MENU SECTION
# ==============================

with left:

    st.subheader("🍽️ Menu")

    tabs = st.tabs(list(MENU.keys()))

    for tab, category in zip(tabs, MENU.keys()):

        with tab:

            items = MENU[category]

            cols = st.columns(2)

            index = 0

            for item_name, price in items.items():

                with cols[index % 2]:

                    if st.button(
                        f"{item_name}\n\nRs {price}",
                        key=f"{category}_{item_name}",
                        use_container_width=True,
                    ):

                        st.session_state.cart.append(
                            {
                                "item": item_name,
                                "price": price,
                                "qty": 1,
                                "time": datetime.now().strftime("%I:%M:%S %p"),
                            }
                        )

                        st.toast(f"{item_name} added to cart")

                        st.rerun()

                index += 1
                # ==============================
# CART
# ==============================

with right:

    st.subheader("🛒 Current Order")

    total = 0

    if len(st.session_state.cart) == 0:

        st.info("Cart is empty")

    else:

        remove_item = None

        for i, item in enumerate(st.session_state.cart):

            subtotal = item["price"] * item["qty"]

            total += subtotal

            with st.container(border=True):

                st.markdown(f"### {item['item']}")

                st.caption(f"Added: {item['time']}")

                c1, c2, c3 = st.columns([1,1,1])

                with c1:

                    if st.button("➖", key=f"minus_{i}"):

                        if item["qty"] > 1:

                            st.session_state.cart[i]["qty"] -= 1

                        else:

                            remove_item = i

                        st.rerun()

                with c2:

                    st.markdown(
                        f"<h3 style='text-align:center'>{item['qty']}</h3>",
                        unsafe_allow_html=True
                    )

                with c3:

                    if st.button("➕", key=f"plus_{i}"):

                        st.session_state.cart[i]["qty"] += 1

                        st.rerun()

                st.write(f"Price : Rs {item['price']}")

                st.write(f"Subtotal : Rs {subtotal}")

                if st.button("❌ Remove", key=f"remove_{i}"):

                    remove_item = i

                    st.rerun()

        if remove_item is not None:

            st.session_state.cart.pop(remove_item)

            st.rerun()

        st.markdown("---")

        st.markdown(
            f"""
            <div class="totalbox">
                TOTAL<br>
                Rs {total}
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

        st.session_state.current_total = total

        st.session_state.current_datetime = datetime.now().strftime(
            "%d-%b-%Y %I:%M:%S %p"
        )

        st.success(
            f"Order #{st.session_state.order_no} Ready"
        )

        st.rerun()

        with col2:

           with col2:

    if st.button(
        "✅ Checkout",
        use_container_width=True
    ):

        st.session_state.current_total = total

        st.session_state.current_datetime = datetime.now().strftime(
            "%d-%b-%Y %I:%M:%S %p"
        )

        st.success(
            f"Order #{st.session_state.order_no} Ready"
        )

        st.rerun()
    # ==============================
# RECEIPT
# ==============================

st.divider()

st.subheader("🧾 Receipt")

if len(st.session_state.cart) > 0:

    total = 0

    receipt_items = []

    for item in st.session_state.cart:

        subtotal = item["price"] * item["qty"]

        total += subtotal

        receipt_items.append({
            "Item": item["item"],
            "Qty": item["qty"],
            "Price": item["price"],
            "Total": subtotal
        })

    st.markdown("""
    <style>

    .receipt{

        background:white;
        border:2px dashed #444;
        border-radius:15px;
        padding:20px;

    }

    .title{

        color:#D62828;
        font-size:30px;
        font-weight:bold;

    }

    .small{

        color:gray;

    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="receipt">', unsafe_allow_html=True)

    c1,c2 = st.columns([1,3])

    with c1:

        if os.path.exists("assets/logo.png"):

            st.image("assets/logo.png", width=90)

        else:

            st.markdown("# 🍔")

    with c2:

        st.markdown(
            """
            <div class="title">
            Affan's Kitchen
            </div>

            <div class="small">
            Restaurant & Fast Food
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    info1,info2 = st.columns(2)

    with info1:

        st.write(f"**Order #:** {st.session_state.order_no}")
        st.write(f"**Staff:** {st.session_state.staff}")

    with info2:

        st.write(
            datetime.now().strftime("%d-%b-%Y")
        )

        st.write(
            datetime.now().strftime("%I:%M:%S %p")
        )

    st.markdown("---")

    receipt_df = pd.DataFrame(receipt_items)

    st.dataframe(
        receipt_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.markdown(
        f"""
        <h2 style='text-align:right;color:#D62828'>
        Total : Rs {total}
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.success("Thank you for visiting Affan's Kitchen ❤️")

    if st.button("🖨️ Complete Order", use_container_width=True):

    # Save order to CSV
    with open(ORDERS_FILE, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        items = [
            f"{i['item']} x{i['qty']}"
            for i in st.session_state.cart
        ]

        writer.writerow([
            st.session_state.order_no,
            datetime.now().strftime("%d-%m-%Y"),
            datetime.now().strftime("%I:%M:%S %p"),
            st.session_state.staff,
            ", ".join(items),
            total
        ])

    # Increase order number AFTER saving
    st.session_state.order_no += 1

    # Clear cart
    st.session_state.cart = []

    # Success message
    st.success("✅ Order Completed Successfully!")

    # 🎈 Balloons only here
    st.balloons()

    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

else:

    st.info("Receipt will appear after adding items.")
# ============================================
# DASHBOARD
# ============================================

st.divider()

st.subheader("📊 Manager Dashboard")

if os.path.exists(ORDERS_FILE):

    try:

        orders = pd.read_csv(ORDERS_FILE)

        if len(orders) > 0:

            today = datetime.now().strftime("%d-%m-%Y")

            today_orders = orders[
                orders["Date"] == today
            ]

            total_orders = len(today_orders)

            total_sales = today_orders["Total"].sum()

            avg_bill = (
                round(total_sales / total_orders, 2)
                if total_orders > 0 else 0
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Today's Orders",
                total_orders
            )

            c2.metric(
                "Today's Sales",
                f"Rs {total_sales}"
            )

            c3.metric(
                "Average Bill",
                f"Rs {avg_bill}"
            )

            st.markdown("---")

            st.subheader("👨 Staff Sales")

            if len(today_orders) > 0:

                staff_sales = (
                    today_orders
                    .groupby("Staff")["Total"]
                    .sum()
                    .reset_index()
                )

                st.dataframe(
                    staff_sales,
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("---")

            st.subheader("📜 Today's Orders")

            st.dataframe(
                today_orders,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No orders yet.")

    except Exception as e:

        st.error(f"Dashboard Error: {e}")
        # ============================================
# SIDEBAR MANAGER
# ============================================

st.sidebar.title("🍔 Affan's Kitchen")

page = st.sidebar.radio(
    "Navigation",
    [
        "🍔 POS",
        "📊 Dashboard",
        "📜 Order History"
    ]
)

# ============================================
# ORDER HISTORY
# ============================================

if page == "📜 Order History":

    st.title("📜 Order History")

    if os.path.exists(ORDERS_FILE):

        df = pd.read_csv(ORDERS_FILE)

        if len(df) == 0:

            st.info("No Orders Found")

        else:

            search = st.text_input(
                "🔍 Search Order / Staff"
            )

            if search:

                df = df[
                    df.astype(str)
                    .apply(
                        lambda x: x.str.contains(
                            search,
                            case=False
                        )
                    )
                    .any(axis=1)
                ]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "⬇ Download Orders CSV",
                df.to_csv(index=False),
                file_name="orders.csv",
                mime="text/csv"
            )

    st.stop()

# ============================================
# DASHBOARD PAGE
# ============================================

if page == "📊 Dashboard":

    st.title("📊 Sales Dashboard")

    if os.path.exists(ORDERS_FILE):

        df = pd.read_csv(ORDERS_FILE)

        if len(df):

            today = datetime.now().strftime("%d-%m-%Y")

            today_df = df[df["Date"] == today]

            col1,col2,col3 = st.columns(3)

            col1.metric(
                "Orders",
                len(today_df)
            )

            col2.metric(
                "Revenue",
                f"Rs {today_df['Total'].sum()}"
            )

            average = (
                round(
                    today_df["Total"].mean(),
                    2
                )
                if len(today_df)
                else 0
            )

            col3.metric(
                "Average Bill",
                f"Rs {average}"
            )

            st.markdown("---")

            st.subheader("👨 Staff Sales")

            if len(today_df):

                staff = (
                    today_df
                    .groupby("Staff")
                    ["Total"]
                    .sum()
                    .reset_index()
                )

                st.dataframe(
                    staff,
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("---")

            st.subheader("🏆 Best Selling Items")

            item_counts = {}

            for items in df["Items"]:

                for item in str(items).split(","):

                    item = item.strip()

                    if item == "":
                        continue

                    name = item.split(" x")[0]

                    item_counts[name] = (
                        item_counts.get(name,0) + 1
                    )

            if item_counts:

                best = (
                    pd.DataFrame(
                        item_counts.items(),
                        columns=[
                            "Item",
                            "Sold"
                        ]
                    )
                    .sort_values(
                        "Sold",
                        ascending=False
                    )
                )

                st.dataframe(
                    best,
                    use_container_width=True,
                    hide_index=True
                )

    st.stop()
    # ============================================
# EXTRA ORDER DETAILS
# ============================================

st.sidebar.markdown("---")
st.sidebar.subheader("⚙ Order Settings")

payment_method = st.sidebar.selectbox(
    "Payment Method",
    [
        "Cash",
        "Card",
        "JazzCash",
        "EasyPaisa"
    ]
)

customer_name = st.sidebar.text_input(
    "Customer Name (Optional)"
)

# ============================================
# SAVE EXTRA DETAILS
# ============================================

if not os.path.exists(ORDERS_FILE):

    with open(
        ORDERS_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "OrderNo",
            "Date",
            "Time",
            "Staff",
            "Customer",
            "Payment",
            "Status",
            "Items",
            "Total"
        ])

# ============================================
# RECEIPT REPRINT
# ============================================

if page == "📜 Order History":

    st.subheader("🖨 Reprint Receipt")

    if len(df):

        order_list = df["OrderNo"].tolist()

        selected = st.selectbox(
            "Select Order",
            order_list
        )

        if st.button("View Receipt"):

            receipt = df[
                df["OrderNo"] == selected
            ].iloc[0]

            st.markdown("## 🧾 Receipt")

            left_logo, right_title = st.columns([1,3])

            with left_logo:

                if os.path.exists("assets/logo.png"):

                    st.image(
                        "assets/logo.png",
                        width=80
                    )

            with right_title:

                st.markdown(
                    "## Affan's Kitchen"
                )

                st.caption(
                    "Restaurant & Fast Food"
                )

            st.write(
                f"Order : {receipt['OrderNo']}"
            )

            st.write(
                f"Date : {receipt['Date']} {receipt['Time']}"
            )

            st.write(
                f"Staff : {receipt['Staff']}"
            )

            if "Customer" in receipt:

                st.write(
                    f"Customer : {receipt['Customer']}"
                )

            if "Payment" in receipt:

                st.write(
                    f"Payment : {receipt['Payment']}"
                )

            st.write("---")

            st.write(receipt["Items"])

            st.write("---")

            st.markdown(
                f"## Total : Rs {receipt['Total']}"
            )

# ============================================
# DAILY SALES SUMMARY
# ============================================

if page == "📊 Dashboard":

    st.markdown("---")

    st.subheader("📅 Daily Summary")

    if len(today_df):

        st.success(
            f"""
Total Orders : {len(today_df)}

Today's Sales : Rs {today_df['Total'].sum()}
"""
        )

# ============================================
# BIG BUTTON STYLE
# ============================================

st.markdown("""
<style>

div.stButton > button{

height:75px;

font-size:22px;

font-weight:bold;

border-radius:18px;

transition:0.25s;

}

div.stButton > button:hover{

transform:scale(1.03);

}

</style>
""", unsafe_allow_html=True)
# ============================================
# SETTINGS / ADMIN
# ============================================

st.sidebar.markdown("---")

admin = st.sidebar.checkbox("⚙ Admin Panel")

if admin:

    st.header("⚙ Admin Panel")

    tab1, tab2, tab3 = st.tabs(
        [
            "📈 Reports",
            "🍔 Menu",
            "💾 Backup"
        ]
    )

    # ====================================
    # REPORTS
    # ====================================

    with tab1:

        st.subheader("Sales Report")

        if os.path.exists(ORDERS_FILE):

            report = pd.read_csv(ORDERS_FILE)

            if len(report):

                st.metric(
                    "Total Orders",
                    len(report)
                )

                st.metric(
                    "Total Sales",
                    f"Rs {report['Total'].sum()}"
                )

                report["Month"] = pd.to_datetime(
                    report["Date"],
                    dayfirst=True,
                    errors="coerce"
                ).dt.strftime("%Y-%m")

                monthly = (
                    report.groupby("Month")["Total"]
                    .sum()
                    .reset_index()
                )

                st.subheader("Monthly Sales")

                st.bar_chart(
                    monthly.set_index("Month")
                )

    # ====================================
    # MENU MANAGER
    # ====================================

    with tab2:

        st.subheader("Current Menu")

        menu_rows = []

        for category, items in MENU.items():

            for name, price in items.items():

                menu_rows.append(
                    {
                        "Category": category,
                        "Item": name,
                        "Price": price
                    }
                )

        st.dataframe(
            pd.DataFrame(menu_rows),
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "Dynamic menu editing will be added in the next version."
        )

    # ====================================
    # BACKUP
    # ====================================

    with tab3:

        st.subheader("Backup Orders")

        if os.path.exists(ORDERS_FILE):

            with open(
                ORDERS_FILE,
                "rb"
            ) as f:

                st.download_button(
                    "⬇ Download Backup",
                    f,
                    file_name="AffansKitchen_Orders.csv",
                    mime="text/csv"
                )

            st.success("Backup ready.")

# ============================================
# FOOTER
# ============================================

st.markdown("---")

st.markdown(
    """
    <div style='text-align:center;color:gray'>
        🍔 <b>Affan's Kitchen POS</b><br>
        Version 1.0
    </div>
    """,
    unsafe_allow_html=True
)
