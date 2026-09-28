import math
from database import query, one


# =========================================================
# FOODGENIE AI ENGINE
# =========================================================


# ---------------------------------------------------------
# 1. REVIEW SENTIMENT ANALYSIS
# ---------------------------------------------------------

POSITIVE_WORDS = [
    "good",
    "great",
    "tasty",
    "delicious",
    "excellent",
    "fresh",
    "fast",
    "amazing",
    "nice",
    "love",
    "awesome",
    "perfect",
    "friendly",
    "clean",
    "hot",
    "best"
]

NEGATIVE_WORDS = [
    "bad",
    "late",
    "cold",
    "poor",
    "slow",
    "worst",
    "terrible",
    "expensive",
    "missing",
    "delay",
    "dirty",
    "rude",
    "unhappy",
    "waste",
    "disappointed"
]


def sentiment(text):
    """
    Analyze customer review and return:
    Positive / Negative / Neutral
    """

    if not text:
        return "Neutral"

    text = text.lower()

    positive_score = 0
    negative_score = 0

    for word in POSITIVE_WORDS:
        if word in text:
            positive_score += 1

    for word in NEGATIVE_WORDS:
        if word in text:
            negative_score += 1

    if positive_score > negative_score:
        return "Positive"

    if negative_score > positive_score:
        return "Negative"

    return "Neutral"


# ---------------------------------------------------------
# 2. FOOD RECOMMENDATION
# ---------------------------------------------------------

def recommend(user_id, limit=8):
    """
    Recommend foods based on:
    - Food rating
    - Restaurant rating
    - Previous orders
    - Delivery time
    """

    foods = query("""
        SELECT
            f.*,
            r.name AS restaurant_name,
            r.rating AS restaurant_rating,
            r.delivery_time
        FROM foods f
        JOIN restaurants r
        ON r.id = f.restaurant_id
        WHERE f.available = 1
    """)

    if not foods:
        return []

    history = query("""
        SELECT
            oi.food_id,
            SUM(oi.qty) AS quantity
        FROM order_items oi
        JOIN orders o
        ON o.id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY oi.food_id
    """, (user_id,))

    previous_orders = {
        row["food_id"]: row["quantity"]
        for row in history
    }

    scored_foods = []

    for food in foods:

        score = 0

        # Food rating
        score += food["rating"] * 2

        # Restaurant rating
        score += food["restaurant_rating"]

        # Previously ordered food
        previous_quantity = previous_orders.get(
            food["id"],
            0
        )

        score += min(
            previous_quantity * 0.5,
            3
        )

        # Faster delivery gets a small bonus
        score += max(
            0,
            (45 - food["delivery_time"]) / 30
        )

        scored_foods.append(
            (score, food)
        )

    scored_foods.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        item[1]
        for item in scored_foods[:limit]
    ]


# ---------------------------------------------------------
# 3. SMART FOOD SEARCH
# ---------------------------------------------------------

def smart_search(
    text,
    max_price=None,
    veg=None,
    category=None
):
    """
    AI-style smart food search.
    """

    if not text:
        text = ""

    text = text.lower().strip()

    foods = query("""
        SELECT
            f.*,
            r.name AS restaurant_name,
            r.rating AS restaurant_rating,
            r.delivery_time
        FROM foods f
        JOIN restaurants r
        ON r.id = f.restaurant_id
        WHERE f.available = 1
    """)

    keywords = set(text.split())

    results = []

    for food in foods:

        searchable_text = (
            f"{food['name']} "
            f"{food['category']} "
            f"{food['restaurant_name']}"
        ).lower()

        score = 0

        # Keyword matching
        for keyword in keywords:

            if keyword in searchable_text:
                score += 2

        # Special AI understanding
        if "spicy" in keywords:

            spicy_foods = [
                "chicken",
                "biryani",
                "burger",
                "pizza"
            ]

            if any(
                item in searchable_text
                for item in spicy_foods
            ):
                score += 3

        if "healthy" in keywords:

            if food["category"].lower() == "healthy":
                score += 4

        if "cheap" in keywords:

            if food["price"] <= 150:
                score += 3

        if "budget" in keywords:

            if food["price"] <= 200:
                score += 3

        if "fast" in keywords:

            if food["delivery_time"] <= 25:
                score += 3

        # Price filter
        if max_price is not None:

            if food["price"] <= max_price:
                score += 1
            else:
                continue

        # Veg filter
        if veg is True and not food["veg"]:
            continue

        # Non-veg filter
        if veg is False and food["veg"]:
            continue

        # Category filter
        if category:

            if category.lower() not in \
                    food["category"].lower():

                continue

        if score > 0:

            results.append(
                (score, food)
            )

    results.sort(
        key=lambda item: (
            item[0],
            item[1]["rating"]
        ),
        reverse=True
    )

    return [
        item[1]
        for item in results
    ]


