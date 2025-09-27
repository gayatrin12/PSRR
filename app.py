import streamlit as st # type: ignore
from datetime import datetime
import io
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://gayatrinikumbh816_db_user:UPX9juLsCmmrpr2I@cluster1.fvhowp4.mongodb.net/myDatabase?retryWrites=true&w=majority&appName=Cluster1"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
# -------------------------
# Page Settings
# -------------------------
st.set_page_config(page_title="THE PURPLE SPOON", layout="centered")

# -------------------------
# Admin Credentials
# -------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# -------------------------
# Session State Init
# -------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "orders" not in st.session_state:
    st.session_state.orders = []
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "table_no" not in st.session_state:
    st.session_state.table_no = ""
if "invoice_no" not in st.session_state:
    st.session_state.invoice_no = 1

# -------------------------
# Bill Generator Function
# -------------------------
def generate_bill_text(order):
    output = io.StringIO()
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%I:%M %p")
    invoice_no = order["invoice_no"]

    output.write("------------------------------------------\n")
    output.write("      🍽️ Purple Spoon Restaurant\n")
    output.write("           Tax Invoice / Bill\n")
    output.write("------------------------------------------\n")
    output.write(f"Invoice No: INV-{invoice_no:04d}\n")
    output.write(f"Table No: {order['table_no']}\n")
    output.write(f"Date: {date}\n")
    output.write(f"Time: {time}\n\n")

    output.write("Items:\n")
    subtotal = 0
    for item in order["items"]:
        line_total = item["qty"] * item["price"]
        subtotal += line_total
        output.write(f" - {item['title']} × {item['qty']} = ₹{line_total}\n")

    gst = round(subtotal * 0.05, 2)
    total = round(subtotal + gst, 2)

    output.write(f"\nSubtotal: ₹{subtotal:.2f}\n")
    output.write(f"GST (5%): ₹{gst:.2f}\n")
    output.write(f"Total: ₹{total:.2f}\n")
    output.write("\n------------------------------------------\n")
    output.write("   Thank you for dining with us! 😊\n")
    output.write("------------------------------------------\n")

    bill_text = output.getvalue()
    output.close()
    return bill_text

# -------------------------
# Menu Data
# -------------------------
categorized_menu = {
    "Snacks": [
        {"id": "sandwich", "title": "Cheese Sandwich", "desc": "Grilled cheese sandwich", "price": 60,
         "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTsTpSojm3atPxfcFPHcX6GE674abx_Zb0F6oBL75lFNEFgwsumz6UHCl9-mH7Vt83GS1c&usqp=CAU"},
        {"id": "french_fries", "title": "French Fries", "desc": "Crispy golden fries", "price": 80,
         "img": "https://static.vecteezy.com/system/resources/previews/027/536/411/non_2x/delicious-french-fries-on-a-white-background-photo.jpg"},
        {"id": "veg_pakora", "title": "Veg Pakora", "desc": "Spicy vegetable fritters", "price": 70,
         "img": "https://www.indianhealthyrecipes.com/wp-content/uploads/2022/02/vegetable-pakora-recipe.jpg"},
    ],
    "Main Course": [
        {"id": "pasta", "title": "White Sauce Pasta", "desc": "Creamy pasta", "price": 150,
         "img": "https://www.reciperasoi.com/wp-content/uploads/2021/02/White-Sauce-Pasta.jpg"},
        {"id": "paratha", "title": "Aloo Paratha", "desc": "Spicy potato stuffed paratha", "price": 90,
         "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTxNJiuPVKv48BB7Tz2wVfLjMyLvPnatfq1vg&s"},
        {"id": "paneer_butter_masala", "title": "Paneer Butter Masala", "desc": "Paneer cubes in creamy tomato gravy", "price": 180,
         "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSXuJq5UB6iQvPawZmR2te-Obw6VSHsktC5MQ&s"},
        {"id": "chicken_biryani", "title": "Chicken Biryani", "desc": "Aromatic spiced chicken rice", "price": 250,
         "img": "https://www.tamarindnthyme.com/wp-content/uploads/2019/08/Chicken-Masala-Biryani-500x500.jpg"},
    ],
    "South Indian": [
        {"id": "idli", "title": "Idli Sambar", "desc": "Soft idli with sambar", "price": 90,
         "img": "https://static.toiimg.com/thumb/msid-113810989,width-1280,height-720,resizemode-4/113810989.jpg"},
        {"id": "dosa", "title": "Masala Dosa", "desc": "Crispy dosa with potato filling", "price": 110,
         "img": "https://ranveerbrar.com/wp-content/uploads/2021/02/Masala-dosa-scaled.jpg"},
        {"id": "vada", "title": "Medu Vada", "desc": "Fried lentil doughnuts", "price": 80,
         "img": "https://bonmasala.com/wp-content/uploads/2022/12/medu-vada-recipe.webp"},
    ],
    "Beverages": [
        {"id": "coffee", "title": "Coffee", "desc": "Freshly brewed coffee", "price": 50,
         "img": "https://www.deliciouslyindian.net/wp-content/uploads/2022/02/IMG_0234-1-scaled.jpg"},
        {"id": "masala_tea", "title": "Masala Tea", "desc": "Spiced Indian tea", "price": 40,
         "img": "https://budleaf.com/wp-content/uploads/2023/04/How-to-make-masala-chai-1568x1039.jpeg"},
        {"id": "lemonade", "title": "Lemonade", "desc": "Refreshing lemon drink", "price": 60,
         "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTIZKj7hitzLIYc6TZ6KwFCSRkgXv77cOkkDA&s"},
    ]
}

