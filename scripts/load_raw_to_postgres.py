import os, json
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql+psycopg2://daxwell:daxwellpass@localhost:5433/daxwell_dw"
LANDING = os.path.join("data", "landing")

def read_shipments_jsonl(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            rows.append({
                "shipment_id": e["shipment_id"],
                "order_id": e["order_id"],
                "ship_date": e["ship_date"],
                "delivered_date": e["delivered_date"],
                "qty_shipped": e["qty_shipped"],
                "carrier": e["carrier"],
                "warehouse": (e.get("event_meta") or {}).get("warehouse"),
                "priority": (e.get("event_meta") or {}).get("priority"),
            })
    df = pd.DataFrame(rows)
    return df

def main():
    engine = create_engine(DB_URL)

    sales = pd.read_csv(os.path.join(LANDING, "sales_orders.csv"), parse_dates=["order_date","promised_ship_date"])
    contracts = pd.read_csv(os.path.join(LANDING, "contracts.csv"), parse_dates=["effective_start","effective_end"])
    inv = pd.read_csv(os.path.join(LANDING, "inventory_snapshots.csv"), parse_dates=["snapshot_date"])
    prod = pd.read_csv(os.path.join(LANDING, "production_batches.csv"), parse_dates=["production_date"])
    ship = read_shipments_jsonl(os.path.join(LANDING, "shipments.json"))
    ship["ship_date"] = pd.to_datetime(ship["ship_date"])
    ship["delivered_date"] = pd.to_datetime(ship["delivered_date"])

    # Basic sanity checks
    assert sales["order_id"].notna().all()
    assert not sales["order_id"].duplicated().any()
    assert (sales["qty_ordered"] > 0).all()
    assert (contracts["effective_end"] >= contracts["effective_start"]).all()

    # Load (truncate then insert)
    with engine.begin() as conn:
        conn.execute(text("truncate raw.sales_orders"))
        conn.execute(text("truncate raw.contracts"))
        conn.execute(text("truncate raw.shipments"))
        conn.execute(text("truncate raw.inventory_snapshots"))
        conn.execute(text("truncate raw.production_batches"))

        sales.to_sql("sales_orders", conn, schema="raw", if_exists="append", index=False, method="multi", chunksize=2000)
        contracts.to_sql("contracts", conn, schema="raw", if_exists="append", index=False, method="multi", chunksize=2000)
        ship.to_sql("shipments", conn, schema="raw", if_exists="append", index=False, method="multi", chunksize=2000)
        inv.to_sql("inventory_snapshots", conn, schema="raw", if_exists="append", index=False, method="multi", chunksize=2000)
        prod.to_sql("production_batches", conn, schema="raw", if_exists="append", index=False, method="multi", chunksize=2000)

    print("? Loaded raw tables:")
    print(f"  sales_orders: {len(sales)}")
    print(f"  contracts: {len(contracts)}")
    print(f"  shipments: {len(ship)}")
    print(f"  inventory_snapshots: {len(inv)}")
    print(f"  production_batches: {len(prod)}")

if __name__ == "__main__":
    main()