# ---------------------------------------------------------
# 4. MEAL PLANNER
# ---------------------------------------------------------

def meal_plan(
    budget,
    people,
    preference="any"
):
    """
    Generate a simple AI-based meal plan
    based on budget, people and preference.
    """

    foods = query("""
        SELECT
            f.*,
            r.name AS restaurant_name
        FROM foods f
        JOIN restaurants r
        ON r.id = f.restaurant_id
        WHERE f.available = 1
    """)

    preference = preference.lower()

    candidates = []

    for food in foods:

        if "veg" in preference:

            if not food["veg"]:
                continue

        if "non" in preference:

            if food["veg"]:
                continue

        candidates.append(food)

    # Highest rated food first
    candidates.sort(
        key=lambda item: item["rating"],
        reverse=True
    )

    selected = []
    total = 0

    # Number of items depends on people
    max_items = max(
        2,
        people + 1
    )

    for food in candidates:

        if len(selected) >= max_items:
            break

        if total + food["price"] <= budget:

            selected.append(food)

            total += food["price"]

    return selected, total


# ---------------------------------------------------------
# 5. DELIVERY ETA PREDICTION
# ---------------------------------------------------------

def predict_eta(
    restaurant_id,
    distance_km=3.0,
    order_load=2
):
    """
    Estimate delivery time.
    """

    restaurant = one("""
        SELECT delivery_time
        FROM restaurants
        WHERE id = ?
    """, (restaurant_id,))

    if restaurant:

        base_time = restaurant["delivery_time"]

    else:

        base_time = 30

    # Distance impact
    distance_time = distance_km * 4

    # Current restaurant order load
    load_time = order_load * 3

    eta = (
        base_time
        + distance_time
        + load_time
    )

    eta = max(
        10,
        round(eta)
    )

    return eta


# ---------------------------------------------------------
# 6. DEMAND FORECASTING
# ---------------------------------------------------------

def demand_forecast():
    """
    Predict which foods may have higher demand.
    """

    foods = query("""
        SELECT
            f.id,
            f.name,
            f.category,
            f.rating,
            COUNT(oi.id) AS order_count
        FROM foods f
        LEFT JOIN order_items oi
        ON f.id = oi.food_id
        GROUP BY f.id
        ORDER BY order_count DESC,
                 f.rating DESC
        LIMIT 15
    """)

    results = []

    for food in foods:

        predicted_demand = (
            food["order_count"] * 1.25
            + food["rating"] * 5
        )

        results.append({
            "name": food["name"],
            "category": food["category"],
            "orders": food["order_count"],
            "rating": food["rating"],
            "forecast": round(
                predicted_demand,
                1
            )
        })

    return results


# ---------------------------------------------------------
# 7. POPULAR FOOD ANALYSIS
# ---------------------------------------------------------

def popular_foods(limit=10):

    foods = query("""
        SELECT
            f.name,
            f.category,
            f.price,
            f.rating,
            COUNT(oi.id) AS total_orders
        FROM foods f
        LEFT JOIN order_items oi
        ON f.id = oi.food_id
        GROUP BY f.id
        ORDER BY total_orders DESC,
                 f.rating DESC
        LIMIT ?
    """, (limit,))

    return foods


# ---------------------------------------------------------
# 8. RESTAURANT RECOMMENDATION
# ---------------------------------------------------------

def recommend_restaurants(limit=6):

    restaurants = query("""
        SELECT *
        FROM restaurants
        WHERE active = 1
        ORDER BY rating DESC,
                 delivery_time ASC
        LIMIT ?
    """, (limit,))

    return restaurants


# ---------------------------------------------------------
# 9. BUDGET FOOD RECOMMENDATION
# ---------------------------------------------------------

def budget_recommendation(
    budget,
    limit=10
):

    foods = query("""
        SELECT
            f.*,
            r.name AS restaurant_name,
            r.rating AS restaurant_rating
        FROM foods f
        JOIN restaurants r
        ON r.id = f.restaurant_id
        WHERE f.available = 1
          AND f.price <= ?
        ORDER BY f.rating DESC
        LIMIT ?
    """, (budget, limit))

    return foods


# ---------------------------------------------------------
# 10. COMBO RECOMMENDATION
# ---------------------------------------------------------