# -------------------------
# Customer UI
# -------------------------
def customer_ui():
    st.markdown("<h1 style='text-align: center; color:#6A1B9A;'> THE PURPLE SPOON RESTRAUNT </h1>", unsafe_allow_html=True)

    # Table number input
    if not st.session_state.table_no:
        table_input = st.text_input("🔢 Enter your Table Number", placeholder="e.g. 12", key="table_input")
        if table_input.strip():
            st.session_state.table_no = table_input.strip()

    if not st.session_state.table_no:
        st.warning("Please enter your table number to continue.")
        st.stop()

    st.info(f"📍 Current Table No: {st.session_state.table_no}")
    if st.button("❌ Change Table Number"):
        st.session_state.table_no = ""
        st.rerun()

    search = st.text_input("🔍 Search menu...")

    tabs = st.tabs(list(categorized_menu.keys()))

    for idx, category in enumerate(categorized_menu):
        with tabs[idx]:
            filtered_items = [item for item in categorized_menu[category] if not search or search.lower() in item["title"].lower()]
            if not filtered_items:
                st.write(f"No items found in {category}.")
            else:
                for item in filtered_items:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(item["img"], width=120)
                    with col2:
                        st.markdown(f"**{item['title']}**")
                        st.caption(item["desc"])
                        st.write(f"💰 ₹{item['price']}")
                        if st.button(f"Order {item['title']}", key=f"order_{item['id']}"):
                            if item["id"] not in st.session_state.cart:
                                st.session_state.cart[item["id"]] = {"title": item["title"], "qty": 0, "price": item["price"]}
                            st.session_state.cart[item["id"]]["qty"] += 1
                            st.success(f"{item['title']} added to cart!")
                            st.rerun()

    st.markdown("---")
    st.subheader("🛒 Your Cart")

    if not st.session_state.cart:
        st.caption("Your cart is empty.")
    else:
        total = 0
        items = []

        for item_id, item in list(st.session_state.cart.items()):
            cols = st.columns([4, 1, 1, 1])
            cols[0].write(f"**{item['title']}**")
            cols[1].write(f"₹{item['price']} × {item['qty']}")
            if cols[2].button("➕", key=f"plus_{item_id}"):
                st.session_state.cart[item_id]["qty"] += 1
                st.rerun()
            if cols[3].button("➖", key=f"minus_{item_id}"):
                st.session_state.cart[item_id]["qty"] -= 1
                if st.session_state.cart[item_id]["qty"] <= 0:
                    del st.session_state.cart[item_id]
                st.rerun()
            total += item["qty"] * item["price"]
            items.append(item)

        st.write(f"### 💵 Total: ₹{total}")

        col_clear, col_order = st.columns(2)

        if col_clear.button("🧹 Clear Cart"):
            st.session_state.cart = {}
            st.rerun()

        if col_order.button("✅ Place Order"):
            now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
            order = {
                "table_no": st.session_state.table_no,
                "items": items.copy(),
                "total": total,
                "status": "Pending",
                "timestamp": now,
                "invoice_no": st.session_state.invoice_no
            }

            # ✅ Save to MongoDB
            db = client["myDatabase"]
            orders_collection = db["orders"]
            result = orders_collection.insert_one(order)
            print(f"Order inserted into DB with ID: {result.inserted_id}")

            # ✅ Save in session (for display)
            st.session_state.orders.append(order)

            st.session_state.invoice_no += 1
            st.session_state.cart = {}
            st.success("🎉 Order placed and saved to database!")
            st.rerun()

    # 🧾 Show previous orders from session
    st.subheader("📝 Your Orders Status")
    has_orders = False
    for order in st.session_state.orders:
        if order["table_no"] == st.session_state.table_no:
            has_orders = True
            st.markdown(f"**Invoice:** INV-{order['invoice_no']:04d} | **Status:** {order['status']} | **Time:** {order['timestamp']}")
            for item in order["items"]:
                st.write(f"- {item['title']} × {item['qty']}")
            st.write(f"**Total:** ₹{order['total']}")

            # Bill generation if Served
            if order["status"] == "Served":
                if st.button(f"🧾 Generate Bill (INV-{order['invoice_no']:04d})", key=f"bill_{order['invoice_no']}"):
                    bill_text = generate_bill_text(order)
                    st.text_area("Generated Bill", bill_text, height=300)
                    st.download_button(
                        label="📥 Download Bill",
                        data=bill_text,
                        file_name=f"invoice_{order['invoice_no']:04d}.txt",
                        mime="text/plain"
                    )
            st.markdown("---")

    if not has_orders:
        st.caption("No orders placed yet.")


