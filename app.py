"""
app.py
------
Main Flask application for the Canteen Management System.

Routes:
  /           Home page
  /menu       View all menu items
  /order      Place a new order
  /cart       View / manage cart
  /bill       Generate final bill
  /reports    View sales reports

All CRUD operations use SQLite via the helper functions below.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_connection
from models import Customer, Menu, Order, Bill

app = Flask(__name__)
app.secret_key = "canteen_secret_key_2024"  # needed for flash messages


# ============================================================
#  DATABASE HELPERS
# ============================================================

def fetch_menu():
    """Fetch all menu items from the database."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM menu ORDER BY category, item_name").fetchall()
    conn.close()
    return rows


def fetch_cart():
    """Fetch all cart items."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cart ORDER BY cart_id").fetchall()
    conn.close()
    return rows


def fetch_orders():
    """Fetch all confirmed orders."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM orders ORDER BY order_date DESC").fetchall()
    conn.close()
    return rows


# ============================================================
#  ROUTE: HOME
# ============================================================
@app.route("/")
def home():
    """Landing / welcome page."""
    return render_template("home.html")


# ============================================================
#  ROUTE: MENU
# ============================================================
@app.route("/menu")
def menu():
    """
    Display all menu items grouped by category.
    Uses the Menu model class for OOP demonstration.
    """
    rows = fetch_menu()
    menu_obj = Menu()
    menu_obj.load_from_db(rows)

    # Group items by category for nicer display
    grouped = {}
    for item in menu_obj.get_all():
        cat = item["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(item)

    return render_template("menu.html", grouped=grouped)


# ============================================================
#  ROUTE: ORDER
# ============================================================
@app.route("/order", methods=["GET", "POST"])
def order():
    """Place a new order — add items to cart."""
    menu_items = fetch_menu()

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        item_id = request.form.get("item_id", "")
        quantity = request.form.get("quantity", "")

        # ---------- Validation ----------
        errors = []
        if not customer_name:
            errors.append("Customer name is required.")
        if not item_id:
            errors.append("Please select a food item.")
        if not quantity:
            errors.append("Quantity is required.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("order.html", menu_items=menu_items)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                flash("Quantity must be at least 1.", "error")
                return render_template("order.html", menu_items=menu_items)
        except ValueError:
            flash("Quantity must be a valid number.", "error")
            return render_template("order.html", menu_items=menu_items)

        # Fetch item price
        conn = get_connection()
        item = conn.execute(
            "SELECT * FROM menu WHERE item_id = ?", (item_id,)
        ).fetchone()
        conn.close()

        if not item:
            flash("Invalid menu item selected.", "error")
            return render_template("order.html", menu_items=menu_items)

        price = item["price"]
        total = round(price * quantity, 2)

        # Insert into cart
        conn = get_connection()
        conn.execute(
            "INSERT INTO cart (item_id, item_name, price, quantity, total) "
            "VALUES (?, ?, ?, ?, ?)",
            (item["item_id"], item["item_name"], price, quantity, total)
        )
        conn.commit()
        conn.close()

        flash(f"'{item['item_name']}' × {quantity} added to cart!", "success")
        return redirect(url_for("order"))

    return render_template("order.html", menu_items=menu_items)


# ============================================================
#  ROUTE: CART
# ============================================================
@app.route("/cart")
def view_cart():
    """View cart items and totals."""
    cart_items = fetch_cart()
    total_amount = sum(item["total"] for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total_amount=total_amount)


@app.route("/cart/remove/<int:cart_id>")
def remove_from_cart(cart_id):
    """Remove a single item from the cart."""
    conn = get_connection()
    conn.execute("DELETE FROM cart WHERE cart_id = ?", (cart_id,))
    conn.commit()
    conn.close()
    flash("Item removed from cart.", "info")
    return redirect(url_for("view_cart"))


@app.route("/cart/update/<int:cart_id>", methods=["POST"])
def update_cart(cart_id):
    """Update quantity of a cart item."""
    new_qty = request.form.get("quantity", "1")

    try:
        new_qty = int(new_qty)
        if new_qty <= 0:
            flash("Quantity must be at least 1.", "error")
            return redirect(url_for("view_cart"))
    except ValueError:
        flash("Invalid quantity.", "error")
        return redirect(url_for("view_cart"))

    conn = get_connection()
    item = conn.execute("SELECT * FROM cart WHERE cart_id = ?", (cart_id,)).fetchone()
    if item:
        new_total = round(item["price"] * new_qty, 2)
        conn.execute(
            "UPDATE cart SET quantity = ?, total = ? WHERE cart_id = ?",
            (new_qty, new_total, cart_id)
        )
        conn.commit()
        flash("Quantity updated.", "success")
    conn.close()
    return redirect(url_for("view_cart"))


# ============================================================
#  ROUTE: BILL  (Final checkout)
# ============================================================
@app.route("/bill", methods=["GET", "POST"])
def bill():
    """
    Generate the final bill using the Bill class.
    On POST: confirm order, move cart items to orders table, then clear cart.
    """
    cart_items = fetch_cart()

    if not cart_items:
        flash("Cart is empty! Add items before generating a bill.", "error")
        return redirect(url_for("order"))

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()

        if not customer_name:
            flash("Please enter your name.", "error")
            # Recalculate bill for display
            bill_obj = Bill("Guest", cart_items)
            return render_template("bill.html",
                                   bill=bill_obj.get_summary(),
                                   cart_items=cart_items)

        # Create Bill object (OOP)
        bill_obj = Bill(customer_name, cart_items)

        # Save each cart item as an order in the database
        conn = get_connection()
        for item in cart_items:
            conn.execute(
                "INSERT INTO orders (customer_name, item_name, quantity, "
                "total_price, order_date) VALUES (?, ?, ?, ?, datetime('now'))",
                (customer_name, item["item_name"], item["quantity"], item["total"])
            )
        # Clear the cart
        conn.execute("DELETE FROM cart")
        conn.commit()
        conn.close()

        flash(f"Order placed successfully! Grand Total: ₹{bill_obj.grand_total}", "success")
        return render_template("bill.html",
                               bill=bill_obj.get_summary(),
                               cart_items=cart_items,
                               confirmed=True)

    # GET — just show bill preview
    bill_obj = Bill("Guest", cart_items)
    return render_template("bill.html",
                           bill=bill_obj.get_summary(),
                           cart_items=cart_items,
                           confirmed=False)


# ============================================================
#  ROUTE: REPORTS
# ============================================================
@app.route("/reports")
def reports():
    """Display sales reports: total orders, revenue, most/least ordered items."""
    conn = get_connection()

    # Total orders
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    # Total revenue
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(total_price), 0) FROM orders"
    ).fetchone()[0]

    # Most ordered item
    most_ordered = conn.execute("""
        SELECT item_name, SUM(quantity) AS total_qty
        FROM orders
        GROUP BY item_name
        ORDER BY total_qty DESC
        LIMIT 1
    """).fetchone()

    # Least ordered item
    least_ordered = conn.execute("""
        SELECT item_name, SUM(quantity) AS total_qty
        FROM orders
        GROUP BY item_name
        ORDER BY total_qty ASC
        LIMIT 1
    """).fetchone()

    # Recent orders (last 20)
    recent = conn.execute(
        "SELECT * FROM orders ORDER BY order_date DESC LIMIT 20"
    ).fetchall()

    conn.close()

    return render_template(
        "reports.html",
        total_orders=total_orders,
        total_revenue=total_revenue,
        most_ordered=most_ordered,
        least_ordered=least_ordered,
        recent_orders=recent,
    )


# ============================================================
#  ERROR HANDLERS
# ============================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("home.html"), 404


# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    # Initialise the database (creates tables + seeds menu)
    init_db()
    # Run the Flask dev server
    app.run(debug=True, host="0.0.0.0", port=5000)
