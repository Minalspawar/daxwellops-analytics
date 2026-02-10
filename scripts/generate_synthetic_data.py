import random
import json
from datetime import date, timedelta
import pandas as pd

random.seed(7)

START = date(2025, 12, 1)
DAYS = 60

customers = [
    ("C001", "HealthSupply Co", "Healthcare"),
    ("C002", "FoodServe Distributors", "Food Service"),
    ("C003", "IndustrialMart", "Industrial"),
    ("C004", "WholesaleHub", "Wholesale"),
]
skus = [
    ("SKU001", "Nitrile Gloves M", "gloves", 4.50),
    ("SKU002", "Nitrile Gloves L", "gloves", 4.60),
    ("SKU003", "Vinyl Gloves M", "gloves", 3.10),
    ("SKU004", "Disposable Gowns", "apparel", 7.80),
    ("SKU005", "Food Prep Wipes", "wipes", 2.20),
]

def daterange(start, days):
    for i in range(days):
        yield start + timedelta(days=i)

# Contracts
contracts = []
for cid, _, _ in customers:
    for sku, _, _, unit_cost in skus:
        base = unit_cost * random.uniform(1.25, 1.6)
        moq = random.choice([50, 100, 200])
        eff_start = START
        eff_end = START + timedelta(days=DAYS + 30)
        contracts.append({
            "customer_id": cid,
            "sku_id": sku,
            "agreed_price": round(base, 2),
            "moq": moq,
            "effective_start": str(eff_start),
            "effective_end": str(eff_end),
        })

# Sales orders
orders = []
order_id = 10000
for d in daterange(START, DAYS):
    for _ in range(random.randint(8, 18)):
        cid, _, _ = random.choice(customers)
        sku, _, _, _ = random.choice(skus)
        qty = random.choice([20, 30, 50, 75, 100, 150, 200])
        promised = d + timedelta(days=random.choice([2, 3, 4, 5, 7]))
        contract_price = [c["agreed_price"] for c in contracts if c["customer_id"] == cid and c["sku_id"] == sku][0]
        price = contract_price
        # Inject ~5% violations
        if random.random() < 0.05:
            price = round(contract_price * random.uniform(0.85, 1.15), 2)

        orders.append({
            "order_id": f"O{order_id}",
            "order_date": str(d),
            "customer_id": cid,
            "sku_id": sku,
            "qty_ordered": qty,
            "unit_price": price,
            "promised_ship_date": str(promised),
        })
        order_id += 1

orders_df = pd.DataFrame(orders)

# Shipments JSONL (semi-structured)
shipments = []
for _, row in orders_df.sample(frac=0.9, random_state=7).iterrows():
    qty_shipped = int(row["qty_ordered"])
    if random.random() < 0.15:
        qty_shipped = int(row["qty_ordered"] * random.choice([0.5, 0.7, 0.8]))

    ship_date = pd.to_datetime(row["order_date"]).date() + timedelta(days=random.choice([1,2,3,4,5,6]))
    deliver_date = ship_date + timedelta(days=random.choice([1,2,3,4]))

    shipments.append({
        "shipment_id": f"S{random.randint(100000,999999)}",
        "order_id": row["order_id"],
        "ship_date": str(ship_date),
        "delivered_date": str(deliver_date),
        "qty_shipped": int(qty_shipped),
        "carrier": random.choice(["UPS", "FedEx", "DHL", "RegionalCarrier"]),
        "event_meta": {"warehouse": random.choice(["HOU1","HOU2"]), "priority": random.choice(["std","exp"])}
    })

# Inventory snapshots
inv_rows = []
on_hand = {sku[0]: random.randint(500, 2500) for sku in skus}
for d in daterange(START, DAYS):
    day_orders = orders_df[orders_df["order_date"] == str(d)]
    for sku_id, g in day_orders.groupby("sku_id"):
        on_hand[sku_id] = max(0, on_hand[sku_id] - int(g["qty_ordered"].sum() * 0.8))
    for sku_id in on_hand:
        on_hand[sku_id] += random.randint(20, 120)

    for sku_id, oh in on_hand.items():
        inv_rows.append({
            "snapshot_date": str(d),
            "sku_id": sku_id,
            "on_hand_qty": int(oh),
            "on_order_qty": random.randint(0, 300)
        })

inventory_df = pd.DataFrame(inv_rows)

# Production batches
prod_rows = []
batch_id = 5000
for d in daterange(START, DAYS):
    for sku, _, _, _ in skus:
        produced = random.randint(100, 400)
        scrap = int(produced * random.uniform(0.01, 0.06))
        prod_rows.append({
            "batch_id": f"B{batch_id}",
            "production_date": str(d),
            "sku_id": sku,
            "line": random.choice(["Line1","Line2","Line3"]),
            "shift": random.choice(["A","B","C"]),
            "qty_produced": produced,
            "scrap_qty": scrap,
        })
        batch_id += 1

production_df = pd.DataFrame(prod_rows)

# Write files
orders_df.to_csv("data/landing/sales_orders.csv", index=False)
pd.DataFrame(contracts).to_csv("data/landing/contracts.csv", index=False)
inventory_df.to_csv("data/landing/inventory_snapshots.csv", index=False)
production_df.to_csv("data/landing/production_batches.csv", index=False)

with open("data/landing/shipments.json", "w", encoding="utf-8") as f:
    for e in shipments:
        f.write(json.dumps(e) + "\n")

print("? Generated landing data in data/landing/")