def combo_recommendation():

    foods = query("""
        SELECT
            f.*,
            r.name AS restaurant_name
        FROM foods f
        JOIN restaurants r
        ON r.id = f.restaurant_id
        WHERE f.available = 1
        ORDER BY f.rating DESC
    """)

    mains = []
    sides = []
    desserts = []

    for food in foods:

        category = food["category"].lower()

        if (
            "pizza" in category
            or "burger" in category
            or "biryani" in category
            or "meals" in category
        ):
            mains.append(food)

        elif (
            "side" in category
            or "fries" in category
        ):
            sides.append(food)

        elif (
            "dessert" in category
        ):
            desserts.append(food)

    combo = []

    if mains:
        combo.append(mains[0])

    if sides:
        combo.append(sides[0])

    if desserts:
        combo.append(desserts[0])

    return combo


# ---------------------------------------------------------
# 11. SUSPICIOUS ORDER DETECTION
# ---------------------------------------------------------

def suspicious_order(
    total,
    recent_orders
):
    """
    Simple rule-based suspicious order detector.
    """

    if total > 2000:
        return True

    if recent_orders >= 8:
        return True

    return False


# ---------------------------------------------------------
# 12. CUSTOMER PREFERENCE ANALYSIS
# ---------------------------------------------------------

def customer_preferences(user_id):

    rows = query("""
        SELECT
            f.category,
            SUM(oi.qty) AS quantity
        FROM order_items oi
        JOIN orders o
        ON o.id = oi.order_id
        JOIN foods f
        ON f.id = oi.food_id
        WHERE o.user_id = ?
        GROUP BY f.category
        ORDER BY quantity DESC
    """, (user_id,))

    return rows


# ---------------------------------------------------------
# 13. REPEAT ORDER PREDICTION
# ---------------------------------------------------------

def repeat_order_prediction(user_id):

    rows = query("""
        SELECT
            f.name,
            SUM(oi.qty) AS quantity
        FROM order_items oi
        JOIN orders o
        ON o.id = oi.order_id
        JOIN foods f
        ON f.id = oi.food_id
        WHERE o.user_id = ?
        GROUP BY f.id
        ORDER BY quantity DESC
        LIMIT 5
    """, (user_id,))

    return rows


# ---------------------------------------------------------
# 14. REVIEW ANALYSIS
# ---------------------------------------------------------

def review_analysis():

    reviews = query("""
        SELECT
            rating,
            comment,
            sentiment
        FROM reviews
        ORDER BY id DESC
    """)

    positive = 0
    negative = 0
    neutral = 0

    for review in reviews:

        result = review["sentiment"]

        if result == "Positive":
            positive += 1

        elif result == "Negative":
            negative += 1

        else:
            neutral += 1

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "total": len(reviews)
    }


# ---------------------------------------------------------
# 15. SIMPLE DELIVERY ROUTE OPTIMIZATION
# ---------------------------------------------------------

def shortest_route(points):

    if not points:
        return []

    remaining = list(points)

    route = [
        remaining.pop(0)
    ]

    while remaining:

        current = route[-1]

        nearest = min(
            remaining,
            key=lambda point:
            math.dist(current, point)
        )

        remaining.remove(nearest)

        route.append(nearest)

    return route


# ---------------------------------------------------------
# 16. AI CHATBOT
# ---------------------------------------------------------

def chatbot(message):

    if not message:
        return (
            "Hello! I am FoodGenie AI. "
            "Ask me about food, restaurants, "
            "orders or recommendations."
        )

    text = message.lower()

    if "hello" in text or "hi" in text:

        return (
            "Hello! 👋 Welcome to FoodGenie AI."
        )

    if "recommend" in text:

        return (
            "I can recommend foods based on "
            "ratings, previous orders and "
            "delivery time."
        )

    if "pizza" in text:

        return (
            "Pizza Hub has popular options "
            "like Margherita Pizza and "
            "Chicken Pizza."
        )

    if "biryani" in text:

        return (
            "Biryani Express offers Chicken, "
            "Mutton and Veg Biryani."
        )

    if "healthy" in text:

        return (
            "Try our healthy food options "
            "from Green Bowl."
        )

    if "cheap" in text or "budget" in text:

        return (
            "I can help you find food within "
            "your budget."
        )

    if "delivery" in text:

        return (
            "FoodGenie can estimate delivery "
            "time using restaurant load and "
            "distance."
        )

    if "order" in text:

        return (
            "You can view your current and "
            "previous orders from Order History."
        )

    return (
        "I can help with food recommendations, "
        "restaurants, delivery, orders, budget "
        "meals and healthy food."
    )