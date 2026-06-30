# 🍽️ Canteen Management System

A simple **Canteen Management System** built as a B.Tech mini project using **Python (Flask)** and **HTML/CSS** with **SQLite** for database storage.

---

## Technologies Used

| Layer      | Tech              |
|------------|-------------------|
| Backend    | Python 3 + Flask  |
| Database   | SQLite            |
| Frontend   | HTML5 + CSS3      |
| Styling    | Custom CSS (Flexbox, CSS Variables) |

---

## Python Concepts Demonstrated

- ✅ **Classes & Objects** — `Person`, `Customer`, `Menu`, `Order`, `Bill`
- ✅ **Constructor (`__init__`)** — Every model class
- ✅ **Inheritance** — `Customer(Person)`
- ✅ **Polymorphism** — Method overriding: `get_details()` in `Customer`
- ✅ **Encapsulation** — Private attributes with `@property` getters/setters
- ✅ **Functions** — Modular helper functions throughout
- ✅ **Lists & Dictionaries** — Menu items, cart, bill summary
- ✅ **Exception Handling** — Try/except in quantity validation
- ✅ **File Handling** — SQLite database read/write operations

---

## Project Structure

```
Canteen-Management-System/
│
├── app.py              # Flask routes & main entry point
├── database.py         # SQLite connection + table creation + seed data
├── models.py           # OOP classes (Person, Customer, Menu, Order, Bill)
│
├── templates/
│   ├── home.html       # Landing page with features
│   ├── menu.html       # Menu display grouped by category
│   ├── order.html      # Order form to add items to cart
│   ├── cart.html       # Cart with update/remove functionality
│   ├── bill.html       # Bill preview & confirmed bill
│   └── reports.html    # Sales stats & recent orders
│
├── static/
│   └── style.css       # Complete custom stylesheet
│
├── database/
│   └── canteen.db      # SQLite database (auto-created)
│
└── README.md
```

---

## How To Run

### 1. Install Python Dependencies

```bash
pip install flask
```

### 2. Start the Application

```bash
python app.py
```

### 3. Open in Browser

Go to **http://localhost:5000**

---

## Features

| Module   | Description                                          |
|----------|------------------------------------------------------|
| Home     | Welcome page with feature cards and navigation       |
| Menu     | Browse 15 food items across Snacks, Drinks, & Meals  |
| Order    | Select items + quantity; validated input             |
| Cart     | Update quantities, remove items, see running total   |
| Bill     | Auto-calculated with 5% tax; confirm & clear cart    |
| Reports  | Total orders, revenue, most/least ordered items      |

---

## Database Schema

### `menu` Table
| Column     | Type    |
|------------|---------|
| item_id    | INTEGER (PK) |
| item_name  | TEXT    |
| category   | TEXT    |
| price      | REAL    |

### `orders` Table
| Column        | Type    |
|---------------|---------|
| order_id      | INTEGER (PK) |
| customer_name | TEXT    |
| item_name     | TEXT    |
| quantity      | INTEGER |
| total_price   | REAL    |
| order_date    | TEXT    |

### `cart` Table (temporary)
| Column    | Type    |
|-----------|---------|
| cart_id   | INTEGER (PK) |
| item_id   | INTEGER (FK → menu) |
| item_name | TEXT    |
| price     | REAL    |
| quantity  | INTEGER |
| total     | REAL    |

---

## License

This project is created for educational purposes as a B.Tech mini project.