# -------------------------
# Admin Login
# -------------------------
def admin_login():
    st.markdown("<h1 style='text-align: center; color:#6A1B9A;'>Admin Login</h1>", unsafe_allow_html=True)

    username = st.text_input("Username", key="admin_username")
    password = st.text_input("Password", type="password", key="admin_password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials!")

# -------------------------
# Admin Dashboard
# -------------------------
def admin_dashboard():
    st.markdown("<h1 style='text-align: center; color:#6A1B9A;'>Admin Dashboard</h1>", unsafe_allow_html=True)

    # Connect to MongoDB
    db = client["myDatabase"]
    orders_collection = db["orders"]

    # ✅ Fetch all orders from the DB
    all_orders = list(orders_collection.find().sort("invoice_no", pymongo.ASCENDING))
    st.write(f"Total Orders: {len(all_orders)}")

    # 🔐 Logout button
    if st.button("Logout"):
        st.session_state.is_admin = False
        st.rerun()

    if not all_orders:
        st.info("No orders yet.")
        return

    for order in all_orders:
        st.markdown(f"### Invoice: INV-{order['invoice_no']:04d} | Table: {order['table_no']} | Status: {order['status']} | Time: {order['timestamp']}")

        for item in order["items"]:
            st.write(f"- {item['title']} × {item['qty']}")
        st.write(f"**Total:** ₹{order['total']}")

        # ✅ Mark as Served (update DB)
        if order["status"] == "Pending":
            if st.button(f"✅ Mark as Served (INV-{order['invoice_no']:04d})", key=f"serve_{order['invoice_no']}"):
                orders_collection.update_one(
                    {"invoice_no": order["invoice_no"]},
                    {"$set": {"status": "Served"}}
                )
                st.success(f"Order INV-{order['invoice_no']:04d} marked as Served.")
                st.rerun()

        # 🧾 Generate bill
        elif order["status"] == "Served":
            if st.button(f"🧾 Generate Bill (INV-{order['invoice_no']:04d})", key=f"admin_bill_{order['invoice_no']}"):
                bill_text = generate_bill_text(order)
                st.text_area("Generated Bill", bill_text, height=300, key=f"bill_text_area_{order['invoice_no']}")
                st.download_button(
                    label="📥 Download Bill as Text",
                    data=bill_text,
                    file_name=f"invoice_{order['invoice_no']:04d}.txt",
                    mime="text/plain",
                    key=f"admin_download_{order['invoice_no']}"
                )
        st.markdown("---")



# -------------------------
# Routing
# -------------------------
mode = st.sidebar.radio("Choose Mode", ["Customer", "Admin"])
if mode == "Admin":
    if st.session_state.is_admin:
        admin_dashboard()
    else:
        admin_login()
else:
    customer_ui()