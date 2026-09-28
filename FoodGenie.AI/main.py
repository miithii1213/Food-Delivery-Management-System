import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import math
from datetime import datetime

DB_NAME = "foodgenie_professional.db"

# ================= PROFESSIONAL THEME =================
BG = "#F4F7FB"
WHITE = "#FFFFFF"
NAVY = "#10243E"
NAVY2 = "#173451"
TEXT = "#172B4D"
MUTED = "#6B7C93"
TEAL = "#10A89A"
TEAL_DARK = "#087F76"
CYAN = "#2CB7C9"
ORANGE = "#F59E0B"
RED = "#E45858"
GREEN = "#2EAD72"
PURPLE = "#7357D9"
BORDER = "#E2E8F0"

FONT = "Segoe UI"


class FoodGenie(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("FoodGenie.AI")
        self.geometry("1180x700")
        self.minsize(980, 600)
        self.configure(bg=BG)

        self.current_user = None
        self.current_role = None
        self.current_restaurant = None

        self.cart = []
        self.history = []
        self.live_after = None
        self.route_step = 0

        self.db = sqlite3.connect(DB_NAME)
        self.db.row_factory = sqlite3.Row

        self.setup_db()
        self.seed_data()

        self.show_login()

    # ==================================================
    # DATABASE
    # ==================================================

    def setup_db(self):

        c = self.db.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            name TEXT,
            phone TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS restaurants(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            location TEXT,
            rating REAL,
            cuisine TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS foods(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER,
            name TEXT,
            category TEXT,
            price REAL,
            description TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS riders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            vehicle TEXT,
            rating REAL,
            available INTEGER DEFAULT 1
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            restaurant_id INTEGER,
            items TEXT,
            total REAL,
            address TEXT,
            payment TEXT,
            status TEXT,
            rider_id INTEGER,
            created_at TEXT
        )
        """)

        self.db.commit()

    def seed_data(self):

        c = self.db.cursor()

        users = [
            ("demo", "1234", "customer", "Demo Customer", "9876500000"),
            ("pizza_hub", "1234", "restaurant", "Pizza Hub", "9876500001"),
            ("admin", "admin123", "admin", "FoodGenie Admin", "9876500002"),
            ("delivery", "1234", "delivery", "Arun Kumar", "9876543210"),
            ("rider2", "1234", "delivery", "Karthik S", "9876501234")
        ]

        for u in users:
            c.execute("""
            INSERT OR IGNORE INTO users
            (username,password,role,name,phone)
            VALUES(?,?,?,?,?)
            """, u)

        restaurants = [
            ("Pizza Hub", "RS Puram", 4.8, "Italian"),
            ("Burger House", "Gandhipuram", 4.6, "Fast Food"),
            ("Spice Garden", "Gandhipuram", 4.7, "Indian"),
            ("Pasta Palace", "Peelamedu", 4.5, "Italian"),
            ("Sweet Treats", "Saibaba Colony", 4.9, "Desserts"),
            ("South Bowl", "Race Course", 4.7, "South Indian")
        ]

        for r in restaurants:
            c.execute("""
            INSERT OR IGNORE INTO restaurants
            (name,location,rating,cuisine)
            VALUES(?,?,?,?)
            """, r)

        riders = [
            ("delivery", "Arun Kumar", "9876543210",
             "TN 38 AB 1234", 4.8),
            ("rider2", "Karthik S", "9876501234",
             "TN 38 CD 5678", 4.7)
        ]

        for r in riders:
            c.execute("""
            INSERT OR IGNORE INTO riders
            (username,name,phone,vehicle,rating,available)
            VALUES(?,?,?,?,?,1)
            """, r)

        food_map = {

            "Pizza Hub": [
                ("Margherita Pizza", "Pizza", 249,
                 "Classic tomato, mozzarella and basil"),
                ("Farmhouse Pizza", "Pizza", 349,
                 "Fresh vegetables with cheese"),
                ("Paneer Tikka Pizza", "Pizza", 379,
                 "Paneer tikka, onion and capsicum"),
                ("Chicken Pepperoni Pizza", "Pizza", 429,
                 "Pepperoni, cheese and herbs"),
                ("Garlic Bread", "Starter", 149,
                 "Buttery garlic bread")
            ],

            "Burger House": [
                ("Classic Veg Burger", "Burger", 159,
                 "Crispy veg patty and fresh lettuce"),
                ("Cheese Burger", "Burger", 199,
                 "Loaded cheese and juicy patty"),
                ("Chicken Burger", "Burger", 229,
                 "Grilled chicken with house sauce"),
                ("French Fries", "Starter", 99,
                 "Crispy salted fries"),
                ("Peri Peri Fries", "Starter", 129,
                 "Spicy peri peri fries")
            ],

            "Spice Garden": [
                ("Veg Biryani", "Biryani", 199,
                 "Aromatic basmati with vegetables"),
                ("Chicken Biryani", "Biryani", 279,
                 "Classic chicken biryani"),
                ("Paneer Butter Masala", "Main Course", 229,
                 "Creamy tomato paneer"),
                ("Chicken 65", "Starter", 219,
                 "Spicy fried chicken"),
                ("Ghee Rice", "Rice", 169,
                 "Fragrant rice with ghee")
            ],

            "Pasta Palace": [
                ("Alfredo Pasta", "Pasta", 259,
                 "Creamy white sauce pasta"),
                ("Arrabbiata Pasta", "Pasta", 239,
                 "Spicy tomato sauce pasta"),
                ("Pesto Pasta", "Pasta", 279,
                 "Basil pesto pasta"),
                ("Chicken Pasta", "Pasta", 299,
                 "Chicken with creamy pasta")
            ],

            "Sweet Treats": [
                ("Chocolate Brownie", "Dessert", 149,
                 "Warm chocolate brownie"),
                ("Choco Lava Cake", "Dessert", 179,
                 "Molten chocolate centre"),
                ("Strawberry Cheesecake", "Dessert", 229,
                 "Creamy cheesecake"),
                ("Gulab Jamun", "Dessert", 99,
                 "Soft syrup-soaked sweet")
            ],

            "South Bowl": [
                ("Masala Dosa", "South Indian", 99,
                 "Crispy dosa with masala"),
                ("Idli Vada", "South Indian", 89,
                 "Soft idli and crispy vada"),
                ("Podi Dosa", "South Indian", 119,
                 "Dosa with spicy podi"),
                ("South Indian Meals", "Meals", 179,
                 "Rice, sambar, poriyal and curd")
            ]
        }

        for restaurant, foods in food_map.items():

            row = c.execute(
                "SELECT id FROM restaurants WHERE name=?",
                (restaurant,)
            ).fetchone()

            rid = row["id"]

            for food in foods:

                exists = c.execute("""
                SELECT id FROM foods
                WHERE restaurant_id=? AND name=?
                """, (rid, food[0])).fetchone()

                if not exists:
                    c.execute("""
                    INSERT INTO foods
                    (restaurant_id,name,category,price,description)
                    VALUES(?,?,?,?,?)
                    """, (rid, *food))

        self.db.commit()

    # ==================================================
    # UI HELPERS
    # ==================================================

    def clear(self):

        if self.live_after:

            try:
                self.after_cancel(self.live_after)
            except:
                pass

            self.live_after = None

        for widget in self.winfo_children():
            widget.destroy()

    def make_button(
        self,
        parent,
        text,
        command,
        bg=TEAL,
        fg=WHITE
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=TEAL_DARK,
            activeforeground=WHITE,
            bd=0,
            relief="flat",
            cursor="hand2",
            font=(FONT, 10, "bold"),
            padx=16,
            pady=6
        )

    def card(self, parent, bg=WHITE):

        return tk.Frame(
            parent,
            bg=bg,
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0
        )

    def label(
        self,
        parent,
        text,
        size=10,
        color=TEXT,
        bold=False,
        bg=WHITE
    ):

        return tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=color,
            font=(
                FONT,
                size,
                "bold" if bold else "normal"
            )
        )

    def title_label(self, parent, text):

        return self.label(
            parent,
            text,
            24,
            TEXT,
            True,
            BG
        )

    def topbar(
        self,
        title,
        subtitle="",
        back=True
    ):

        bar = tk.Frame(
            self,
            bg=WHITE,
            height=72,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        bar.pack(fill="x")

        if back:

            self.make_button(
                bar,
                "← Back",
                self.go_back,
                WHITE,
                TEXT
            ).pack(
                side="left",
                padx=18,
                pady=9
            )

        box = tk.Frame(bar, bg=WHITE)
        box.pack(side="left", pady=7)

        self.label(
            box,
            title,
            17,
            TEXT,
            True
        ).pack(anchor="w")

        if subtitle:

            self.label(
                box,
                subtitle,
                9,
                MUTED
            ).pack(anchor="w")

        if self.current_user:

            userbox = tk.Frame(
                bar,
                bg=WHITE
            )

            userbox.pack(
                side="right",
                padx=18
            )

            self.label(
                userbox,
                self.current_user,
                9,
                TEXT,
                True
            ).pack(anchor="e")

            self.label(
                userbox,
                self.current_role.upper(),
                8,
                TEAL,
                True
            ).pack(anchor="e")

    def content(self):

        outer = tk.Frame(
            self,
            bg=BG
        )

        outer.pack(
            fill="both",
            expand=True
        )

        canvas = tk.Canvas(
            outer,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            outer,
            orient="vertical",
            command=canvas.yview
        )

        frame = tk.Frame(
            canvas,
            bg=BG
        )

        frame.bind(
            "<Configure>",
            lambda e:
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        window_id = canvas.create_window(
            (0, 0),
            window=frame,
            anchor="nw"
        )

        def resize_frame(event):
            canvas.itemconfigure(window_id, width=event.width)

        canvas.bind("<Configure>", resize_frame)

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        def wheel(event):

            canvas.yview_scroll(
                int(-event.delta / 120),
                "units"
            )

        canvas.bind(
            "<MouseWheel>",
            wheel
        )

        frame.bind(
            "<MouseWheel>",
            wheel
        )

        return frame

    # ==================================================
    # NAVIGATION
    # ==================================================

    def open_page(self, page):

        self.history.append(page)
        page()

    def go_back(self):

        if len(self.history) > 1:

            self.history.pop()
            self.history[-1]()

        else:

            self.home_by_role()

    def home_by_role(self):

        if self.current_role == "customer":
            self.customer_home()

        elif self.current_role == "restaurant":
            self.restaurant_home()

        elif self.current_role == "delivery":
            self.rider_home()

        elif self.current_role == "admin":
            self.admin_home()

        else:
            self.show_login()

    # ==================================================
    # LOGIN
    # ==================================================

    def show_login(self):

        self.clear()
        self.history = []

        main = tk.Frame(
            self,
            bg=BG
        )

        main.pack(
            fill="both",
            expand=True
        )

        left = tk.Frame(
            main,
            bg=NAVY,
            width=470
        )

        left.pack(
            side="left",
            fill="y"
        )

        left.pack_propagate(False)

        self.label(
            left,
            "FoodGenie.AI",
            31,
            WHITE,
            True,
            NAVY
        ).pack(
            anchor="w",
            padx=45,
            pady=(78, 3)
        )

        self.label(
            left,
            "Professional Food Delivery Platform",
            12,
            "#C8D6E5",
            False,
            NAVY
        ).pack(
            anchor="w",
            padx=47
        )

        self.label(
            left,
            "Smart ordering • AI recommendations\n"
            "Live delivery • Restaurant management",
            11,
            "#AFC2D6",
            False,
            NAVY
        ).pack(
            anchor="w",
            padx=47,
            pady=22
        )

        self.label(
            left,
            "Demo Login",
            10,
            "#7FDCD3",
            True,
            NAVY
        ).pack(
            anchor="w",
            padx=47
        )

        self.label(
            left,
            "Customer: demo / 1234\n"
            "Restaurant: pizza_hub / 1234\n"
            "Rider: delivery / 1234\n"
            "Admin: admin / admin123",
            9,
            "#D7E4EF",
            False,
            NAVY
        ).pack(
            anchor="w",
            padx=47,
            pady=5
        )

        right = tk.Frame(
            main,
            bg=BG
        )

        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        box = self.card(right)

        box.place(
            relx=.5,
            rely=.5,
            anchor="center",
            width=420,
            height=430
        )

        self.label(
            box,
            "Welcome back",
            22,
            TEXT,
            True
        ).pack(
            anchor="w",
            padx=35,
            pady=(25, 3)
        )

        self.label(
            box,
            "Sign in to continue",
            10,
            MUTED
        ).pack(
            anchor="w",
            padx=35,
            pady=(0, 16)
        )

        self.label(
            box,
            "Username",
            9,
            MUTED,
            True
        ).pack(
            anchor="w",
            padx=35
        )

        self.user_entry = tk.Entry(
            box,
            font=(FONT, 11),
            bd=0,
            bg="#F8FAFC",
            fg=TEXT
        )

        self.user_entry.pack(
            fill="x",
            padx=35,
            ipady=10,
            pady=(3, 10)
        )

        self.label(
            box,
            "Password",
            9,
            MUTED,
            True
        ).pack(
            anchor="w",
            padx=35
        )

        self.pass_entry = tk.Entry(
            box,
            show="•",
            font=(FONT, 11),
            bd=0,
            bg="#F8FAFC",
            fg=TEXT
        )

        self.pass_entry.pack(
            fill="x",
            padx=35,
            ipady=10,
            pady=(3, 14)
        )

        self.make_button(
            box,
            "SIGN IN",
            self.login,
            TEAL
        ).pack(
            fill="x",
            padx=35
        )

        self.label(
            box,
            "FoodGenie.AI • Smart food, smarter decisions",
            8,
            MUTED
        ).pack(pady=14)

    def login(self):

        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        row = self.db.execute(
            """
            SELECT *
            FROM users
            WHERE username=? AND password=?
            """,
            (username, password)
        ).fetchone()

        if not row:

            messagebox.showerror(
                "Login",
                "Invalid username or password"
            )

            return

        self.current_user = row["username"]
        self.current_role = row["role"]

        self.cart = []
        self.history = []

        self.home_by_role()

    def logout(self):

        self.current_user = None
        self.current_role = None
        self.cart = []
        self.history = []

        self.show_login()

    # ==================================================
    # CUSTOMER HOME
    # ==================================================

    def customer_home(self):

        self.clear()

        self.topbar(
            "Customer Dashboard",
            "Smart food ordering and AI assistance",
            False
        )

        f = self.content()

        self.label(
            f,
            "Good to see you 👋",
            25,
            TEXT,
            True,
            BG
        ).pack(
            anchor="w",
            padx=30,
            pady=(16, 1)
        )

        self.label(
            f,
            "What are you craving today?",
            11,
            MUTED,
            False,
            BG
        ).pack(
            anchor="w",
            padx=30
        )

        hero = tk.Frame(
            f,
            bg=NAVY
        )

        hero.pack(
            fill="x",
            padx=30,
            pady=14
        )

        self.label(
            hero,
            "FOODGENIE.AI",
            11,
            TEAL,
            True,
            NAVY
        ).pack(
            anchor="w",
            padx=25,
            pady=(14, 1)
        )

        self.label(
            hero,
            "Your personal food intelligence dashboard",
            21,
            WHITE,
            True,
            NAVY
        ).pack(
            anchor="w",
            padx=25
        )

        self.label(
            hero,
            "Discover food • optimize budget • plan meals • track delivery",
            10,
            "#C8D6E5",
            False,
            NAVY
        ).pack(
            anchor="w",
            padx=25,
            pady=(3, 14)
        )

        grid = tk.Frame(
            f,
            bg=BG
        )

        grid.pack(
            fill="x",
            padx=24
        )

        buttons = [
            ("🍽", "Browse Restaurants", self.restaurants_page, TEAL),
            ("🧠", "AI Command Center", self.ai_command_center, PURPLE),
            ("🛒", "My Cart", self.cart_page, ORANGE),
            ("📦", "My Orders", self.orders_page, CYAN),
            ("📍", "Live Delivery", self.live_orders_page, GREEN),
            ("💰", "Budget Meals", self.budget_page, TEAL_DARK),
            ("📅", "Meal Planner", self.meal_planner, PURPLE),
            ("🎧", "Help & Support", self.help_page, NAVY2)
        ]

        for i, (icon, title, cmd, color) in enumerate(buttons):

            c = self.card(grid)

            c.grid(
                row=i // 4,
                column=i % 4,
                sticky="ew",
                padx=6,
                pady=4
            )

            grid.columnconfigure(
                i % 4,
                weight=1
            )

            self.label(
                c,
                icon,
                24,
                color,
                True
            ).pack(
                anchor="w",
                padx=17,
                pady=(10, 3)
            )

            self.label(
                c,
                title,
                10,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=17
            )

            self.label(
                c,
                "Open →",
                8,
                MUTED
            ).pack(
                anchor="w",
                padx=17,
                pady=(2, 10)
            )

            c.bind(
                "<Button-1>",
                lambda e, fun=cmd: fun()
            )

        recent = self.card(f)

        recent.pack(
            fill="x",
            padx=30,
            pady=12
        )

        self.label(
            recent,
            "Quick AI Suggestion",
            13,
            TEXT,
            True
        ).pack(
            anchor="w",
            padx=20,
            pady=(11, 3)
        )

        self.label(
            recent,
            self.smart_daily_suggestion(),
            10,
            MUTED
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 11)
        )

        self.make_button(
            f,
            "LOGOUT",
            self.logout,
            NAVY2
        ).pack(
            anchor="e",
            padx=30,
            pady=(0, 16)
        )

    # ==================================================
    # RESTAURANTS
    # ==================================================

    def restaurants_page(self):

        self.clear()

        self.topbar(
            "Restaurants",
            "Choose a restaurant and explore its menu"
        )

        f = self.content()

        self.title_label(
            f,
            "Find your next meal"
        ).pack(
            anchor="w",
            padx=28,
            pady=(14, 3)
        )

        self.label(
            f,
            "Curated restaurants across Coimbatore",
            10,
            MUTED,
            False,
            BG
        ).pack(
            anchor="w",
            padx=28
        )

        grid = tk.Frame(
            f,
            bg=BG
        )

        grid.pack(
            fill="x",
            padx=22,
            pady=11
        )

        rows = self.db.execute(
            "SELECT * FROM restaurants ORDER BY rating DESC"
        ).fetchall()

        for i, r in enumerate(rows):

            c = self.card(grid)

            c.grid(
                row=i // 2,
                column=i % 2,
                sticky="ew",
                padx=6,
                pady=4
            )

            grid.columnconfigure(
                i % 2,
                weight=1
            )

            self.label(
                c,
                "🍴",
                27,
                TEAL,
                True
            ).pack(
                anchor="w",
                padx=18,
                pady=(10, 1)
            )

            self.label(
                c,
                r["name"],
                14,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=18
            )

            self.label(
                c,
                f'{r["cuisine"]} • {r["location"]}',
                9,
                MUTED
            ).pack(
                anchor="w",
                padx=18,
                pady=1
            )

            self.label(
                c,
                f'★ {r["rating"]}',
                9,
                ORANGE,
                True
            ).pack(
                anchor="w",
                padx=18
            )

            self.make_button(
                c,
                "VIEW MENU",
                lambda rid=r["id"]:
                self.open_menu(rid),
                NAVY2
            ).pack(
                anchor="w",
                padx=18,
                pady=9
            )

    def open_menu(self, rid):

        self.clear()

        restaurant = self.db.execute(
            "SELECT * FROM restaurants WHERE id=?",
            (rid,)
        ).fetchone()

        self.current_restaurant = rid

        self.topbar(
            restaurant["name"],
            f'{restaurant["cuisine"]} • '
            f'{restaurant["location"]} • '
            f'★ {restaurant["rating"]}'
        )

        f = self.content()

        self.title_label(
            f,
            "Menu"
        ).pack(
            anchor="w",
            padx=28,
            pady=(13, 8)
        )

        foods = self.db.execute(
            "SELECT * FROM foods WHERE restaurant_id=?",
            (rid,)
        ).fetchall()

        for food in foods:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=3
            )

            left = tk.Frame(
                c,
                bg=WHITE
            )

            left.pack(
                side="left",
                fill="x",
                expand=True,
                padx=18,
                pady=8
            )

            self.label(
                left,
                food["name"],
                11,
                TEXT,
                True
            ).pack(anchor="w")

            self.label(
                left,
                food["description"],
                8,
                MUTED
            ).pack(
                anchor="w",
                pady=1
            )

            self.label(
                left,
                food["category"],
                8,
                TEAL,
                True
            ).pack(anchor="w")

            self.label(
                c,
                f'₹{food["price"]:.0f}',
                12,
                TEXT,
                True
            ).pack(
                side="left",
                padx=15
            )

            self.make_button(
                c,
                "ADD",
                lambda x=food:
                self.add_to_cart(x),
                TEAL
            ).pack(
                side="right",
                padx=15
            )

    def add_to_cart(self, food):

        if self.cart and self.cart[0]["restaurant_id"] != food["restaurant_id"]:

            messagebox.showwarning(
                "Cart",
                "Please order from one restaurant at a time."
            )

            return

        self.cart.append(dict(food))

        messagebox.showinfo(
            "Cart",
            f'{food["name"]} added to cart.'
        )

    # ==================================================
    # CART
    # ==================================================

    def cart_total(self):

        return sum(
            float(x["price"])
            for x in self.cart
        )

    def cart_page(self):

        self.clear()

        self.topbar(
            "My Cart",
            "Review items before checkout"
        )

        f = self.content()

        self.title_label(
            f,
            "Cart"
        ).pack(
            anchor="w",
            padx=28,
            pady=(13, 8)
        )

        if not self.cart:

            self.label(
                f,
                "Your cart is empty.",
                13,
                MUTED,
                True,
                BG
            ).pack(pady=31)

            self.make_button(
                f,
                "BROWSE RESTAURANTS",
                self.restaurants_page
            ).pack()

            return

        for i, item in enumerate(self.cart):

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=2
            )

            self.label(
                c,
                f'{i+1}. {item["name"]}',
                11,
                TEXT,
                True
            ).pack(
                side="left",
                padx=18,
                pady=9
            )

            self.label(
                c,
                f'₹{item["price"]:.0f}',
                11,
                TEAL,
                True
            ).pack(
                side="right",
                padx=18
            )

        total = self.cart_total()

        self.label(
            f,
            f"Total: ₹{total:.0f}",
            16,
            TEXT,
            True,
            BG
        ).pack(
            anchor="e",
            padx=30,
            pady=9
        )

        self.make_button(
            f,
            "🧠 ANALYZE CART WITH AI",
            self.ai_cart,
            PURPLE
        ).pack(
            anchor="e",
            padx=30,
            pady=3
        )

        self.make_button(
            f,
            "CHECKOUT →",
            self.checkout_page,
            TEAL
        ).pack(
            anchor="e",
            padx=30,
            pady=5
        )

    # ==================================================
    # CHECKOUT
    # ==================================================

    def checkout_page(self):

        self.clear()

        self.topbar(
            "Checkout",
            "Delivery details and payment"
        )

        f = self.content()

        self.title_label(
            f,
            "Complete your order"
        ).pack(
            anchor="w",
            padx=28,
            pady=(14, 12)
        )

        box = self.card(f)

        box.pack(
            fill="x",
            padx=28
        )

        self.label(
            box,
            "Delivery Address",
            11,
            TEXT,
            True
        ).pack(
            anchor="w",
            padx=20,
            pady=(13, 3)
        )

        address = tk.Text(
            box,
            height=4,
            font=(FONT, 10),
            bg="#F8FAFC",
            fg=TEXT,
            bd=0
        )

        address.pack(
            fill="x",
            padx=20,
            pady=(0, 12)
        )

        self.label(
            box,
            "Payment Method",
            11,
            TEXT,
            True
        ).pack(
            anchor="w",
            padx=20
        )

        payment = tk.StringVar(
            value="Cash on Delivery"
        )

        for p in [
            "Cash on Delivery",
            "UPI",
            "Card"
        ]:

            tk.Radiobutton(
                box,
                text=p,
                variable=payment,
                value=p,
                bg=WHITE,
                fg=TEXT,
                selectcolor=WHITE,
                font=(FONT, 10)
            ).pack(
                anchor="w",
                padx=20,
                pady=1
            )

        self.label(
            box,
            f"Order Total: ₹{self.cart_total():.0f}",
            15,
            TEAL,
            True
        ).pack(
            anchor="w",
            padx=20,
            pady=11
        )

        self.make_button(
            f,
            "PLACE ORDER",
            lambda:
            self.place_order(
                address.get("1.0", "end").strip(),
                payment.get()
            ),
            TEAL
        ).pack(
            anchor="e",
            padx=28,
            pady=11
        )

    def place_order(self, address, payment):

        if not address:

            messagebox.showwarning(
                "Checkout",
                "Please enter delivery address."
            )

            return

        if not self.cart:
            return

        rid = self.cart[0]["restaurant_id"]

        total = self.cart_total()

        items = "|".join(
            x["name"]
            for x in self.cart
        )

        self.db.execute(
            """
            INSERT INTO orders
            (
                customer,
                restaurant_id,
                items,
                total,
                address,
                payment,
                status,
                rider_id,
                created_at
            )
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                self.current_user,
                rid,
                items,
                total,
                address,
                payment,
                "Placed",
                None,
                datetime.now().isoformat()
            )
        )

        self.db.commit()

        self.cart = []

        messagebox.showinfo(
            "Order Confirmed",
            "Your order has been placed successfully."
        )

        self.orders_page()

    # ==================================================
    # ORDERS
    # ==================================================

    def orders_page(self):

        self.clear()

        self.topbar(
            "My Orders",
            "Order history and status"
        )

        f = self.content()

        orders = self.db.execute(
            """
            SELECT o.*,r.name restaurant
            FROM orders o
            JOIN restaurants r
            ON o.restaurant_id=r.id
            WHERE customer=?
            ORDER BY o.id DESC
            """,
            (self.current_user,)
        ).fetchall()

        if not orders:

            self.label(
                f,
                "No orders yet.",
                13,
                MUTED,
                True,
                BG
            ).pack(pady=37)

            return

        for o in orders:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=4
            )

            self.label(
                c,
                f'Order #{o["id"]} • {o["restaurant"]}',
                12,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=20,
                pady=(10, 1)
            )

            self.label(
                c,
                o["items"].replace("|", " • "),
                9,
                MUTED
            ).pack(
                anchor="w",
                padx=20
            )

            self.label(
                c,
                f'₹{o["total"]:.0f} • '
                f'{o["payment"]} • '
                f'{o["status"]}',
                10,
                TEAL,
                True
            ).pack(
                anchor="w",
                padx=20,
                pady=2
            )

            row = tk.Frame(
                c,
                bg=WHITE
            )

            row.pack(
                anchor="e",
                padx=15,
                pady=6
            )

            self.make_button(
                row,
                "DETAILS",
                lambda oid=o["id"]:
                self.order_details(oid),
                NAVY2
            ).pack(
                side="left",
                padx=3
            )

            if o["status"] in (
                "Ready",
                "Out for Delivery"
            ):

                self.make_button(
                    row,
                    "LIVE TRACK",
                    lambda oid=o["id"]:
                    self.live_tracking(oid),
                    GREEN
                ).pack(
                    side="left",
                    padx=3
                )

    def live_orders_page(self):

        self.clear()

        self.topbar(
            "Live Delivery",
            "Orders currently moving"
        )

        f = self.content()

        orders = self.db.execute(
            """
            SELECT o.*,r.name restaurant
            FROM orders o
            JOIN restaurants r
            ON o.restaurant_id=r.id
            WHERE customer=?
            AND o.status IN
            ('Ready','Out for Delivery')
            ORDER BY o.id DESC
            """,
            (self.current_user,)
        ).fetchall()

        if not orders:

            self.label(
                f,
                "No active delivery right now.",
                13,
                MUTED,
                True,
                BG
            ).pack(pady=37)

            return

        for o in orders:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=4
            )

            self.label(
                c,
                f'Order #{o["id"]} • {o["restaurant"]}',
                12,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=20,
                pady=(10, 2)
            )

            self.label(
                c,
                f'Status: {o["status"]}',
                10,
                TEAL,
                True
            ).pack(
                anchor="w",
                padx=20
            )

            self.make_button(
                c,
                "OPEN LIVE MAP",
                lambda oid=o["id"]:
                self.live_tracking(oid),
                GREEN
            ).pack(
                anchor="e",
                padx=18,
                pady=7
            )

    # ==================================================
    # ORDER DETAILS
    # ==================================================

    def order_details(self, oid):

        self.clear()

        self.topbar(
            f"Order #{oid}",
            "Order details"
        )

        f = self.content()

        o = self.db.execute(
            """
            SELECT o.*,r.name restaurant
            FROM orders o
            JOIN restaurants r
            ON o.restaurant_id=r.id
            WHERE o.id=?
            """,
            (oid,)
        ).fetchone()

        self.title_label(
            f,
            "Order Summary"
        ).pack(
            anchor="w",
            padx=28,
            pady=12
        )

        c = self.card(f)

        c.pack(
            fill="x",
            padx=28
        )

        details = [
            ("Restaurant", o["restaurant"]),
            ("Items", o["items"].replace("|", " • ")),
            ("Total", f'₹{o["total"]:.0f}'),
            ("Address", o["address"]),
            ("Payment", o["payment"]),
            ("Status", o["status"])
        ]

        for key, value in details:

            row = tk.Frame(
                c,
                bg=WHITE
            )

            row.pack(
                fill="x",
                padx=18,
                pady=4
            )

            self.label(
                row,
                key,
                9,
                MUTED,
                True
            ).pack(
                side="left"
            )

            self.label(
                row,
                str(value),
                10,
                TEXT,
                True
            ).pack(
                side="right"
            )

        if o["rider_id"]:

            rider = self.db.execute(
                "SELECT * FROM riders WHERE id=?",
                (o["rider_id"],)
            ).fetchone()

            if rider:

                self.label(
                    f,
                    "Delivery Partner",
                    14,
                    TEXT,
                    True,
                    BG
                ).pack(
                    anchor="w",
                    padx=28,
                    pady=(16, 5)
                )

                rc = self.card(f)

                rc.pack(
                    fill="x",
                    padx=28
                )

                self.label(
                    rc,
                    f'🏍 {rider["name"]}',
                    12,
                    TEXT,
                    True
                ).pack(
                    anchor="w",
                    padx=20,
                    pady=(10, 3)
                )

                self.label(
                    rc,
                    f'Phone: {rider["phone"]} • '
                    f'{rider["vehicle"]} • '
                    f'★ {rider["rating"]}',
                    9,
                    MUTED
                ).pack(
                    anchor="w",
                    padx=20,
                    pady=(0, 10)
                )

        if o["status"] in (
            "Ready",
            "Out for Delivery"
        ):

            self.make_button(
                f,
                "VIEW LIVE MAP",
                lambda:
                self.live_tracking(oid),
                GREEN
            ).pack(
                anchor="e",
                padx=28,
                pady=11
            )

    # ==================================================
    # LIVE MAP
    # ==================================================

    def live_tracking(self, oid):

        self.clear()

        self.topbar(
            "Live Delivery Tracking",
            "Simulated in-app live route"
        )

        f = self.content()

        o = self.db.execute(
            "SELECT * FROM orders WHERE id=?",
            (oid,)
        ).fetchone()

        self.label(
            f,
            f"Order #{oid} • {o['status']}",
            14,
            TEXT,
            True,
            BG
        ).pack(
            anchor="w",
            padx=28,
            pady=(13, 6)
        )

        mapbox = self.card(f)

        mapbox.pack(
            fill="x",
            padx=28
        )

        canvas = tk.Canvas(
            mapbox,
            width=900,
            height=430,
            bg="#E8F0F4",
            highlightthickness=0
        )

        canvas.pack(
            padx=15,
            pady=9
        )

        for y in [80, 170, 260, 350]:

            canvas.create_line(
                0,
                y,
                900,
                y,
                fill="#C5D3DA",
                width=26
            )

            canvas.create_line(
                0,
                y,
                900,
                y,
                fill="#F8FBFC",
                width=2,
                dash=(10, 8)
            )

        for x in [120, 310, 520, 730]:

            canvas.create_line(
                x,
                0,
                x,
                430,
                fill="#C5D3DA",
                width=22
            )

            canvas.create_line(
                x,
                0,
                x,
                430,
                fill="#F8FBFC",
                width=2,
                dash=(10, 8)
            )

        canvas.create_rectangle(
            35,
            20,
            105,
            65,
            fill="#CBE8D8",
            outline=""
        )

        canvas.create_text(
            70,
            42,
            text="PARK",
            fill="#4A7D63",
            font=(FONT, 8, "bold")
        )

        start = (110, 350)
        end = (760, 80)

        canvas.create_line(
            start[0],
            start[1],
            end[0],
            end[1],
            fill=TEAL,
            width=5,
            dash=(12, 7)
        )

        canvas.create_oval(
            end[0] - 12,
            end[1] - 12,
            end[0] + 12,
            end[1] + 12,
            fill=GREEN,
            outline=WHITE,
            width=3
        )

        canvas.create_text(
            end[0],
            end[1] - 25,
            text="YOU",
            fill=TEXT,
            font=(FONT, 9, "bold")
        )

        bike = canvas.create_text(
            start[0],
            start[1],
            text="🏍",
            font=("Segoe UI Emoji", 24)
        )

        canvas.create_text(
            start[0],
            start[1] + 25,
            text="RIDER",
            fill=TEXT,
            font=(FONT, 8, "bold")
        )

        self.route_step = 0

        def move():

            if not canvas.winfo_exists():
                return

            self.route_step += 1

            t = min(
                self.route_step / 100,
                1
            )

            x = (
                start[0]
                + (end[0] - start[0]) * t
            )

            y = (
                start[1]
                + (end[1] - start[1]) * t
                - 45 * math.sin(math.pi * t)
            )

            canvas.coords(
                bike,
                x,
                y
            )

            if self.route_step < 100:

                self.live_after = self.after(
                    700,
                    move
                )

            else:

                self.live_after = None

        move()

        info = self.card(f)

        info.pack(
            fill="x",
            padx=28,
            pady=7
        )

        self.label(
            info,
            "● LIVE",
            10,
            GREEN,
            True
        ).pack(
            side="left",
            padx=20,
            pady=9
        )

        self.label(
            info,
            "Bike is moving along the simulated route",
            9,
            MUTED
        ).pack(
            side="left"
        )

    # ==================================================
    # AI COMMAND CENTER
    # ==================================================

    def ai_command_center(self):

        self.clear()
        self.topbar("AI Command Center", "FoodGenie intelligent food tools")
        f=self.content()
        self.title_label(f,"FoodGenie AI").pack(anchor="w",padx=28,pady=(22,3))
        self.label(f,"AI tools + experimental food intelligence",10,MUTED,False,BG).pack(anchor="w",padx=28)
        tools=[
            ("🤖","AI Food Chat","Ask anything about food",self.ai_assistant),("🎯","Smart Recommendation","Personalized food picks",self.ai_recommendation),("💰","Budget Optimizer","Build meals within budget",self.ai_budget),("🛒","Smart Cart AI","Analyze your cart",self.ai_cart),
            ("❤️","Mood Food AI","Food based on mood",self.ai_mood),("💪","Nutrition AI","Protein and lighter choices",self.ai_health),("🌶","Spice AI","Mild to extra spicy",self.ai_spice),("🔥","Trending AI","Based on order patterns",self.ai_trending),
            ("🍽","Combo Generator","Create smart combinations",self.ai_combo),("🔁","Reorder AI","Past-order suggestions",self.ai_reorder),("⭐","Restaurant Match","Match restaurants",self.ai_restaurant_match),("📅","AI Meal Planner","Generate weekly meals",self.meal_planner),
            ("🧑‍🤝‍🧑","Party Planner","Plan food for groups",self.ai_party_planner),("🔎","Smart Search","Natural-language food search",self.ai_smart_search),("🧾","Order Insight","Analyze order history",self.ai_order_insight),("🌟","Daily AI Pick","One-click food suggestion",self.ai_daily_pick),
            ("🧬","Taste DNA","Discover your food fingerprint",self.ai_taste_dna),("🧾","Smart Bill Split","Fairly split group orders",self.ai_smart_split),("♻️","Leftover Rescue","Reduce unnecessary ordering",self.ai_leftover_rescue),("💎","Value Score","Compare price + rating",self.ai_value_score),
            ("⏱️","ETA Predictor","Transparent delivery estimate",self.ai_eta_predictor),("🌱","Eco Choice","Plant-forward menu helper",self.ai_eco_choice),("🎉","Occasion Planner","Plan food for events",self.ai_occasion_planner),("🎁","Surprise Meal","Random menu discovery",self.ai_surprise_meal)]
        grid=tk.Frame(f,bg=BG); grid.pack(fill="x",padx=22,pady=18)
        for i,(icon,title,desc,command) in enumerate(tools):
            c=self.card(grid); c.grid(row=i//4,column=i%4,sticky="ew",padx=5,pady=5); grid.columnconfigure(i%4,weight=1)
            self.label(c,icon,21,TEAL,True).pack(anchor="w",padx=14,pady=(12,2)); self.label(c,title,9,TEXT,True).pack(anchor="w",padx=14); self.label(c,desc,8,MUTED).pack(anchor="w",padx=14,pady=2); self.make_button(c,"OPEN →",command,NAVY2).pack(anchor="w",padx=14,pady=9)

    # ==================================================
    # AI COMMON PAGE - FIXED
    # ==================================================

    def ai_input_page(self, title, subtitle, prompt, callback):
        self.clear()
        self.topbar(title, subtitle)
        f = self.content()

        self.title_label(f, title).pack(anchor="w", padx=28, pady=(14, 3))
        self.label(f, prompt, 10, MUTED, False, BG).pack(anchor="w", padx=28, pady=(0, 10))

        entry = tk.Entry(
            f, font=(FONT, 12), bg=WHITE, fg=TEXT,
            insertbackground=TEXT, bd=0, relief="flat"
        )
        entry.pack(fill="x", padx=28, ipady=12)

        result = tk.Frame(f, bg=BG)
        result.pack(fill="both", expand=True, padx=28, pady=(3, 0))

        def execute():
            query = entry.get().strip()
            try:
                callback(query, result)
            except Exception as exc:
                self.show_ai_results(result, "AI Error", [f"Error: {exc}"])

        self.make_button(f, "RUN AI", execute, TEAL).pack(anchor="e", padx=28, pady=7)
        entry.bind("<Return>", lambda e: execute())
        entry.focus_set()
        return entry, result

    def show_ai_results(self, result, title, items):
        for widget in result.winfo_children():
            widget.destroy()

        self.label(result, "🧠 " + title, 14, TEXT, True, BG).pack(anchor="w", pady=(3, 6))

        if not items:
            items = ["No AI suggestions found."]

        for item in items:
            c = self.card(result)
            c.pack(fill="x", pady=2)
            self.label(c, str(item), 10, TEXT).pack(anchor="w", padx=18, pady=8)

    def _ai_foods(self):
        return self.db.execute("""
            SELECT f.*, r.name AS restaurant, r.cuisine AS cuisine, r.rating AS restaurant_rating
            FROM foods f
            JOIN restaurants r ON r.id = f.restaurant_id
        """).fetchall()

    def _ai_find_food(self, name):
        rows = self.db.execute(
            """SELECT f.*, r.name AS restaurant, r.cuisine AS cuisine
               FROM foods f JOIN restaurants r ON r.id=f.restaurant_id
               WHERE lower(f.name)=lower(?) LIMIT 1""", (name,)
        ).fetchall()
        return rows[0] if rows else None

    # ==================================================
    # AI FOOD CHAT
    # ==================================================

    def ai_assistant(self):
        def run(q, result):
            q = q.lower().strip()
            if not q:
                answer = "Try: spicy food, cheap dinner, dessert, pizza, healthy, protein or burger."
            elif "spicy" in q:
                answer = "🌶 Spicy picks: Chicken 65, Arrabbiata Pasta and Peri Peri Fries."
            elif "pizza" in q:
                answer = "🍕 Pizza picks: Margherita Pizza, Farmhouse Pizza and Paneer Tikka Pizza."
            elif "burger" in q:
                answer = "🍔 Burger picks: Classic Veg Burger, Cheese Burger and Chicken Burger."
            elif "dessert" in q or "sweet" in q:
                answer = "🍰 Sweet picks: Chocolate Brownie, Choco Lava Cake, Cheesecake and Gulab Jamun."
            elif "protein" in q:
                answer = "💪 Protein-oriented picks: Chicken Biryani, Chicken Burger, Chicken Pasta and Chicken 65."
            elif "cheap" in q or "budget" in q:
                answer = "💰 Budget tip: use Budget Optimizer and enter your maximum amount."
            elif "healthy" in q or "light" in q:
                answer = "🥗 Lighter-category picks: Idli Vada, Masala Dosa and South Indian Meals."
            else:
                answer = "🤖 I can help with recommendations, budget, mood, spice, nutrition, combos, restaurants and meal planning."
            self.show_ai_results(result, "AI Food Response", [answer])

        self.ai_input_page("AI Food Chat", "Ask FoodGenie anything about food", "Example: spicy pizza", run)

    # ==================================================
    # SMART RECOMMENDATION
    # ==================================================

    def ai_recommendation(self):
        def run(q, result):
            q = q.lower().strip()
            foods = self._ai_foods()
            scored = []

            numbers = [int(x) for x in q.replace("₹", " ").split() if x.isdigit()]
            budget = numbers[0] if ("under" in q and numbers) else None

            groups = {
                "pizza": ["pizza"], "burger": ["burger"], "pasta": ["pasta"],
                "biryani": ["biryani"], "dessert": ["dessert", "brownie", "cake", "sweet"],
                "spicy": ["spicy", "podi", "peri", "65", "arrabbiata"],
                "chicken": ["chicken"], "south": ["south", "dosa", "idli"],
                "veg": ["veg", "paneer", "vegetable"],
            }

            for food in foods:
                text = f"{food['name']} {food['category']} {food['description']} {food['cuisine']}".lower()
                score = 0
                for key, words in groups.items():
                    if key in q and any(w in text for w in words):
                        score += 15
                if budget is not None:
                    score += 20 if food["price"] <= budget else -15
                if "cheap" in q or "budget" in q:
                    if food["price"] <= 200:
                        score += 10
                if score == 0 and not q:
                    score = 1
                scored.append((score, food))

            scored.sort(key=lambda x: (-x[0], x[1]["price"]))
            items = [
                f"🎯 {food['name']} — ₹{food['price']:.0f} • {food['restaurant']} • AI Match {max(1, min(99, 50 + score))}%"
                for score, food in scored[:6]
            ]
            self.show_ai_results(result, "Smart Recommendations", items)

        self.ai_input_page("Smart Recommendation", "Tell AI what you feel like eating", "Example: spicy pizza under 400", run)

    # ==================================================
    # BUDGET OPTIMIZER
    # ==================================================

    def ai_budget(self):
        def run(q, result):
            try:
                numbers = [int(x) for x in q.replace("₹", " ").split() if x.isdigit()]
                budget = numbers[0] if numbers else 300
            except Exception:
                budget = 300

            foods = self._ai_foods()
            combos = []

            for a in foods:
                if a["price"] <= budget:
                    combos.append((budget - a["price"], [a]))
                for b in foods:
                    if b["id"] <= a["id"] or b["restaurant_id"] != a["restaurant_id"]:
                        continue
                    total = a["price"] + b["price"]
                    if total <= budget:
                        combos.append((budget - total, [a, b]))

            combos.sort(key=lambda x: x[0])
            items = []
            for remaining, combo in combos[:5]:
                total = sum(x["price"] for x in combo)
                names = " + ".join(x["name"] for x in combo)
                items.append(f"💰 ₹{total:.0f} — {names} • {combo[0]['restaurant']} • Left ₹{remaining:.0f}")

            if not items:
                items = [f"No meal found under ₹{budget}.", "Try a slightly higher budget."]
            self.show_ai_results(result, "Budget Optimizer", items)

        self.ai_input_page("Budget Optimizer", "Build meals within your budget", "Example: 350", run)

    # ==================================================
    # SMART CART AI
    # ==================================================

    def ai_cart(self):
        self.clear()
        self.topbar("Smart Cart AI", "Analyze your current cart")
        f = self.content()
        self.title_label(f, "🛒 Cart Intelligence").pack(anchor="w", padx=28, pady=14)

        if not self.cart:
            self.show_ai_results(f, "AI Cart Report", [
                "Your cart is empty.",
                "Add some food items and open Smart Cart AI again."
            ])
            return

        total = sum(float(x["price"]) * int(x.get("qty", 1)) for x in self.cart)
        count = sum(int(x.get("qty", 1)) for x in self.cart)
        tips = [
            f"🧾 Items: {count}",
            f"💰 Cart total: ₹{total:.0f}",
        ]
        if total >= 500:
            tips.append("💡 Tip: Compare the cart with Budget Optimizer before checkout.")
        elif total < 200:
            tips.append("💡 Tip: Your cart is relatively low-cost.")
        else:
            tips.append("💡 Tip: Your cart is in a moderate spending range.")
        if count >= 3:
            tips.append("🍽 Combo Tip: Check Combo Generator for a grouped meal.")
        self.show_ai_results(f, "AI Cart Report", tips)

    # ==================================================
    # MOOD AI
    # ==================================================

    def ai_mood(self):
        def run(q, result):
            q = q.lower()
            if "happy" in q or "celebrat" in q:
                names = ["Choco Lava Cake", "Farmhouse Pizza", "Cheese Burger"]
            elif "sad" in q or "comfort" in q:
                names = ["Chocolate Brownie", "Chicken Biryani", "Alfredo Pasta"]
            elif "tired" in q or "energy" in q:
                names = ["Chicken Biryani", "Chicken Burger", "Ghee Rice"]
            elif "romantic" in q:
                names = ["Pesto Pasta", "Margherita Pizza", "Strawberry Cheesecake"]
            else:
                names = ["Margherita Pizza", "Alfredo Pasta", "Chocolate Brownie"]
            self.show_ai_results(result, "Mood Food Suggestions", ["❤️ " + x for x in names])
        self.ai_input_page("Mood Food AI", "Tell AI your current mood", "Example: happy / sad / tired / romantic", run)

    # ==================================================
    # NUTRITION AI
    # ==================================================

    def ai_health(self):
        def run(q, result):
            q = q.lower()
            if "protein" in q:
                names = ["Chicken Biryani", "Chicken Burger", "Chicken Pasta", "Chicken 65"]
            elif "light" in q or "lighter" in q:
                names = ["Idli Vada", "Masala Dosa", "South Indian Meals"]
            elif "energy" in q:
                names = ["Ghee Rice", "Chicken Biryani", "Pasta"]
            else:
                names = ["Masala Dosa", "Idli Vada", "Chicken Biryani"]
            self.show_ai_results(result, "Nutrition AI", ["💪 " + x for x in names])
        self.ai_input_page("Nutrition AI", "General food-category suggestions", "Example: protein / light / energy", run)

    # ==================================================
    # SPICE AI
    # ==================================================

    def ai_spice(self):
        def run(q, result):
            q = q.lower()
            if "extra" in q:
                names = ["Chicken 65", "Peri Peri Fries", "Arrabbiata Pasta"]
            elif "spicy" in q or "medium" in q:
                names = ["Chicken 65", "Arrabbiata Pasta", "Podi Dosa"]
            else:
                names = ["Margherita Pizza", "Alfredo Pasta", "Idli Vada"]
            self.show_ai_results(result, "Spice AI", ["🌶 " + x for x in names])
        self.ai_input_page("Spice AI", "Find food by spice preference", "Example: mild / medium / spicy / extra spicy", run)

    # ==================================================
    # TRENDING AI - ACTUAL ORDER COUNTS
    # ==================================================

    def ai_trending(self):
        foods = self.db.execute("""
            SELECT f.name, f.price, r.name AS restaurant, COUNT(o.id) AS order_count
            FROM foods f
            JOIN restaurants r ON r.id=f.restaurant_id
            LEFT JOIN orders o ON instr('|' || o.items || '|', '|' || f.name || '|') > 0
            GROUP BY f.id
            ORDER BY order_count DESC, f.name ASC
            LIMIT 10
        """).fetchall()

        items = [
            f"🔥 #{i} {x['name']} — ₹{x['price']:.0f} • {x['restaurant']} • {x['order_count']} order(s)"
            for i, x in enumerate(foods, 1)
        ]
        if not items:
            items = ["No order data available yet."]

        self.clear()
        self.topbar("Trending AI", "Based on FoodGenie order activity")
        f = self.content()
        self.title_label(f, "🔥 Trending Food").pack(anchor="w", padx=28, pady=14)
        self.show_ai_results(f, "AI Trending Feed", items)

    # ==================================================
    # COMBO GENERATOR
    # ==================================================

    def ai_combo(self):
        foods = self._ai_foods()
        pairs = []

        for a in foods:
            for b in foods:
                if b["id"] <= a["id"]:
                    continue
                if a["restaurant_id"] != b["restaurant_id"]:
                    continue
                total = a["price"] + b["price"]
                pairs.append((total, a, b))

        pairs.sort(key=lambda x: x[0])
        selected = pairs[:8]

        items = [
            f"🍽 {a['name']} + {b['name']} — ₹{total:.0f} • {a['restaurant']}"
            for total, a, b in selected
        ]
        if not items:
            items = [
                "🍕 Movie Night — Pizza + Garlic Bread",
                "🍔 Burger Combo — Burger + Fries",
                "🍛 Indian Feast — Biryani + Starter"
            ]

        self.clear()
        self.topbar("Combo Generator", "Smart meal combinations")
        f = self.content()
        self.title_label(f, "AI Combo Ideas").pack(anchor="w", padx=28, pady=14)
        self.show_ai_results(f, "Generated Combos", items)

    # ==================================================
    # REORDER AI
    # ==================================================

    def ai_reorder(self):
        orders = self.db.execute("""
            SELECT items FROM orders
            WHERE customer=? ORDER BY id DESC LIMIT 30
        """, (self.current_user,)).fetchall()

        frequency = {}
        for order in orders:
            for name in str(order["items"]).split("|"):
                name = name.strip()
                if name:
                    frequency[name] = frequency.get(name, 0) + 1

        if frequency:
            ranked = sorted(frequency.items(), key=lambda x: (-x[1], x[0]))
            items = [f"🔁 {name} — ordered {count} time(s)" for name, count in ranked[:8]]
        else:
            items = [
                "No previous orders yet.",
                "Place an order and Reorder AI will learn your favourites."
            ]

        self.clear()
        self.topbar("Reorder AI", "Based on your order history")
        f = self.content()
        self.title_label(f, "You May Want Again").pack(anchor="w", padx=28, pady=14)
        self.show_ai_results(f, "AI Reorder Suggestions", items)

    # ==================================================
    # RESTAURANT MATCH
    # ==================================================

    def ai_restaurant_match(self):
        def run(q, result):
            q = q.lower().strip()
            restaurants = self.db.execute("SELECT * FROM restaurants").fetchall()
            matches = []

            for r in restaurants:
                cuisine = str(r["cuisine"]).lower()
                name = str(r["name"]).lower()
                score = 50
                if cuisine in q:
                    score += 25
                if any(x in q for x in ["pizza", "pasta", "italian"]) and cuisine == "italian":
                    score += 20
                if "burger" in q and "fast" in cuisine:
                    score += 20
                if "dessert" in q and "dessert" in cuisine:
                    score += 20
                if "south" in q and "south" in cuisine:
                    score += 20
                if any(x in q for x in ["spice", "indian", "biryani"]) and "indian" in cuisine:
                    score += 15
                if name in q:
                    score += 10
                matches.append((min(score, 99), r))

            matches.sort(key=lambda x: (-x[0], x[1]["name"]))
            items = [
                f"⭐ {r['name']} — {r['cuisine']} • Rating {r['rating']} • AI Match {score}%"
                for score, r in matches[:6]
            ]
            self.show_ai_results(result, "Restaurant Matches", items)

        self.ai_input_page("Restaurant Match", "Find restaurants by preference", "Example: pizza / Italian / dessert", run)

    # ==================================================
    # PARTY PLANNER
    # ==================================================

    def ai_party_planner(self):
        def run(q, result):
            import re
            numbers = re.findall(r"\d+", q)
            people = int(numbers[0]) if numbers else 4

            if people <= 2:
                plan = ["👥 2 people", "🍕 1 Main", "🍟 1 Side", "🍰 1 Dessert"]
            elif people <= 5:
                plan = [f"👥 {people} people", "🍕 2 Mains", "🍟 2 Sides", "🍰 1 Dessert"]
            else:
                plan = [f"👥 {people} people", "🍕 3 Mains", "🍟 3 Sides", "🍰 2 Desserts"]

            self.show_ai_results(result, "Party Plan", plan)

        self.ai_input_page("Party Planner", "Plan food for a group", "Example: 6 people", run)

    # ==================================================
    # SMART SEARCH
    # ==================================================

    def ai_smart_search(self):
        def run(q, result):
            q = q.lower().strip()
            foods = self._ai_foods()
            numbers = [int(x) for x in q.replace("₹", " ").split() if x.isdigit()]
            budget = numbers[0] if ("under" in q and numbers) else None

            words = [
                x for x in q.split()
                if len(x) > 2 and not x.isdigit() and x not in {"under", "for", "the", "and", "with"}
            ]

            matches = []
            for food in foods:
                text = f"{food['name']} {food['category']} {food['description']} {food['cuisine']}".lower()
                score = sum(3 for word in words if word in text)
                if budget is not None:
                    score += 5 if food["price"] <= budget else -5
                if score > 0:
                    matches.append((score, food))

            matches.sort(key=lambda x: (-x[0], x[1]["price"]))
            items = [
                f"🔎 {food['name']} — ₹{food['price']:.0f} • {food['restaurant']}"
                for score, food in matches[:8]
            ]
            if not items:
                items = ["No close match.", "Try: spicy pizza under 400"]
            self.show_ai_results(result, "Smart Search Results", items)

        self.ai_input_page("Smart Search", "Natural-language food search", "Example: spicy pizza under 400", run)

    # ==================================================
    # ORDER INSIGHT
    # ==================================================

    def ai_order_insight(self):
        orders = self.db.execute("""
            SELECT * FROM orders
            WHERE customer=? ORDER BY id DESC
        """, (self.current_user,)).fetchall()

        if not orders:
            items = [
                "No orders found yet.",
                "After your first order, AI Order Insight will show spending and activity."
            ]
        else:
            spend = sum(float(x["total"] or 0) for x in orders)
            average = spend / len(orders)
            completed = sum(1 for x in orders if str(x["status"]).lower() in {"delivered", "completed"})
            items = [
                f"📦 Orders analyzed: {len(orders)}",
                f"💰 Total spend: ₹{spend:.0f}",
                f"📊 Average order value: ₹{average:.0f}",
                f"✅ Delivered/completed: {completed}",
                "💡 Tip: Use Budget Optimizer to compare meals before checkout."
            ]

        self.clear()
        self.topbar("Order Insight", "Summary of your recent activity")
        f = self.content()
        self.title_label(f, "AI Order Report").pack(anchor="w", padx=28, pady=14)
        self.show_ai_results(f, "Insights", items)

    # ==================================================
    # DAILY AI PICK
    # ==================================================

    def ai_daily_pick(self):
        foods = self._ai_foods()
        if not foods:
            return

        # Deterministic daily pick so it stays stable during the day.
        index = datetime.now().timetuple().tm_yday % len(foods)
        food = foods[index]

        self.clear()
        self.topbar("Daily AI Pick", "A data-backed daily suggestion")
        f = self.content()
        self.title_label(f, "Today's Pick").pack(anchor="w", padx=28, pady=14)
        self.show_ai_results(f, "FoodGenie Suggests", [
            f"🌟 {food['name']} — ₹{food['price']:.0f}",
            f"{food['restaurant']} • {food['category']}",
            food['description']
        ])

    def smart_daily_suggestion(self):
        hour = datetime.now().hour
        if hour < 11:
            return "Breakfast idea: Masala Dosa or Idli Vada."
        if hour < 16:
            return "Lunch idea: Chicken Biryani or South Indian Meals."
        if hour < 20:
            return "Evening idea: Burger + Fries or Pizza + Garlic Bread."
        return "Dinner idea: Pasta or Pizza, followed by a dessert."

    # ==================================================
    # BUDGET PAGE
    # ==================================================

    def budget_page(self):

        self.clear()

        self.topbar(
            "Budget Meals",
            "Find meals within a spending limit"
        )

        f = self.content()

        self.title_label(
            f,
            "Budget Optimizer"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        entry = tk.Entry(
            f,
            font=(FONT, 12),
            bg=WHITE,
            fg=TEXT,
            bd=0
        )

        entry.pack(
            fill="x",
            padx=28,
            ipady=12
        )

        entry.insert(
            0,
            "300"
        )

        self.budget_result_frame = tk.Frame(
            f,
            bg=BG
        )

        self.budget_result_frame.pack(
            fill="x",
            padx=28
        )

        self.make_button(
            f,
            "FIND MEALS",
            lambda:
            self.budget_results(
                entry.get()
            ),
            TEAL
        ).pack(
            anchor="e",
            padx=28,
            pady=7
        )

    def budget_results(self, value):

        for widget in self.budget_result_frame.winfo_children():
            widget.destroy()

        try:
            budget = float(value)
        except:
            budget = 300

        foods = self.db.execute(
            "SELECT * FROM foods WHERE price<=?",
            (budget,)
        ).fetchall()

        foods = sorted(
            foods,
            key=lambda x: x["price"],
            reverse=True
        )[:10]

        for food in foods:

            c = self.card(
                self.budget_result_frame
            )

            c.pack(
                fill="x",
                pady=2
            )

            self.label(
                c,
                food["name"],
                10,
                TEXT,
                True
            ).pack(
                side="left",
                padx=18,
                pady=7
            )

            self.label(
                c,
                f'₹{food["price"]:.0f}',
                10,
                TEAL,
                True
            ).pack(
                side="right",
                padx=18
            )

    # ==================================================
    # MEAL PLANNER
    # ==================================================

    def meal_planner(self):

        self.clear()

        self.topbar(
            "AI Meal Planner",
            "A simple 7-day food plan"
        )

        f = self.content()

        self.title_label(
            f,
            "Weekly Meal Plan"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        meals = [
            "Masala Dosa + Idli Vada",
            "Chicken Biryani + Gulab Jamun",
            "Alfredo Pasta + Brownie",
            "Farmhouse Pizza + Garlic Bread",
            "South Indian Meals + Dessert",
            "Cheese Burger + Fries",
            "Paneer Butter Masala + Ghee Rice"
        ]

        for day, meal in zip(
            days,
            meals
        ):

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=2
            )

            self.label(
                c,
                day,
                10,
                TEAL,
                True
            ).pack(
                side="left",
                padx=18,
                pady=8
            )

            self.label(
                c,
                meal,
                10,
                TEXT,
                True
            ).pack(
                side="right",
                padx=18
            )

    # ==================================================
    # HELP
    # ==================================================

    def help_page(self):

        self.clear()

        self.topbar(
            "Help & Support",
            "FoodGenie customer support"
        )

        f = self.content()

        self.title_label(
            f,
            "How can we help?"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        questions = [

            (
                "How do I place an order?",
                "Browse Restaurants → Menu → Add → Checkout."
            ),

            (
                "Can I track my order?",
                "Open My Orders → Live Track."
            ),

            (
                "How does AI work?",
                "This demo uses local rule-based AI logic."
            ),

            (
                "Is live GPS real?",
                "The map is a simulated route for demonstration."
            )
        ]

        for question, answer in questions:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=3
            )

            self.label(
                c,
                question,
                10,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=18,
                pady=(8, 2)
            )

            self.label(
                c,
                answer,
                9,
                MUTED
            ).pack(
                anchor="w",
                padx=18,
                pady=(0, 8)
            )

    # ==================================================
    # EXTRA AI FEATURES - FOODGENIE DIFFERENTIATORS
    # ==================================================

    def _ai_order_rows(self):
        return self.db.execute("SELECT * FROM orders WHERE customer=? ORDER BY id DESC", (self.current_user,)).fetchall()

    def ai_taste_dna(self):
        rows = self._ai_order_rows()
        if not rows:
            self.ai_input_page("Taste DNA AI", "Build your personal taste profile", "Tell me your favorite cuisine, spice level and food preference", self._taste_dna_manual)
            return
        counts = {}
        for r in rows:
            for part in str(r["items"] or "").split(","):
                name = part.strip()
                if name:
                    counts[name.lower()] = counts.get(name.lower(), 0) + 1
        top = sorted(counts.items(), key=lambda x:x[1], reverse=True)[:5]
        items = ["🧬 YOUR TASTE DNA", "", f"Orders analyzed: {len(rows)}", "Most repeated choices:"]
        items += [f"• {name.title()} — {n} time(s)" for name,n in top]
        items += ["", "AI insight: use repeat patterns to discover similar meals without repeating the exact dish."]
        self.ai_input_page("Taste DNA AI", "Your personal food fingerprint", "", lambda q,result:self.show_ai_results(result,"Taste DNA",items))

    def _taste_dna_manual(self, q, result):
        self.show_ai_results(result, "Taste DNA", ["🧬 PERSONAL TASTE PROFILE", "", f"Preference input: {q or 'balanced food'}", "", "• Explore 2 familiar dishes + 1 new dish", "• Keep spice level consistent first", "• Compare cuisine variety before repeating"])

    def ai_smart_split(self):
        self.ai_input_page("Smart Bill Split AI", "Split a food order fairly", "Example: 4 people, total ₹1200", self._smart_split_run)

    def _smart_split_run(self, q, result):
        import re
        nums=[float(x) for x in re.findall(r"\d+(?:\.\d+)?",q)]
        people=max(1,int(nums[0])) if nums else 2
        total=nums[1] if len(nums)>1 else self.cart_total()
        self.show_ai_results(result,"Smart Bill Split",["🧾 FAIR SPLIT","",f"People: {people}",f"Total: ₹{total:.2f}",f"Equal share: ₹{total/people:.2f} each","","Add individual item prices for an item-level split."])

    def ai_leftover_rescue(self):
        rows=self.db.execute("SELECT name,price FROM foods ORDER BY price ASC").fetchall()
        items=["♻️ LEFTOVER RESCUE","","Low-cost add-ons for a fuller meal:"]+[f"• {r['name']} — ₹{r['price']:.0f}" for r in rows[:6]]+["","AI rule: use an existing cart item first, then add the smallest useful side."]
        self.ai_input_page("Leftover Rescue AI","Reduce unnecessary ordering","",lambda q,result:self.show_ai_results(result,"Leftover Rescue",items))

    def ai_value_score(self):
        rows=self.db.execute("SELECT f.name,f.price,r.name AS restaurant,r.rating FROM foods f JOIN restaurants r ON r.id=f.restaurant_id").fetchall()
        scored=[((float(r["rating"] or 0)/max(float(r["price"] or 1),1))*100,r) for r in rows]
        items=["💎 VALUE INTELLIGENCE","","Transparent heuristic = rating ÷ price × 100"]
        items += [f"• {r['name']} | {r['restaurant']} | ₹{r['price']:.0f} | value {score:.1f}" for score,r in sorted(scored,key=lambda x:x[0],reverse=True)[:7]]
        items += ["","This is a price/rating heuristic, not a quality guarantee."]
        self.ai_input_page("Value Score AI","Compare price and rating together","",lambda q,result:self.show_ai_results(result,"Value Score",items))

    def ai_eta_predictor(self):
        rows=self.db.execute("SELECT status,COUNT(*) AS n FROM orders GROUP BY status").fetchall()
        active=sum(int(r["n"]) for r in rows if str(r["status"]).lower() not in ("delivered","cancelled"))
        prep=18+min(active*3,18)
        items=["⏱️ ETA PREDICTOR","",f"Active orders in demo data: {active}",f"Estimated preparation window: {prep}–{prep+10} min","Delivery depends on rider availability and route distance.","","Demo estimate only; no live GPS traffic is used."]
        self.ai_input_page("ETA Predictor AI","Transparent delivery-time estimate","",lambda q,result:self.show_ai_results(result,"ETA Predictor",items))

    def ai_eco_choice(self):
        rows=self.db.execute("SELECT name,category,price FROM foods ORDER BY price ASC").fetchall()
        keys=("salad","veg","vegetable","idli","dosa","rice","bowl","roti","paneer")
        eco=[r for r in rows if any(k in (str(r["name"])+" "+str(r["category"])).lower() for k in keys)] or list(rows[:6])
        items=["🌱 ECO CHOICE AI","","Plant-forward / packaging-light heuristic:"]+[f"• {r['name']} — ₹{r['price']:.0f}" for r in eco[:7]]+["","Heuristic only; supplier-level carbon data is not available in this demo."]
        self.ai_input_page("Eco Choice AI","A lightweight sustainability assistant","",lambda q,result:self.show_ai_results(result,"Eco Choice",items))

    def ai_occasion_planner(self):
        self.ai_input_page("Occasion Planner AI","Plan food for birthdays, dates and gatherings","Example: birthday, 8 people, ₹2500",self._occasion_run)

    def _occasion_run(self,q,result):
        import re
        nums=[float(x) for x in re.findall(r"\d+(?:\.\d+)?",q)]
        people=max(1,int(nums[0])) if nums else 4
        budget=nums[1] if len(nums)>1 else people*300
        per=budget/people
        self.show_ai_results(result,"Occasion Planner",["🎉 OCCASION PLAN","",f"Guests: {people}",f"Budget: ₹{budget:.0f}",f"Budget/person: ₹{per:.0f}","","• 1 main per person","• 1 shared side for every 2–3 people","• 1 shared dessert","• Keep ~10% budget as buffer"])

    def ai_surprise_meal(self):
        import random
        rows=self.db.execute("SELECT name,price FROM foods").fetchall()
        picks=random.sample(list(rows),min(3,len(rows))) if rows else []
        items=["🎁 SURPRISE MEAL","","Random picks from the current menu:"]+[f"🎲 {r['name']} — ₹{r['price']:.0f}" for r in picks]+["","Use this when you want FoodGenie to decide instead of scrolling."]
        self.ai_input_page("Surprise Meal AI","Let FoodGenie choose","",lambda q,result:self.show_ai_results(result,"Surprise Meal",items))

    # ==================================================
    # RESTAURANT DASHBOARD
    # ==================================================

    def restaurant_home(self):

        self.clear()

        self.topbar(
            "Restaurant Dashboard",
            "Manage your restaurant",
            False
        )

        f = self.content()

        self.title_label(
            f,
            "Restaurant Control Center"
        ).pack(
            anchor="w",
            padx=28,
            pady=(14, 3)
        )

        grid = tk.Frame(
            f,
            bg=BG
        )

        grid.pack(
            fill="x",
            padx=22,
            pady=14
        )

        buttons = [
            ("📦", "Orders", self.restaurant_orders),
            ("🍴", "Manage Menu", self.manage_menu),
            ("➕", "Add Food", self.add_food),
            ("📊", "Sales Report", self.sales_report),
            ("⚙", "Settings", self.restaurant_settings)
        ]

        for i, (
            icon,
            title,
            command
        ) in enumerate(buttons):

            c = self.card(grid)

            c.grid(
                row=0,
                column=i,
                sticky="ew",
                padx=5
            )

            grid.columnconfigure(
                i,
                weight=1
            )

            self.label(
                c,
                icon,
                22,
                TEAL,
                True
            ).pack(
                pady=(10, 2)
            )

            self.label(
                c,
                title,
                9,
                TEXT,
                True
            ).pack(
                pady=(0, 10)
            )

            c.bind(
                "<Button-1>",
                lambda e, fun=command:
                fun()
            )

        self.make_button(
            f,
            "LOGOUT",
            self.logout,
            NAVY2
        ).pack(
            anchor="e",
            padx=28,
            pady=12
        )

    def restaurant_name(self):

        row = self.db.execute(
            "SELECT name FROM users WHERE username=?",
            (self.current_user,)
        ).fetchone()

        return (
            row["name"]
            if row
            else "Pizza Hub"
        )

    def restaurant_orders(self):

        self.clear()

        self.topbar(
            "Restaurant Orders",
            "Accept and update customer orders"
        )

        f = self.content()

        rid = self.db.execute(
            "SELECT id FROM restaurants WHERE name=?",
            (self.restaurant_name(),)
        ).fetchone()["id"]

        orders = self.db.execute(
            """
            SELECT *
            FROM orders
            WHERE restaurant_id=?
            ORDER BY id DESC
            """,
            (rid,)
        ).fetchall()

        if not orders:

            self.label(
                f,
                "No orders yet.",
                13,
                MUTED,
                True,
                BG
            ).pack(pady=37)

            return

        for order in orders:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=4
            )

            self.label(
                c,
                f'#{order["id"]} • '
                f'{order["customer"]}',
                11,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=18,
                pady=(8, 2)
            )

            self.label(
                c,
                order["items"].replace("|", " • "),
                9,
                MUTED
            ).pack(
                anchor="w",
                padx=18
            )

            self.label(
                c,
                f'₹{order["total"]:.0f} • '
                f'{order["status"]}',
                10,
                TEAL,
                True
            ).pack(
                anchor="w",
                padx=18,
                pady=2
            )

            row = tk.Frame(
                c,
                bg=WHITE
            )

            row.pack(
                anchor="e",
                padx=12,
                pady=6
            )

            for status in [
                "Accepted",
                "Preparing",
                "Ready",
                "Rejected"
            ]:

                color = (
                    RED
                    if status == "Rejected"
                    else
                    GREEN
                    if status == "Ready"
                    else NAVY2
                )

                self.make_button(
                    row,
                    status,
                    lambda oid=order["id"],
                    st=status:
                    self.change_order_status(
                        oid,
                        st
                    ),
                    color
                ).pack(
                    side="left",
                    padx=2
                )

    def change_order_status(
        self,
        oid,
        status
    ):

        self.db.execute(
            """
            UPDATE orders
            SET status=?
            WHERE id=?
            """,
            (status, oid)
        )

        if status == "Ready":

            rider = self.db.execute(
                """
                SELECT id
                FROM riders
                WHERE available=1
                LIMIT 1
                """
            ).fetchone()

            if rider:

                self.db.execute(
                    """
                    UPDATE orders
                    SET rider_id=?
                    WHERE id=?
                    """,
                    (rider["id"], oid)
                )

                self.db.execute(
                    """
                    UPDATE riders
                    SET available=0
                    WHERE id=?
                    """,
                    (rider["id"],)
                )

        self.db.commit()

        self.restaurant_orders()

    # ==================================================
    # MENU
    # ==================================================

    def manage_menu(self):

        self.clear()

        self.topbar(
            "Manage Menu",
            "View current menu items"
        )

        f = self.content()

        rid = self.db.execute(
            "SELECT id FROM restaurants WHERE name=?",
            (self.restaurant_name(),)
        ).fetchone()["id"]

        foods = self.db.execute(
            """
            SELECT *
            FROM foods
            WHERE restaurant_id=?
            """,
            (rid,)
        ).fetchall()

        for food in foods:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=2
            )

            self.label(
                c,
                food["name"],
                10,
                TEXT,
                True
            ).pack(
                side="left",
                padx=18,
                pady=7
            )

            self.label(
                c,
                f'₹{food["price"]:.0f}',
                10,
                TEAL,
                True
            ).pack(
                side="right",
                padx=18
            )

        self.make_button(
            f,
            "ADD NEW FOOD",
            self.add_food,
            TEAL
        ).pack(
            anchor="e",
            padx=28,
            pady=11
        )

    def add_food(self):

        self.clear()

        self.topbar(
            "Add Food",
            "Add a new menu item"
        )

        f = self.content()

        self.title_label(
            f,
            "New Menu Item"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        entries = []

        for field in [
            "Food Name",
            "Category",
            "Price",
            "Description"
        ]:

            self.label(
                f,
                field,
                9,
                MUTED,
                True,
                BG
            ).pack(
                anchor="w",
                padx=28,
                pady=(5, 2)
            )

            entry = tk.Entry(
                f,
                font=(FONT, 11),
                bg=WHITE,
                fg=TEXT,
                bd=0
            )

            entry.pack(
                fill="x",
                padx=28,
                ipady=10
            )

            entries.append(entry)

        def save():

            try:
                price = float(
                    entries[2].get()
                )

            except:

                messagebox.showwarning(
                    "Menu",
                    "Enter valid price."
                )

                return

            rid = self.db.execute(
                "SELECT id FROM restaurants WHERE name=?",
                (self.restaurant_name(),)
            ).fetchone()["id"]

            self.db.execute(
                """
                INSERT INTO foods
                (
                    restaurant_id,
                    name,
                    category,
                    price,
                    description
                )
                VALUES(?,?,?,?,?)
                """,
                (
                    rid,
                    entries[0].get(),
                    entries[1].get(),
                    price,
                    entries[3].get()
                )
            )

            self.db.commit()

            messagebox.showinfo(
                "Menu",
                "Food added successfully."
            )

            self.manage_menu()

        self.make_button(
            f,
            "SAVE FOOD",
            save,
            TEAL
        ).pack(
            anchor="e",
            padx=28,
            pady=11
        )

    # ==================================================
    # SALES
    # ==================================================

    def sales_report(self):

        self.clear()

        self.topbar(
            "Sales Report",
            "Restaurant performance"
        )

        f = self.content()

        rid = self.db.execute(
            "SELECT id FROM restaurants WHERE name=?",
            (self.restaurant_name(),)
        ).fetchone()["id"]

        orders = self.db.execute(
            """
            SELECT *
            FROM orders
            WHERE restaurant_id=?
            AND status!='Rejected'
            """,
            (rid,)
        ).fetchall()

        total = sum(
            float(x["total"])
            for x in orders
        )

        average = (
            total / len(orders)
            if orders
            else 0
        )

        self.title_label(
            f,
            "Sales Overview"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        stats = [
            ("Orders", len(orders)),
            ("Revenue", f"₹{total:.0f}"),
            ("Average Order", f"₹{average:.0f}")
        ]

        for key, value in stats:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=3
            )

            self.label(
                c,
                key,
                10,
                MUTED,
                True
            ).pack(
                side="left",
                padx=18,
                pady=9
            )

            self.label(
                c,
                str(value),
                14,
                TEAL,
                True
            ).pack(
                side="right",
                padx=18
            )

    def restaurant_settings(self):

        self.clear()

        self.topbar(
            "Restaurant Settings",
            "Account details"
        )

        f = self.content()

        self.title_label(
            f,
            "Settings"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        self.show_ai_results(
            f,
            "Restaurant Account",
            [
                f"Login: {self.current_user}",
                f"Restaurant: {self.restaurant_name()}",
                "Status: Active"
            ]
        )

    # ==================================================
    # RIDER
    # ==================================================

    def rider_home(self):

        self.clear()

        self.topbar(
            "Delivery Dashboard",
            "Assigned deliveries",
            False
        )

        f = self.content()

        self.title_label(
            f,
            "Rider Control Center"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        rider = self.db.execute(
            "SELECT * FROM riders WHERE username=?",
            (self.current_user,)
        ).fetchone()

        self.label(
            f,
            f'🏍 {rider["name"]} • ★ {rider["rating"]}',
            12,
            TEXT,
            True,
            BG
        ).pack(
            anchor="w",
            padx=28
        )

        self.label(
            f,
            f'{rider["vehicle"]} • {rider["phone"]}',
            9,
            MUTED,
            False,
            BG
        ).pack(
            anchor="w",
            padx=28,
            pady=2
        )

        grid = tk.Frame(
            f,
            bg=BG
        )

        grid.pack(
            fill="x",
            padx=22,
            pady=12
        )

        buttons = [
            ("📦", "Assigned Orders", self.rider_orders),
            ("📍", "Delivery Map", self.rider_map)
        ]

        for i, (
            icon,
            title,
            command
        ) in enumerate(buttons):

            c = self.card(grid)

            c.grid(
                row=0,
                column=i,
                sticky="ew",
                padx=6
            )

            grid.columnconfigure(
                i,
                weight=1
            )

            self.label(
                c,
                icon,
                25,
                TEAL,
                True
            ).pack(
                pady=(12, 3)
            )

            self.label(
                c,
                title,
                10,
                TEXT,
                True
            ).pack(
                pady=(0, 12)
            )

            c.bind(
                "<Button-1>",
                lambda e, fun=command:
                fun()
            )

        self.make_button(
            f,
            "LOGOUT",
            self.logout,
            NAVY2
        ).pack(
            anchor="e",
            padx=28,
            pady=12
        )

    def rider_orders(self):

        self.clear()

        self.topbar(
            "Assigned Deliveries",
            "Orders assigned to you"
        )

        f = self.content()

        rider = self.db.execute(
            "SELECT id FROM riders WHERE username=?",
            (self.current_user,)
        ).fetchone()

        orders = self.db.execute(
            """
            SELECT o.*,r.name restaurant
            FROM orders o
            JOIN restaurants r
            ON r.id=o.restaurant_id
            WHERE o.rider_id=?
            ORDER BY o.id DESC
            """,
            (rider["id"],)
        ).fetchall()

        if not orders:

            self.label(
                f,
                "No assigned orders.",
                13,
                MUTED,
                True,
                BG
            ).pack(pady=37)

            return

        for order in orders:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=4
            )

            self.label(
                c,
                f'#{order["id"]} • '
                f'{order["restaurant"]}',
                11,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=18,
                pady=(8, 2)
            )

            self.label(
                c,
                f'{order["address"]} • '
                f'₹{order["total"]:.0f}',
                9,
                MUTED
            ).pack(
                anchor="w",
                padx=18
            )

            self.label(
                c,
                order["status"],
                10,
                TEAL,
                True
            ).pack(
                anchor="w",
                padx=18,
                pady=2
            )

            row = tk.Frame(
                c,
                bg=WHITE
            )

            row.pack(
                anchor="e",
                padx=12,
                pady=6
            )

            self.make_button(
                row,
                "PICK UP",
                lambda oid=order["id"]:
                self.rider_pickup(oid),
                NAVY2
            ).pack(
                side="left",
                padx=3
            )

            self.make_button(
                row,
                "DELIVERED",
                lambda oid=order["id"]:
                self.rider_delivery(oid),
                GREEN
            ).pack(
                side="left",
                padx=3
            )

    def rider_pickup(self, oid):

        self.db.execute(
            """
            UPDATE orders
            SET status='Out for Delivery'
            WHERE id=?
            """,
            (oid,)
        )

        self.db.commit()

        self.rider_orders()

    def rider_delivery(self, oid):

        row = self.db.execute(
            "SELECT rider_id FROM orders WHERE id=?",
            (oid,)
        ).fetchone()

        self.db.execute(
            """
            UPDATE orders
            SET status='Delivered'
            WHERE id=?
            """,
            (oid,)
        )

        if row and row["rider_id"]:

            self.db.execute(
                """
                UPDATE riders
                SET available=1
                WHERE id=?
                """,
                (row["rider_id"],)
            )

        self.db.commit()

        self.rider_orders()

    def rider_map(self):

        self.clear()

        self.topbar(
            "Delivery Map",
            "Rider route overview"
        )

        f = self.content()

        self.title_label(
            f,
            "Route Map"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        canvas = tk.Canvas(
            f,
            width=900,
            height=430,
            bg="#E8F0F4",
            highlightthickness=0
        )

        canvas.pack(
            padx=28
        )

        for y in [
            80,
            170,
            260,
            350
        ]:

            canvas.create_line(
                0,
                y,
                900,
                y,
                fill="#C5D3DA",
                width=25
            )

        for x in [
            120,
            310,
            520,
            730
        ]:

            canvas.create_line(
                x,
                0,
                x,
                430,
                fill="#C5D3DA",
                width=22
            )

        canvas.create_text(
            450,
            210,
            text="🏍 RIDER ROUTE",
            font=(FONT, 20, "bold"),
            fill=NAVY
        )

    # ==================================================
    # ADMIN
    # ==================================================

    def admin_home(self):

        self.clear()

        self.topbar(
            "Admin Dashboard",
            "Platform overview",
            False
        )

        f = self.content()

        self.title_label(
            f,
            "FoodGenie Administration"
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        users = self.db.execute(
            "SELECT COUNT(*) n FROM users"
        ).fetchone()["n"]

        restaurants = self.db.execute(
            "SELECT COUNT(*) n FROM restaurants"
        ).fetchone()["n"]

        orders = self.db.execute(
            "SELECT COUNT(*) n FROM orders"
        ).fetchone()["n"]

        revenue = self.db.execute(
            """
            SELECT COALESCE(SUM(total),0) n
            FROM orders
            WHERE status!='Rejected'
            """
        ).fetchone()["n"]

        grid = tk.Frame(
            f,
            bg=BG
        )

        grid.pack(
            fill="x",
            padx=22
        )

        stats = [
            ("Users", users),
            ("Restaurants", restaurants),
            ("Orders", orders),
            ("Revenue", f"₹{revenue:.0f}")
        ]

        for i, (key, value) in enumerate(stats):

            c = self.card(grid)

            c.grid(
                row=0,
                column=i,
                sticky="ew",
                padx=5
            )

            grid.columnconfigure(
                i,
                weight=1
            )

            self.label(
                c,
                key,
                9,
                MUTED,
                True
            ).pack(
                anchor="w",
                padx=16,
                pady=(10, 3)
            )

            self.label(
                c,
                str(value),
                20,
                TEAL,
                True
            ).pack(
                anchor="w",
                padx=16,
                pady=(0, 10)
            )

        self.make_button(
            f,
            "VIEW ALL ORDERS",
            self.admin_orders,
            NAVY2
        ).pack(
            anchor="w",
            padx=28,
            pady=14
        )

        self.make_button(
            f,
            "LOGOUT",
            self.logout,
            NAVY2
        ).pack(
            anchor="e",
            padx=28
        )

    def admin_orders(self):

        self.clear()

        self.topbar(
            "All Orders",
            "Platform-wide order monitoring"
        )

        f = self.content()

        rows = self.db.execute(
            """
            SELECT o.*,r.name restaurant
            FROM orders o
            JOIN restaurants r
            ON r.id=o.restaurant_id
            ORDER BY o.id DESC
            """
        ).fetchall()

        for order in rows:

            c = self.card(f)

            c.pack(
                fill="x",
                padx=28,
                pady=3
            )

            self.label(
                c,
                f'#{order["id"]} • '
                f'{order["customer"]} • '
                f'{order["restaurant"]}',
                10,
                TEXT,
                True
            ).pack(
                anchor="w",
                padx=18,
                pady=(8, 1)
            )

            self.label(
                c,
                f'₹{order["total"]:.0f} • '
                f'{order["status"]} • '
                f'{order["created_at"][:16]}',
                9,
                MUTED
            ).pack(
                anchor="w",
                padx=18,
                pady=(0, 8)
            )


# ======================================================
# RUN APP
# ======================================================

if __name__ == "__main__":

    app = FoodGenie()

    app.mainloop()