from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path("data/transaction_data.csv")
OUT_DIR = Path("outputs")
N_SEGMENTS = 4
PROMO_SHARE = 0.5
MIN_WEEKS = 5
GROSS_MARGIN = 0.25
SEGMENT_NAMES = ["Low-Value", "Occasional", "Regular", "Loyal High-Value"]

def load_and_clean(path):
    df = pd.read_csv(path)
    for c in ["DAY", "QUANTITY", "SALES_VALUE", "RETAIL_DISC"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[(df["QUANTITY"] > 0) & (df["SALES_VALUE"] > 0)].copy()
    df["promo_line"] = df["RETAIL_DISC"].fillna(0) < 0
    df["disc_amount"] = -df["RETAIL_DISC"].fillna(0)
    df["promo_qty"] = np.where(df["promo_line"], df["QUANTITY"], 0)
    return df

def build_segments(df):
    max_day = df["DAY"].max()
    rfm = df.groupby("household_key").agg(
        recency=("DAY", lambda x: max_day - x.max()),
        frequency=("BASKET_ID", "nunique"),
        monetary=("SALES_VALUE", "sum"),
    ).reset_index()
    X = StandardScaler().fit_transform(np.log1p(rfm[["recency", "frequency", "monetary"]]))
    rfm["cluster"] = KMeans(n_clusters=N_SEGMENTS, random_state=42, n_init=10).fit_predict(X)
    order = rfm.groupby("cluster")["monetary"].mean().sort_values().index.tolist()
    name_map = {cluster: SEGMENT_NAMES[i] for i, cluster in enumerate(order)}
    rfm["segment"] = rfm["cluster"].map(name_map)
    profile = rfm.groupby("segment").agg(
        households=("household_key", "nunique"),
        avg_recency=("recency", "mean"),
        avg_baskets=("frequency", "mean"),
        avg_spend=("monetary", "mean"),
    ).reindex(SEGMENT_NAMES).reset_index()
    spend = rfm.groupby("segment")["monetary"].sum()
    profile["share_of_spend"] = profile["segment"].map(spend / spend.sum() * 100)
    return rfm, profile

def promotion_grid(df):
    pw = df.groupby(["PRODUCT_ID", "WEEK_NO"]).agg(
        units=("QUANTITY", "sum"),
        promo_units=("promo_qty", "sum"),
        sales=("SALES_VALUE", "sum"),
        discount=("disc_amount", "sum"),
    ).reset_index()
    pw["promoted"] = pw["promo_units"] / pw["units"] >= PROMO_SHARE
    counts = pw.groupby("PRODUCT_ID")["promoted"].agg(promoted_weeks="sum", total_weeks="count")
    counts["nonpromoted_weeks"] = counts["total_weeks"] - counts["promoted_weeks"]
    eligible = counts[(counts.promoted_weeks >= MIN_WEEKS) & (counts.nonpromoted_weeks >= MIN_WEEKS)].index
    return pw[pw.PRODUCT_ID.isin(eligible)].copy(), eligible

def uplift_for(frame, global_grid, eligible):
    local = frame.groupby(["PRODUCT_ID", "WEEK_NO"]).agg(
        units=("QUANTITY", "sum"), sales=("SALES_VALUE", "sum"), discount=("disc_amount", "sum")
    ).reset_index()
    base = global_grid[global_grid.PRODUCT_ID.isin(eligible)][["PRODUCT_ID", "WEEK_NO", "promoted"]]
    x = base.merge(local, on=["PRODUCT_ID", "WEEK_NO"], how="left").fillna({"units": 0, "sales": 0, "discount": 0})
    g = x.groupby(["PRODUCT_ID", "promoted"]).agg(
        mean_units=("units", "mean"), n=("units", "size"), sales=("sales", "sum"), discount=("discount", "sum")
    ).reset_index()
    p = g[g.promoted].set_index("PRODUCT_ID")
    n = g[~g.promoted].set_index("PRODUCT_ID")
    idx = p.index.intersection(n.index)
    p, n = p.loc[idx], n.loc[idx]
    uplift = p.mean_units.sum() / n.mean_units.sum() - 1
    incremental_units = p["n"] * (p.mean_units - n.mean_units)
    price = p.sales / (p["n"] * p.mean_units).replace(0, np.nan)
    incremental_sales = (incremental_units * price).replace([np.inf, -np.inf], np.nan).fillna(0).sum()
    discount_cost = p.discount.sum()
    net_return = incremental_sales * GROSS_MARGIN - discount_cost
    return {
        "products": len(idx),
        "uplift_pct": uplift * 100,
        "incremental_sales": incremental_sales,
        "discount_cost": discount_cost,
        "net_return_25pct_margin": net_return,
    }

def main():
    OUT_DIR.mkdir(exist_ok=True)
    df = load_and_clean(DATA_PATH)
    rfm, profile = build_segments(df)
    df = df.merge(rfm[["household_key", "segment"]], on="household_key", how="left")
    grid, eligible = promotion_grid(df)
    rows = [{"segment": "All customers", **uplift_for(df, grid, eligible)}]
    for segment in SEGMENT_NAMES:
        rows.append({"segment": segment, **uplift_for(df[df.segment == segment], grid, eligible)})
    results = pd.DataFrame(rows)
    profile.to_csv(OUT_DIR / "segment_profile.csv", index=False)
    results.to_csv(OUT_DIR / "promotion_results.csv", index=False)
    print(f"Clean transaction lines: {len(df):,}")
    print(f"Households: {df.household_key.nunique():,}")
    print(profile.to_string(index=False))
    print(results.to_string(index=False))

if __name__ == "__main__":
    main()
