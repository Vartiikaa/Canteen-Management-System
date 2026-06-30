"""
models.py
---------
Contains all OOP classes for the Canteen Management System.

Demonstrates:
  - Classes & Objects
  - __init__ (Constructor)
  - Inheritance (Customer inherits Person)
  - Polymorphism (Method Overriding via get_details())
  - Encapsulation (Private attributes with getters/setters)
  - Lists and Dictionaries
"""

from datetime import datetime


# ============================================================
#  PERSON  (Base Class)
# ============================================================
class Person:
    """Base class representing any person in the system."""

    def __init__(self, name: str, phone: str = ""):
        # Private (encapsulated) attributes — convention: _name, _phone
        self._name = name
        self._phone = phone

    # ---- Getter / Setter for name (Encapsulation) ----
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if value.strip():
            self._name = value.strip()
        else:
            raise ValueError("Name cannot be empty")

    # ---- Getter / Setter for phone ----
    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        self._phone = value

    def get_details(self) -> str:
        """Return basic details. (Overridden in child class — Polymorphism)"""
        return f"Name: {self._name} | Phone: {self._phone}"


# ============================================================
#  CUSTOMER  (Inherits Person)
# ============================================================
class Customer(Person):
    """
    Represents a customer.
    Inherits name/phone from Person and adds order history.
    """

    def __init__(self, name: str, phone: str = "", customer_id: int = 0):
        super().__init__(name, phone)           # call parent constructor
        self._customer_id = customer_id
        self._orders = []                       # list to hold order objects

    # ---- Getter / Setter ----
    @property
    def customer_id(self) -> int:
        return self._customer_id

    @customer_id.setter
    def customer_id(self, value: int):
        self._customer_id = value

    @property
    def orders(self) -> list:
        return self._orders

    def add_order(self, order):
        """Add an Order object to the customer's history."""
        self._orders.append(order)

    # ---- Overriding get_details (Polymorphism) ----
    def get_details(self) -> str:
        base = super().get_details()
        return f"{base} | Customer ID: {self._customer_id} | Orders: {len(self._orders)}"


# ============================================================
#  MENU  (Represents the food catalogue)
# ============================================================
class Menu:
    """
    Manages menu items.  Uses a dictionary to hold items loaded from DB.
    """

    def __init__(self):
        self._items = {}   # {item_id: {"item_name":..., "category":..., "price":...}}

    def load_from_db(self, rows):
        """Populate the menu dictionary from database rows."""
        self._items.clear()
        for row in rows:
            self._items[row["item_id"]] = {
                "item_id":   row["item_id"],
                "item_name": row["item_name"],
                "category":  row["category"],
                "price":     row["price"],
            }

    def get_all(self) -> list:
        """Return all menu items as a list of dicts."""
        return list(self._items.values())

    def get_by_id(self, item_id: int) -> dict:
        """Return a single item by ID, or None."""
        return self._items.get(item_id)

    def get_price(self, item_id: int) -> float:
        """Return the price of a specific item."""
        item = self._items.get(item_id)
        return item["price"] if item else 0.0


# ============================================================
#  ORDER  (Handles a single order transaction)
# ============================================================
class Order:
    """
    Represents one order entry (one line item).
    Multiple Order objects can make up a customer's cart.
    """

    def __init__(self, customer_name: str, item_name: str,
                 quantity: int, total_price: float):
        self.customer_name = customer_name
        self.item_name = item_name
        self.quantity = quantity
        self.total_price = total_price
        self.order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_summary(self) -> dict:
        """Return order data as a dictionary (handy for templates)."""
        return {
            "customer_name": self.customer_name,
            "item_name":     self.item_name,
            "quantity":      self.quantity,
            "total_price":   self.total_price,
            "order_date":    self.order_date,
        }


# ============================================================
#  BILL  (Generates final bill from cart)
# ============================================================
class Bill:
    """
    Takes a list of cart items and calculates the final bill.
    Demonstrates list processing, encapsulation, and basic math.
    """

    def __init__(self, customer_name: str, cart_items: list):
        self._customer_name = customer_name
        self._cart_items = cart_items   # list of dicts
        self._subtotal = 0.0
        self._tax_rate = 0.05           # 5% tax
        self._tax_amount = 0.0
        self._grand_total = 0.0
        self._calculate()

    # ---- Private helper (Encapsulation) ----
    def _calculate(self):
        """Calculate subtotal, tax, and grand total."""
        self._subtotal = sum(item["total"] for item in self._cart_items)
        self._tax_amount = round(self._subtotal * self._tax_rate, 2)
        self._grand_total = round(self._subtotal + self._tax_amount, 2)

    # ---- Read-only properties ----
    @property
    def subtotal(self) -> float:
        return self._subtotal

    @property
    def tax_rate(self) -> float:
        return self._tax_rate

    @property
    def tax_amount(self) -> float:
        return self._tax_amount

    @property
    def grand_total(self) -> float:
        return self._grand_total

    @property
    def customer_name(self) -> str:
        return self._customer_name

    @property
    def cart_items(self) -> list:
        return self._cart_items

    def get_summary(self) -> dict:
        """Return full bill summary."""
        return {
            "customer_name": self._customer_name,
            "item_list":     self._cart_items,
            "subtotal":      self._subtotal,
            "tax_rate":      self._tax_rate * 100,
            "tax_amount":    self._tax_amount,
            "grand_total":   self._grand_total,
        }
