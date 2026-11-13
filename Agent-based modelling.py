import mesa
import random

class ShopperAgent(mesa.Agent):
    """
    A data-driven consumer agent with a randomized budget and price sensitivity weight.
    Evaluates store items based on intrinsic utility, shelf placement, and active promotions.
    """

    def __init__(self, model):
        super().__init__(model)
        self.budget = random.uniform(30.0, 100.0)
        self.price_sensitivity = random.uniform(0.3, 0.7)  # Gamma parameter
        self.basket = []

    def step(self):
        for item in self.model.inventory:
            self.evaluate_and_buy(item)

    def evaluate_and_buy(self, item):
        price = item["promo_price"] if item["has_promo"] else item["regular_price"]
        if self.budget < price:
            return

        # 1. Shelf Placement Weightage (M_tier)
        if item["shelf_tier"] == "eye_level":
            tier_weight = 1.35  # ~35% sales uplift at eye-level
        elif item["shelf_tier"] == "chest_level":
            tier_weight = 1.25  # ~25% sales uplift at chest-level
        elif item["shelf_tier"] == "waist_level":
            tier_weight = 1.10  # ~10% sales uplift at waist-level
        else:  # stoop_level or knee_level
            tier_weight = 0.80  # Lower visibility penalty zone

        # 2. Promotional Sensitivity Modifier
        discount_pct = (item["regular_price"] - item["promo_price"]) / item["regular_price"] if item["has_promo"] else 0.0
        promo_multiplier = 1.0 + (self.price_sensitivity * discount_pct)

        # Final purchase probability calculation
        purchase_prob = min(item["base_utility"] * tier_weight * promo_multiplier, 1.0)

        if random.random() < purchase_prob:
            self.basket.append(item)
            self.budget -= price
            self.model.total_revenue += price
            self.model.total_profit += (price - item["unit_cost"])
            self.model.items_sold += 1


class StoreModel(mesa.Model):
    def __init__(self, inventory_data, num_shoppers=100):
        super().__init__()
        self.inventory = inventory_data
        self.num_shoppers = num_shoppers
        self.total_revenue = 0.0
        self.total_profit = 0.0
        self.items_sold = 0

        for _ in range(self.num_shoppers):
            ShopperAgent(self)

    def step(self):
        self.agents.shuffle_do("step")

if __name__ == "__main__":
# Sample data-driven inventory mimicking HK Circle K field observations
    data = [
        {"items": "Coffee + Bun", "regular_price": 24.0, "promo_price": 18.0, "unit_cost": 9.0, "base_utility": 0.45, "shelf_tier": "eye_level", "has_promo": True},
        {"items": "Water + Yogurt", "regular_price": 20.0, "promo_price": 20.0, "unit_cost": 8.0, "base_utility": 0.35, "shelf_tier": "chest_level", "has_promo": False},
        {"items": "Hot Meal + Drink", "regular_price": 38.0, "promo_price": 30.0, "unit_cost": 15.0, "base_utility": 0.55, "shelf_tier": "eye_level", "has_promo": True},
        {"items": "Bento + Green Tea", "regular_price": 42.0, "promo_price": 35.0, "unit_cost": 18.0, "base_utility": 0.50, "shelf_tier": "eye_level", "has_promo": True},
        {"items": "Fish Balls + Drink", "regular_price": 26.0, "promo_price": 20.0, "unit_cost": 10.0, "base_utility": 0.40, "shelf_tier": "waist_level", "has_promo": True},
        {"items": "Beer 4-pack + Chips", "regular_price": 65.0, "promo_price": 55.0, "unit_cost": 30.0, "base_utility": 0.45, "shelf_tier": "knee_level", "has_promo": True}
    ]

    print("--- Running Data-Driven Simulation Model ---")
    model = StoreModel(inventory_data=data, num_shoppers=1)
    
    # Run simulation for 5 time-steps
    for step_num in range(1, 6):
        model.step()

    print(f"Total Revenue:  HK${model.total_revenue:.2f}")
    print(f"Total Profit:   HK${model.total_profit:.2f}")
    print(f"Total Items Sold: {model.items_sold}")